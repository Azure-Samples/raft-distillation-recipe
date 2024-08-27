# Llama 3.1 405B distillation using UC Berkeley's RAFT recipe on Azure AI Serverless


<p align="center">
    <img src="./doc/gorilla-distillation.jpeg" width="75%" />
    <p align="center"><i>Generated using DALL-e 3 on Azure AI</i></p>
</p>

This repository is a recipe that will walk you through using [Meta Llama 3.1 405B](https://aka.ms/c/learn-deploy-llama) deployed on [Azure AI](https://aka.ms/c/learn-ai) to generate a synthetic dataset using [UC Berkeley's Gorilla](https://aka.ms/ucb-gorilla) project RAFT method (see [blog post](https://aka.ms/raft-blog)). The synthetically generated dataset will be used to finetune a selection of student models. Finally, we will deploy the fine-tuned model and evaluate its performance compared to a baseline model.

<table>
    <tr>
        <td><img src="./doc/microsoft-logo.png" style="max-height:100px; height: auto;"/></td>
        <td><img src="./doc/meta-logo.png" style="max-height:100px; height: auto;" /></td>
        <td><img src="./doc/ucb-logo.png" style="max-height:100px; height: auto;" /></td>
    </tr>
</table>

**Project Goal**: The primary objective of this project is to simplify and automate the process of distilling large language models. The workflows and notebooks are meant to be as hands-free as possible, ensuring that even complex tasks like generating synthetic datasets, fine-tuning models, and deploying them can be accomplished with minimal manual intervention. Whether you’re a beginner or an expert, our focus is on providing a seamless experience that allows you to focus on the results rather than the process.

## More about RAFT

- [Microsoft/Meta Blog post](https://aka.ms/raft-blog): RAFT:  A new way to teach LLMs to be better at RAG
- [Paper](https://aka.ms/raft-paper): RAFT: Adapting Language Model to Domain Specific RAG
- [UC Berkeley blog post](https://aka.ms/raft-blog-ucb): RAFT: Adapting Language Model to Domain Specific RAG
- [Meta blog post](https://aka.ms/raft-blog-meta): RAFT: Sailing Llama towards better domain-specific RAG
- [Gorilla project home](https://aka.ms/gorilla-home): Large Language Model Connected with Massive APIs
- [RAFT Github project](https://aka.ms/raft-repo)

## Getting started / Provisioning Azure AI infrastructure

The infrastructure for this project is fully provisioned using the Azure Developer CLI ([AZD](https://aka.ms/c/learn/azd)). AZD simplifies the deployment process by automating the setup of all required Azure resources, ensuring that you can get started with minimal configuration. This approach allows you to focus on the core aspects of model distillation and fine-tuning, while AZD handles the complexities of cloud resource management behind the scenes. By leveraging AZD, the project maintains a consistent and reproducible environment, making it easier to collaborate and scale.

The easiest is to open the project in Codespaces (or in VS Code Dev Container locally). It comes with azd included.

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/Azure-Samples/llama-raft-recipe)

Login using azd

```
azd auth login --use-device-code
```

Provision the infrastructure

```
azd up
```

The post provisioning [tests.sh](./infra/azd/hooks/tests.sh) script will run infra integration tests to make sure everything is deployed successfully.

Another post provisioning script, [export_env.sh](./infra/azd/hooks/export_env.sh) will export the environment variables for the provisioned infrastructure to the generated [./.env.state](./.env.state) file.

### Bring you own models

The easiest is to provision the infrastructure using azd but you can of course also bring your own models. Just provide environment variables for endpoints of your models in the [./.env](./.env) manual env file at the root of the project.

<details>
<summary>Environment variable configuration</summary>

Those environment variables are expected by RAFT cli scripts. They are suffixed by the purpose of the model `COMPLETION`, `EMBEDDING`, `BASELINE` followed by either standard **OpenAI** or **Azure OpenAI** variable names.

Choose for each model purpose either one of the following API styles:

<details>
<summary>OpenAI API</summary>

| Env var name                    | Explanation  |
| ------------------------------- | -----  |
| `COMPLETION_OPENAI_API_KEY`     | API Key for the teacher model  |
| `COMPLETION_OPENAI_BASE_URL`    | Base URL for the teacher model  |
| `COMPLETION_OPENAI_DEPLOYMENT`  | Deployment name for the teacher model  |
| `EMBEDDING_OPENAI_API_KEY`      | API Key for the embedding model  |
| `EMBEDDING_OPENAI_BASE_URL`     | Base URL for the embedding model  |
| `EMBEDDING_OPENAI_DEPLOYMENT`   | Deployment name for the embedding model  |
| `BASELINE_OPENAI_API_KEY`       | API Key for the baseline model  |
| `BASELINE_OPENAI_BASE_URL`      | Base URL for the baseline model  |
| `BASELINE_OPENAI_DEPLOYMENT`    | Deployment name for the baseline model  |

</details>

<details>
<summary>Azure OpenAI API</summary>

| Env var name                         | Explanation  |
| ------------------------------------ | -----  |
| `COMPLETION_AZURE_OPENAI_API_KEY`    | API Key for the teacher model  |
| `COMPLETION_AZURE_OPENAI_ENDPOINT`   | Endpoint for the teacher model  |
| `COMPLETION_AZURE_OPENAI_DEPLOYMENT` | Deployment name for the teacher model  |
| `COMPLETION_OPENAI_API_VERSION`      | API Version for the teacher model  |
| `EMBEDDING_AZURE_OPENAI_API_KEY`     | API Key for the embedding model  |
| `EMBEDDING_AZURE_OPENAI_ENDPOINT`    | Endpoint for the embedding model  |
| `EMBEDDING_AZURE_OPENAI_DEPLOYMENT`  | Deployment name for the embedding model  |
| `EMBEDDING_OPENAI_API_VERSION`       | API Version for the embedding model  |
| `BASELINE_AZURE_OPENAI_API_KEY`      | API Key for the baseline model  |
| `BASELINE_AZURE_OPENAI_ENDPOINT`     | Endpoint for the baseline model  |
| `BASELINE_AZURE_OPENAI_DEPLOYMENT`   | Deployment name for the baseline model  |
| `BASELINE_OPENAI_API_VERSION`        | API Version for the baseline model  |

</details>

</details>

## Notebooks

This repository is organized in 4 notebooks, one for each step of the process:

| Notebook      | Explanation      |
| ------------- | ---------------- |
| [1_gen.ipynb](./1_gen.ipynb) | Generate a finetuning dataset using RAFT |
| [2_finetune.ipynb](./2_finetune.ipynb) | Fine tune a base model using the generated dataset |
| [3_deploy.ipynb](./3_deploy.ipynb) | Deploy the fine tuned model |
| [4_eval.ipynb](./4_eval.ipynb) | Evaluate the fine tuned model |

## Run time and costs

**Warning**: The times and costs mentioned bellow are indications to give you a sense of what to expect but can vary dramatically depending on your experience, please monitor your usage to avoid surprises.

| Notebook      | Run time      | Cost      |
| ------------- | ---------------- | ---------------- |
| [1_gen.ipynb](./1_gen.ipynb) | From 5 minutes for the sample to multiple days for bigger domains | From $1 for the sample to $50 or more for bigger domains  |
| [2_finetune.ipynb](./2_finetune.ipynb) | Roughly 1.5 hours | Roughly $50 |
| [3_deploy.ipynb](./3_deploy.ipynb) | < 10 minutes | < $1 |
| [4_eval.ipynb](./4_eval.ipynb) | From 5 minutes for the sample to multiple days for bigger domains | From $1 for the sample to $50 or more for bigger domains |

## Dormant infrastructure costs

While not used, the infrastructure of this project won't cost much but will still cost a bit.

**TODO**: provide costs estimations for dormant infra

## Configuration files

| File      | Explanation      |
| ------------- | ---------------- |
| [.env](./.env) | User provided environment variables read by notebooks and scripts |
| [.env.state](./.env.state) | Environment variables for resources created during notebooks execution and shared by all notebooks |
| [config.json](./config.json) | Configuration necessary to connect to the Azure AI Studio Hub (same as Azure ML Workspace) |

## Parameterized execution

In addition to executing notebooks interactively, the notebooks also support parameterized command line execution using [papermill](https://papermill.readthedocs.io/).

### Parameter files

The parameter files are contained in folder [parameters](./parameters/) and support the following configurations:

| Parameter file     | Model      | Format      |
| ------------- | ---------------- | ---------------- |
| [Llama-2-7b.yaml](./parameters/Llama-2-7b.yaml)   | Llama-2-7b | Completion |
| [Meta-Llama-3-8B-Instruct.yaml](./parameters/Meta-Llama-3-8B-Instruct.yaml)   | Meta-Llama-3-8B-Instruct | Chat |
| [Meta-Llama-3.1-8B-Instruct.yaml](./parameters/Meta-Llama-3.1-8B-Instruct.yaml)   | Meta-Llama-3.1-8B-Instruct | Chat |

### Running notebooks from the command line with a parameter file

Notebooks can be run all at once with a given parameter file using the following command:

```
./run_all.sh -p ./parameters/Meta-Llama-3.1-8B-Instruct.yaml
```

## Taking down the infrastructure

After you are done working with the project, you can take down the infrastructure with the following command.

**IMPORTANT**: Please be aware that this will **DELETE** everything related to this project including **generated datasets** and **fine-tuned models**.

**IMPORTANT**: Save everything important to you before running this command.

```
azd down --purge
```

**Note**: The `--purge` parameter is important to reclaim quotas, for example for Azure OpenAI embedding models.
