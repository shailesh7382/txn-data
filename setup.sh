#!/bin/bash
set -e

echo "Checking for Python 3..."
if ! command -v python3 &> /dev/null; then
    echo "Python 3 not found. Installing (Debian/Ubuntu example)..."
    sudo apt-get update
    sudo apt-get install -y python3 python3-venv python3-pip
fi

echo "Setting up Python virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

echo "Upgrading pip..."
pip install --upgrade pip

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Making run_all.sh executable..."
chmod +x run_all.sh

echo "Setup complete."
echo "To activate the environment, run: source .venv/bin/activate"
echo "To run the workflow, use: ./run_all.sh"

