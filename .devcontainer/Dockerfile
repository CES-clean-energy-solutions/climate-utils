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
    && apt-get clean

# Create a workspace directory
WORKDIR /workspace

# Install Node.js 22.x
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash -
RUN apt-get install -y nodejs
RUN node -v && npm -v

# Add a default user for VS Code
RUN useradd -ms /bin/bash vscode
USER vscode

# Set the working directory
WORKDIR /workspace

# Install commonly used Python tools
# RUN pip install --upgrade pip setuptools wheel

# Install dependencies from requirements.txt
COPY requirements.txt .
RUN pip install -r requirements.txt

# Install climatevis package from GitHub
# RUN pip install git+https://github.com/CES-clean-energy-solutions/climatevis.git