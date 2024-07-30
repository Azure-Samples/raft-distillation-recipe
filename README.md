# RAFT Notebooks

## Endpoints needed

### Gen notebook

| Use | Models | Env vars |
| --- | --- | --- |
| Dataset generation completion model | Llama 2 70B, Llama 3 80B, Llama 3.1 405B | `COMPLETION_OPENAI_BASE_URL`<br>`COMPLETION_OPENAI_API_KEY` |
| Dataset generation embedding model | ADA 002 | `EMBEDDING_AZURE_OPENAI_ENDPOINT`<br>`EMBEDDING_AZURE_OPENAI_API_KEY`<br>`EMBEDDING_OPENAI_API_VERSION` |

### Eval notebook

| Use | Models | Env vars |
| --- | --- | --- |
| Scoring | GPT 4 Turbo | `SCORE_AZURE_OPENAI_ENDPOINT`<br>`SCORE_AZURE_OPENAI_API_KEY`<br>`SCORE_OPENAI_API_VERSION`<br>`SCORE_AZURE_OPENAI_DEPLOYMENT` |
