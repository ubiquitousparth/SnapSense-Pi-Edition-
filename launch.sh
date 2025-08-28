#!/bin/bash

# This script ensures the SnapSense application is launched correctly
# by activating its virtual environment first.

# Get the absolute path of the directory where this script is located
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)

# Path to the virtual environment
VENV_PATH="$SCRIPT_DIR/venv/bin/activate"

# Path to the main Python script
APP_PATH="$SCRIPT_DIR/src/main.py"

# Check if the virtual environment exists
if [ ! -f "$VENV_PATH" ]; then
    echo "Error: Virtual environment not found at $VENV_PATH"
    echo "Please run the installation steps first."
    exit 1
fi

# Activate the virtual environment and run the application
source "$VENV_PATH"
python3 "$APP_PATH"
