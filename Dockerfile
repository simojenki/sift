FROM mcr.microsoft.com/devcontainers/python:3.12

ARG LAZYGIT_VERSION=0.61.1
ARG ZELLIJ_VERSION=0.44.0
ARG TARGETARCH

# Claude Code via official Anthropic apt repo
RUN curl -fsSL https://downloads.claude.ai/keys/claude-code.asc \
        | gpg --dearmor --yes -o /usr/share/keyrings/claude-code.gpg \
    && printf '%s\n' \
        'Types: deb' \
        'URIs: https://downloads.claude.ai/claude-code/apt/stable' \
        'Suites: stable' \
        'Components: main' \
        "Architectures: $(dpkg --print-architecture)" \
        'Signed-By: /usr/share/keyrings/claude-code.gpg' \
        > /etc/apt/sources.list.d/claude-code.sources \
    && apt-get update \
    && apt-get install -y claude-code

# lazygit
RUN ARCH=$([ "$TARGETARCH" = "arm64" ] && echo "arm64" || echo "x86_64") \
    && curl -Lo /tmp/lazygit.tar.gz \
    "https://github.com/jesseduffield/lazygit/releases/download/v${LAZYGIT_VERSION}/lazygit_${LAZYGIT_VERSION}_Linux_${ARCH}.tar.gz" \
    && tar -xf /tmp/lazygit.tar.gz -C /usr/local/bin lazygit \
    && rm /tmp/lazygit.tar.gz

# zellij
RUN ARCH=$([ "$TARGETARCH" = "arm64" ] && echo "aarch64" || echo "x86_64") \
    && curl -Lo /tmp/zellij.tar.gz \
    "https://github.com/zellij-org/zellij/releases/download/v${ZELLIJ_VERSION}/zellij-${ARCH}-unknown-linux-musl.tar.gz" \
    && tar -xf /tmp/zellij.tar.gz -C /usr/local/bin zellij \
    && rm /tmp/zellij.tar.gz

# ruff
RUN pip install --no-cache-dir ruff

USER vscode
WORKDIR /workspace