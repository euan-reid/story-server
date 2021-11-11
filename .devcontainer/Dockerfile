# See here for image contents: https://github.com/microsoft/vscode-dev-containers/tree/v0.205.2/containers/python-3/.devcontainer/base.Dockerfile

# [Choice] Python version (use -bullseye variants on local arm64/Apple Silicon): 3, 3.10, 3.9, 3.8,
# 3.7, 3.6, 3-bullseye, 3.10-bullseye, 3.9-bullseye, 3.8-bullseye, 3.7-bullseye, 3.6-bullseye,
# 3-buster, 3.10-buster, 3.9-buster, 3.8-buster, 3.7-buster, 3.6-buster
ARG VARIANT="3.10-bullseye"
FROM mcr.microsoft.com/vscode/devcontainers/python:0-${VARIANT}

# Install gcloud cli and Datastore Emulator
RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" \
    | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
RUN export DEBIAN_FRONTEND=noninteractive \
    && sudo apt-get update \
    && sudo apt-get install -y \
        apt-transport-https \
        ca-certificates \
        gnupg
RUN curl https://packages.cloud.google.com/apt/doc/apt-key.gpg \
    | sudo apt-key --keyring /usr/share/keyrings/cloud.google.gpg add -
RUN export DEBIAN_FRONTEND=noninteractive \
    && sudo apt-get update \
    && sudo apt-get install -y --no-install-recommends \
        google-cloud-sdk \
        google-cloud-sdk-datastore-emulator
