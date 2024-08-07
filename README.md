# Llama 3.1 405B distillation using UC Berkeley's RAFT recipe on Azure AI Serverless

This repository is a recipe that will walk you through using [Meta Llama 3.1 405B](https://aka.ms/c/learn-deploy-llama) deployed on [Azure AI](https://aka.ms/c/learn-ai) to generate a synthetic dataset using [UC Berkeley's Gorilla](https://aka.ms/ucb-gorilla) project RAFT method (see [blog post](https://aka.ms/raft-blog)). The synthetically generated dataset will be used to finetune a selection of student models. Finally, we will evaluate the performance of the fine tuned model and compare it to the baseline model.

This repository is organized in 4 notebooks, one for each step of the process:

| Notebook      | Explanation      |
| ------------- | ---------------- |
| [0_gen.ipynb](./0_gen.ipynb) (**Start here**) | Generate a finetuning dataset using RAFT |
| [1_finetune.ipynb](./1_finetune.ipynb) | Fine tune a base model using the generated dataset |
| [2_deploy.ipynb](./2_deploy.ipynb) | Deploy the fine tuned model |
| [3_eval.ipynb](./3_eval.ipynb) | Evaluate the fine tuned model |

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/cedricvidal/llama-raft-recipe)

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

![Gorilla Student](./doc/student-gorilla.jpeg "Student Gorilla")
