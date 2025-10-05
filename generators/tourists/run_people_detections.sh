#!/bin/bash
# People Detections Generator Runner Script
# This script activates the project's virtual environment and runs the people detections generator

set -e  # Exit on any error

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "People Detections Generator Runner"
echo "=================================="
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

# Run the people detections generator with all arguments passed to this script
echo "Running people detections generator..."
python "$SCRIPT_DIR/people_detections_generator.py" "$@"

echo ""
echo "People detections generator completed!"
