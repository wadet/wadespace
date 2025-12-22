#!/bin/bash

# Wade Space - Graphical UI Launcher
# Activates virtual environment and runs the Pygame UI

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found at ./venv"
    echo "Please run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
echo "🚀 Starting Wade Space (Graphical Mode)..."
source venv/bin/activate

# Check if pygame is installed
if ! python -c "import pygame" 2>/dev/null; then
    echo "❌ Pygame not installed"
    echo "Installing pygame..."
    pip install pygame
fi

# Run the UI
python -m src.ui_main

# Deactivate on exit
deactivate
