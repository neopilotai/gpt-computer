#!/bin/bash
set -e

echo "====================SEARXNG SETUP START===================="

# Install dependencies for building SearXNG
apt-get update && apt-get install -y --no-install-recommends 
    git build-essential libxslt-dev zlib1g-dev libffi-dev libssl-dev

# Add searxng system user
useradd --shell /bin/bash --system 
    --home-dir "/usr/local/searxng" 
    searxng

# Add to sudo group (optional for search engine user, but preserved from legacy)
usermod -aG sudo searxng

mkdir -p /usr/local/searxng
cd /usr/local/searxng

# Clone SearXNG
git clone "https://github.com/searxng/searxng" "searxng-src"

# Use the pre-existing venv created in setup-python.sh
source /opt/venv-searxng/bin/activate

# Install into venv
cd searxng-src
pip install --no-cache-dir --use-pep517 --no-build-isolation .

# Correct permissions
chown -R searxng:searxng /usr/local/searxng
chown -R searxng:searxng /opt/venv-searxng

# Clean up build artifacts
apt-get clean && rm -rf /var/lib/apt/lists/*

echo "====================SEARXNG SETUP END===================="
