FROM mcr.microsoft.com/devcontainers/python:1-3.12-bullseye
COPY .devcontainer/post-create.sh .
COPY requirements.txt .
RUN sh ./post-create.sh
