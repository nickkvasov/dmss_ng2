#!/bin/bash
# Tourist Generator Test Runner Script
# This script activates the project's virtual environment and runs the tourist generator tests

set -e  # Exit on any error

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "Tourist Generator Test Runner"
echo "============================"
echo "Project root: $PROJECT_ROOT"
echo "Script directory: $SCRIPT_DIR"
echo ""

# Check if virtual environment exists
if [ ! -d "$PROJECT_ROOT/.venv" ]; then
    echo "Error: Virtual environment not found at $PROJECT_ROOT/.venv"
    echo "Please create the virtual environment first:"
    echo "  cd $PROJECT_ROOT"
    echo "  python -m venv .venv"
    echo "  source .venv/bin/activate"
    echo "  pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source "$PROJECT_ROOT/.venv/bin/activate"

# Verify Python path
echo "Using Python: $(which python)"
echo "Python version: $(python --version)"
echo ""

# Change to project root directory
cd "$PROJECT_ROOT"

# Run the tourist generator tests
echo "Running tourist generator tests..."
python "$SCRIPT_DIR/test_tourist_generator.py"

echo ""
echo "Tourist generator tests completed!"
