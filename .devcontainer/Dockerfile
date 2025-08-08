# Use an official Python 3.12 slim image as a base (better compatibility)
FROM python:3.12-slim

# Install additional dependencies
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    curl \
    sudo \
    && apt-get clean

# Create a workspace directory
WORKDIR /workspace

# Install Node.js 22.x
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash -
RUN apt-get install -y nodejs
RUN node -v && npm -v

# Install Claude Code globally
RUN npm install -g @anthropic-ai/claude-code

# Install devcontainer CLI
RUN npm install -g @devcontainers/cli

# Add a default user for VS Code
RUN useradd -ms /bin/bash vscode

# Configure sudo for vscode user
RUN echo "vscode ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Set the working directory
WORKDIR /workspace

# Install commonly used Python tools
RUN pip install --upgrade pip setuptools wheel

# (Optional) Pre-install dependencies
RUN pip install ipykernel jupyter

# Create .claude directory and set ownership for vscode user
RUN mkdir -p /workspaces/climate-utils/.claude && chown vscode:vscode /workspaces/climate-utils/.claude

# Switch to vscode user
USER vscode

# Install requirements as vscode user
COPY requirements.txt .
RUN pip install -r requirements.txt

# Add useful bash aliases
RUN echo 'alias ll="ls -la"' >> ~/.bashrc && \
    echo 'alias la="ls -A"' >> ~/.bashrc && \
    echo 'alias l="ls -CF"' >> ~/.bashrc && \
    echo 'alias ..="cd .."' >> ~/.bashrc && \
    echo 'alias ...="cd ../.."' >> ~/.bashrc && \
    echo 'alias ....="cd ../../.."' >> ~/.bashrc && \
    echo 'alias grep="grep --color=auto"' >> ~/.bashrc && \
    echo 'alias fgrep="fgrep --color=auto"' >> ~/.bashrc && \
    echo 'alias egrep="egrep --color=auto"' >> ~/.bashrc && \
    echo 'alias h="history"' >> ~/.bashrc && \
    echo 'alias j="jobs -l"' >> ~/.bashrc && \
    echo 'alias vi="vim"' >> ~/.bashrc && \
    echo 'alias svi="sudo vim"' >> ~/.bashrc && \
    echo 'alias vis="vim \"\$@\""' >> ~/.bashrc && \
    echo 'alias ports="netstat -tulanp"' >> ~/.bashrc