FROM mcr.microsoft.com/devcontainers/base:ubuntu-24.04

# Create mount targets before Docker mounts the named volumes. Otherwise Docker
# can create their parent directories as root, preventing VS Code from starting.
RUN mkdir -p /home/vscode/.bash-history \
        /home/vscode/.vscode-server/data/User \
        /home/vscode/.vscode-server/data/agentSessionData \
        /home/vscode/.copilot/chats \
        /home/vscode/.copilot/session-state \
        /home/vscode/.config/gh \
        /home/vscode/.ssh \
    && chown -R vscode:vscode /home/vscode/.bash-history \
        /home/vscode/.vscode-server /home/vscode/.copilot \
        /home/vscode/.config /home/vscode/.ssh \
    && chmod 700 /home/vscode/.config/gh /home/vscode/.ssh

RUN printf '\nshopt -s histappend\nPROMPT_COMMAND="history -a${PROMPT_COMMAND:+; $PROMPT_COMMAND}"\n' \
    >> /home/vscode/.bashrc

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        ca-certificates \
        git \
        jq \
        latexmk \
        make \
        poppler-utils \
        python3 \
        shellcheck \
        texlive-binaries \
        texlive-extra-utils \
        texlive-fonts-recommended \
        texlive-latex-base \
        texlive-latex-extra \
        texlive-luatex \
        texlive-xetex \
    && rm -rf /var/lib/apt/lists/*
