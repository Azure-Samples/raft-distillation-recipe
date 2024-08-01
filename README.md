# Llama 3.1 405B distillation using UC Berkeley's RAFT recipe

This repository is a recipe that will walk you through using Meta Llama 3.1 405B deployed on Azure AI to generate a synthetic dataset using UC Berkeley's Gorilla project RAFT method (see [blog post](https://aka.ms/raft-blog)). The synthetically generated dataset will be used to finetune a Llama 3.1 8B model. Finally, we will evaluate the performance of the fine tuned model and compare it to the baseline model.

Start with the [gen](./gen.ipynb) notebook.

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/cedricvidal/llama-raft-recipe)

![Gorilla Student](./doc/student-gorilla.jpeg "Student Gorilla")
