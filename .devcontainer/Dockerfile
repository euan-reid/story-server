# See here for image contents: https://github.com/microsoft/vscode-dev-containers/tree/v0.205.2/containers/python-3/.devcontainer/base.Dockerfile

# [Choice] Python version (use -bullseye variants on local arm64/Apple Silicon): 3, 3.10, 3.9, 3.8,
# 3.7, 3.6, 3-bullseye, 3.10-bullseye, 3.9-bullseye, 3.8-bullseye, 3.7-bullseye, 3.6-bullseye,
# 3-buster, 3.10-buster, 3.9-buster, 3.8-buster, 3.7-buster, 3.6-buster
ARG VARIANT="3.10-bullseye"
FROM mcr.microsoft.com/vscode/devcontainers/python:0-${VARIANT}

# Install additional source requirements
RUN DEBIAN_FRONTEND=noninteractive apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        apt-transport-https \
        ca-certificates \
        gnupg

# Add gcloud sources.list.d
RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" \
    | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list

# Add gcloud GPG key to keyrings
RUN mkdir /root/.gnupg
RUN curl -fsSL https://packages.cloud.google.com/apt/doc/apt-key.gpg \
    | gpg --dearmor \
    | tee /usr/share/keyrings/cloud.google.gpg

# Update apt with additional sources
RUN DEBIAN_FRONTEND=noninteractive apt-get update

# Install gcloud CLI for GCP auth and Datastore emulator
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    google-cloud-sdk \
    google-cloud-sdk-datastore-emulator
