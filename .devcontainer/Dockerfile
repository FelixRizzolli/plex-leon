FROM mcr.microsoft.com/devcontainers/python:3.14

# Use bash as the shell for RUN commands
SHELL ["/bin/bash", "-lc"]

RUN <<BASH
set -euo pipefail

echo "INSTALL PLEX-LEON IMAGE"

# Configure Bash
#  --> Disable Bash's bracket paste mode
echo "bind 'set enable-bracket-paste off'" >> ~/.bashrc
#  --> Always show hidden files in ls and colorize the output
echo "alias ls='ls -a --color=auto'" >> ~/.bashrc

# Configure Git
#  --> Ensure that git treats /workspace as a safe directory to avoid permission-related issues.
git config --global --add safe.directory /workspace

# Install GitHub CLI
sudo apt-get update
sudo apt-get install gh -y

# Install poetry
curl -sSL https://install.python-poetry.org | python3 -

# Install ffmpeg & mediainfo
sudo apt-get update -y
sudo apt-get install -y ffmpeg
sudo apt-get install -y mediainfo
BASH