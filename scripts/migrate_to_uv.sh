#!/bin/bash
# Migration Script for Sik Sort - Switch from pip to UV
# This script helps existing users migrate from pip to UV

set -e

echo "=================================="
echo "Sik Sort - Migration to UV"
echo "=================================="
echo ""

# Check if UV is installed
echo "Checking for UV installation..."
if ! command -v uv &> /dev/null; then
    echo "UV is not installed. Installing UV..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    
    # Source the UV environment
    export PATH="$HOME/.cargo/bin:$PATH"
    
    if ! command -v uv &> /dev/null; then
        echo "Failed to install UV. Please install manually:"
        echo "curl -LsSf https://astral.sh/uv/install.sh | sh"
        exit 1
    fi
    
    echo "UV installed successfully!"
else
    echo "UV is already installed."
fi

echo ""

# Check if in virtual environment
if [ -n "$VIRTUAL_ENV" ]; then
    echo "You are currently in a virtual environment."
    echo "Please deactivate it first by running: deactivate"
    exit 1
fi

# Check if .venv exists
if [ -d ".venv" ]; then
    echo "Found existing .venv directory."
    read -p "Do you want to remove it and create a new one with UV? (y/n) " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Removing old .venv..."
        rm -rf .venv
        echo "Old .venv removed."
    else
        echo "Keeping existing .venv. You can manually remove it later."
        echo "Migration cancelled."
        exit 0
    fi
fi

echo ""
echo "Creating new virtual environment with UV..."
uv venv

echo "Virtual environment created successfully!"
echo ""

echo "Activating virtual environment..."
source .venv/bin/activate

echo "Installing Sik Sort with development dependencies..."
uv pip install -e ".[dev]"

echo ""
echo "=================================="
echo "Migration Complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Run tests to verify: uv run pytest"
echo "2. Try the application: sik --help"
echo "3. Check out UV_QUICK_REFERENCE.md for UV commands"
echo ""
echo "Your virtual environment is now active!"
echo "To activate it in the future, run: source .venv/bin/activate"
