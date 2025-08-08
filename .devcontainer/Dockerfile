FROM mcr.microsoft.com/devcontainers/python:3.13

# Set bash as the default shell
ENV SHELL=/bin/bash 

RUN echo "INSTALL PLEX LEON IMAGE" && \
    # Disable Bash's bracket paste mode
    echo "bind 'set enable-bracket-paste off'" >> ~/.bashrc && \
    # Always show hidden files in ls and colorize the output
    echo "alias ls='ls -a --color=auto'" >> ~/.bashrc && \
    # Ensure that git treats /workspace as a safe directory to avoid permission-related issues.
    git config --global --add safe.directory /workspace && \
    # Install GitHub CLI
    apt-get update && \
    apt-get install gh -y && \
    # Install poetry
    curl -sSL https://install.python-poetry.org | python3 -
