# Llama 3.1 405B distillation using UC Berkeley's RAFT recipe on Azure AI Serverless

This repository is a recipe that will walk you through using [Meta Llama 3.1 405B](https://aka.ms/c/learn-deploy-llama) deployed on [Azure AI](https://aka.ms/c/learn-ai) to generate a synthetic dataset using [UC Berkeley's Gorilla](https://aka.ms/ucb-gorilla) project RAFT method (see [blog post](https://aka.ms/raft-blog)). The synthetically generated dataset will be used to finetune a Llama 3.1 8B model. Finally, we will evaluate the performance of the fine tuned model and compare it to the baseline model.

This repository is organized in 4 notebooks, one for each step of the process:

| Notebook      | Explanation      |
| ------------- | ---------------- |
| [0_gen.ipynb](./0_gen.ipynb) (**Start here**) | Generate a finetuning dataset using RAFT |
| [1_finetune.ipynb](./1_finetune.ipynb) | Fine tune a base model using the generated dataset |
| [2_deploy.ipynb](./2_deploy.ipynb) | Deploy the fine tuned model |
| [3_eval.ipynb](./3_eval.ipynb) | Evaluate the fine tuned model |

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/cedricvidal/llama-raft-recipe)

![Gorilla Student](./doc/student-gorilla.jpeg "Student Gorilla")
