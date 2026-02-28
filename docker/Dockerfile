# Stage 1: Base - Kali Linux with core packages, Python, and SearXNG
FROM kalilinux/kali-rolling AS base

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US:en
ENV LC_ALL=en_US.UTF-8
ENV TZ=UTC

# Copy setup scripts
COPY docker/common/scripts/ /setup/

# Run base installation
RUN bash /setup/setup-base.sh && \
    bash /setup/setup-python.sh && \
    bash /setup/setup-searxng.sh

# Stage 2: CLI - Minimal image for gpt-computer command
FROM base AS cli

WORKDIR /app
COPY . .

# Install gpt-computer using uv into the gptc venv
RUN /opt/venv-gptc/bin/uv pip install -e .

# Link the binary to a global location
RUN ln -s /opt/venv-gptc/bin/gpt-computer /usr/local/bin/gpt-computer && \
    ln -s /opt/venv-gptc/bin/gptc /usr/local/bin/gptc

COPY docker/entrypoint.sh /app/entrypoint.sh
ENTRYPOINT ["bash", "/app/entrypoint.sh"]

# Stage 3: Full Runtime - For specialized environments (SearXNG, VNC, etc.)
FROM cli AS full-runtime

# Copy configurations and execution scripts
COPY docker/common/etc/searxng/ /etc/searxng/
COPY docker/run/fs/etc/supervisor/ /etc/supervisor/
COPY docker/run/fs/exe/ /exe/

# Expose ports
EXPOSE 22 80 8888 9000-9009

# Entrypoint for runtime is the initialize script
CMD ["/exe/initialize.sh", "main"]
