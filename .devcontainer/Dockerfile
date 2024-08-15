FROM mcr.microsoft.com/devcontainers/python:1-3.12-bullseye
COPY requirements.txt .

RUN echo "Utilities to display PDFs in notebooks" && \
    sudo apt update && \
    sudo apt install -y libmagickwand-dev && \
    sudo sed -i /PDF/d /etc/ImageMagick-6/policy.xml

RUN echo "Installing requirements" && \
    pip install -r requirements.txt
