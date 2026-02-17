#!/bin/bash

# Define virtual environment directory
VENV_DIR=".venv"

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 1. Create Virtual Environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment in $VENV_DIR..."
    if command_exists uv; then
        uv venv "$VENV_DIR"
    else
        python3 -m venv "$VENV_DIR"
    fi
fi

# 2. Activate Virtual Environment
source "$VENV_DIR/bin/activate"

# 3. Install Dependencies
if [ -f "requirements.txt" ]; then
    echo "Installing/Updating dependencies from requirements.txt..."
    if command_exists uv; then
        # uv is faster
        uv pip install -r requirements.txt
    else
        # Standard pip fallback
        pip install -r requirements.txt
    fi
else
    echo "Warning: requirements.txt not found."
fi

# 4. Run Application
echo "Starting PromptShell..."
python main.py
