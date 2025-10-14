#!/bin/bash
# Snake of Despair - Unix Launcher
# This script provides an easy way to run the game on Unix-like systems

echo "Starting Snake of Despair..."
echo

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "Error: Python is not installed or not in PATH"
        echo "Please install Python 3.11 or 3.12"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

# Check Python version
PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
REQUIRED_VERSION="3.11"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "Error: Python $REQUIRED_VERSION or higher is required"
    echo "Current version: $PYTHON_VERSION"
    exit 1
fi

# Check if requirements are installed
if ! $PYTHON_CMD -c "import pygame" &> /dev/null; then
    echo "Installing required packages..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "Error: Failed to install requirements"
        exit 1
    fi
fi

# Make the script executable
chmod +x "$0"

# Run the game
echo "Launching Snake of Despair..."
$PYTHON_CMD -m snake_of_despair "$@"

# Check exit code
if [ $? -ne 0 ]; then
    echo
    echo "Game exited with error code $?"
    read -p "Press Enter to continue..."
fi
