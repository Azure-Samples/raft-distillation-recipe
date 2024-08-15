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

## More about RAFT

- [Microsoft/Meta Blog post](https://aka.ms/raft-blog): RAFT:  A new way to teach LLMs to be better at RAG
- [Paper](https://aka.ms/raft-paper): RAFT: Adapting Language Model to Domain Specific RAG
- [UC Berkeley blog post](https://aka.ms/raft-blog-ucb): RAFT: Adapting Language Model to Domain Specific RAG
- [Meta blog post](https://aka.ms/raft-blog-meta): RAFT: Sailing Llama towards better domain-specific RAG
- [Gorilla project home](https://aka.ms/gorilla-home): Large Language Model Connected with Massive APIs
- [RAFT Github project](https://aka.ms/raft-repo)

## Notebooks

This repository is organized in 4 notebooks, one for each step of the process:

| Notebook      | Explanation      |
| ------------- | ---------------- |
| [0_workspace.ipynb](./0_workspace.ipynb) (**Start here**) | Configure or provisions an Azure AI Studio Hub (same as an Azure ML Workspace) |
| [1_gen.ipynb](./1_gen.ipynb) | Generate a finetuning dataset using RAFT |
| [2_finetune.ipynb](./2_finetune.ipynb) | Fine tune a base model using the generated dataset |
| [3_deploy.ipynb](./3_deploy.ipynb) | Deploy the fine tuned model |
| [4_eval.ipynb](./4_eval.ipynb) | Evaluate the fine tuned model |

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/Azure-Samples/llama-raft-recipe)

## Run time and cost

**Warning**: The times and costs mentioned bellow are indications to give you a sense of what to expect but can vary dramatically depending on your experience, please monitor your usage to avoid surprises.

| Notebook      | Run time      | Cost      |
| ------------- | ---------------- | ---------------- |
| [0_workspace.ipynb](./0_workspace.ipynb) | A few minutes | A few cents |
| [1_gen.ipynb](./1_gen.ipynb) | From 5 minutes for the sample to multiple days for bigger domains | From $1 for the sample to $50 or more for bigger domains  |
| [2_finetune.ipynb](./2_finetune.ipynb) | Roughly 1.5 hours | Roughly $50 |
| [3_deploy.ipynb](./3_deploy.ipynb) | < 10 minutes | < $1 |
| [4_eval.ipynb](./4_eval.ipynb) | From 5 minutes for the sample to multiple days for bigger domains | From $1 for the sample to $50 or more for bigger domains |

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
./run_all.sh -p ./parameters/Llama-2-7b.yaml
```
