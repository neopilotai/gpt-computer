#!/bin/bash
set -e

echo "====================PYTHON SETUP START===================="
# Install Python and build dependencies
apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-venv python3-pip \
    build-essential libssl-dev zlib1g-dev libbz2-dev \
    libreadline-dev libsqlite3-dev wget curl llvm \
    libncursesw5-dev xz-utils tk-dev libxml2-dev \
    libxmlsec1-dev libffi-dev liblzma-dev

# Install uv globally
curl -LsSf https://astral.sh/uv/install.sh | sh
mv /root/.local/bin/uv /usr/local/bin/uv

# Setup gpt-computer environment (let uv handle the python version)
uv venv /opt/venv-gptc --python 3.12
source /opt/venv-gptc/bin/activate

# Install common ML dependencies
uv pip install \
    torch==2.4.0 \
    torchvision==0.19.0 \
    --index-url https://download.pytorch.org/whl/cpu

# Setup SearXNG environment
uv venv /opt/venv-searxng --python 3.12


# Cleanup
apt-get clean && rm -rf /var/lib/apt/lists/*

echo "====================PYTHON SETUP END===================="
