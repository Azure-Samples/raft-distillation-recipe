import os
import json
from datetime import datetime
from promptflow.core import AzureOpenAIModelConfiguration
from promptflow.evals.evaluators import RelevanceEvaluator, GroundednessEvaluator, FluencyEvaluator, CoherenceEvaluator, SimilarityEvaluator
from promptflow.evals.evaluate import evaluate
from dotenv import load_dotenv
import argparse
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
from logconf import log_setup
from tenacity import retry, wait_exponential, retry_if_exception_type
from openai import RateLimitError
from client_utils import build_openai_client
from openai import OpenAI

logger = logging.getLogger("pfeval")

load_dotenv()

def get_args() -> argparse.Namespace:
    """
    Parses and returns the arguments specified by the user's command
    """
    parser = argparse.ArgumentParser()

    parser.add_argument("--input", type=str, default="input.jsonl", help="The input data JSONL file to load")
    parser.add_argument("--output", type=str, default="output.jsonl", help="The output data JSONL file to export to")
    parser.add_argument("--mode", type=str, default="local", help="local or remote")
    parser.add_argument("--workers", type=int, default="2", help="Number of worker threads in local mode")

    args = parser.parse_args()
    return args

base_url=os.environ["EVAL_OPENAI_BASE_URL"]
api_key=os.environ["EVAL_OPENAI_API_KEY"]
api_version=os.environ["EVAL_OPENAI_DEPLOYMENT"]

print(f"base_url={base_url}")
print(f"api_key={api_key}")
print(f"api_version={api_version}")

client = build_openai_client("EVAL")
#client = OpenAI(
#    base_url=os.environ["EVAL_OPENAI_BASE_URL"],
#    api_key=os.environ["EVAL_OPENAI_API_KEY"],
#)

def get_answer(context, question):
    response = client.completions.create(
        model="Llama-2-7b-raft-bats-18k-unrrr",
        prompt=format_prompt(context, question),
        temperature=0.2,
        max_tokens=1024,
        stop='<STOP>'
    )
    answer = response.choices[0].text
    return {"answer": answer}

def format_prompt(context, question):
    return f"{context}\n{question}"

def evaluate_aistudio(model_config, project_scope, project_scope_report, data_path):
    # create unique id for each run with date and time
    time_str = datetime.now().strftime("%Y%m%d%H%M%S")
    run_id = f"chat_evaluation_sdk_{time_str}"
    print(run_id)

    result = evaluate(
        evaluation_name=run_id,
        data=data_path,
        #target=get_answer,
        azure_ai_project=project_scope_report,
        evaluators={
            "similarity": SimilarityEvaluator(model_config),
            "groundedness": GroundednessEvaluator(project_scope=project_scope),
        },
        evaluator_config={
            "defaults": {
                "question": "${data.question}",
                "answer": "${target.answer}",
                "ground_truth": "${data.gold_final_answer}",
                "context": "${data.context}",
            },
        },
    )
    print(f"studio_url=f{result['studio_url']}")
    return result

def evaluate_local(model_config, project_scope, project_scope_report, data_path, workers=2):
    data = []
    with open(data_path) as f:
        for line in f:
            data.append(json.loads(line))

    evaluators = [
#        RelevanceEvaluator(model_config),
#        FluencyEvaluator(model_config),
#        CoherenceEvaluator(model_config),
        GroundednessEvaluator(model_config),
        SimilarityEvaluator(model_config),
    ]

    @retry(wait=wait_exponential(multiplier=1, min=10, max=120), reraise=True, retry=retry_if_exception_type(RateLimitError))
    def evaluate_row_with(row, evaluator):
        result = evaluator(
            question=row['question'],
            answer=row['final_answer'],
            context=row['context'],
            ground_truth=row['gold_final_answer']
        )
        return result

    def evaluate_row(row, pbar):
        for evaluator in evaluators:
            try:
                result = evaluate_row_with(row, evaluator)
            except Exception as e:
                result = {
                    "error": str(e)
                }
            row.update(result)
            pbar.update(1)
        return row

    results = []
    futures = []
    with tqdm(total=len(data) * len(evaluators)) as pbar:
        with ThreadPoolExecutor(max_workers=workers) as executor:
            for row in data:
                futures.append(executor.submit(evaluate_row, row, pbar))
            for future in as_completed(futures):
                results.append(future.result())

    return results

if __name__ == "__main__":
    import time
    import jsonlines

    log_setup()
    args = get_args()

    # Initialize Azure OpenAI Connection
    logger.info("Loading model configuration")

    # Model config
    azure_endpoint = os.environ["SCORE_AZURE_OPENAI_ENDPOINT"]
    api_key = os.environ["SCORE_AZURE_OPENAI_API_KEY"]
    api_version = os.environ["SCORE_OPENAI_API_VERSION"]
    deployment = os.environ["SCORE_AZURE_OPENAI_DEPLOYMENT"]

    logger.info(f"deployment={deployment}")
    logger.info(f"api_version={api_version}")
    logger.info(f"azure_endpoint={azure_endpoint}")

    # Project Scope
    subscription_id=os.environ["GROUNDEDNESS_SUB_ID"]
    resource_group_name=os.environ["GROUNDEDNESS_GROUP"]
    project_name=os.environ["GROUNDEDNESS_PROJECT_NAME"]

    logger.info(f"subscription_id={subscription_id}")
    logger.info(f"resource_group_name={resource_group_name}")
    logger.info(f"project_name={project_name}")

    model_config = AzureOpenAIModelConfiguration(
            azure_deployment=deployment,
            api_key=api_key,
            api_version=api_version,
            azure_endpoint=azure_endpoint
        )

    project_scope = {
        "subscription_id": subscription_id,
        "resource_group_name": resource_group_name,
        "project_name": project_name,
    }

    subscription_id = os.environ["REPORT_SUB_ID"]
    resource_group_name = os.environ["REPORT_GROUP"]
    project_name = os.environ["REPORT_PROJECT_NAME"]

    print(f"report subscription_id={subscription_id}")
    print(f"report resource_group_name={resource_group_name}")
    print(f"report project_name={project_name}")

    project_scope_report = {
        "subscription_id": subscription_id,
        "resource_group_name": resource_group_name,
        "project_name": project_name,
    }

    start=time.time()
    logger.info(f"Starting evaluate...")

    modes = {"local": evaluate_local, "remote": evaluate_aistudio}
    evaluate_func = modes[args.mode]
    logger.info(f"Evaluating {args.input} with mode {args.mode}")
    logger.info(f"Output file will be saved to {args.output}")
    eval_result = evaluate_func(model_config=model_config, data_path=args.input, project_scope=project_scope, project_scope_report=project_scope_report, workers=args.workers)

    end=time.time()
    logger.info(f"Finished evaluate in {end - start}s")
    logger.info(f"Writing {len(eval_result)} results to {args.output}")

    #save evaluation results to a JSONL file
    if args.mode == "local":
        with jsonlines.open(args.output, 'w') as writer:
            writer.write_all(eval_result)
