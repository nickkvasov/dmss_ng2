#!/bin/bash

# End-to-End Nebula Graph Pipeline Runner
# Shell wrapper for run_end_to_end.py

set -e

# Default values
CONFIG_FILE="config.yaml"
ENVIRONMENT=""
SPACE_NAME=""
TIMESTAMPED=false
DRY_RUN=false
MOCK_MODE=false
SKIP_VALIDATION=false
VERBOSE=false
QUIET=false

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "End-to-End Nebula Graph Pipeline Runner"
    echo "Automates: Ontology → Schema Generation → Database Commit → Validation"
    echo ""
    echo "Options:"
    echo "  -c, --config FILE       Configuration file path (default: config.yaml)"
    echo "  -e, --environment ENV   Environment name (development, staging, production)"
    echo "  -s, --space-name NAME   Space name for schema generation"
    echo "  -t, --timestamped       Generate timestamped schema file"
    echo "  -d, --dry-run           Show what would be executed without actually executing"
    echo "  -m, --mock              Run in mock mode (no actual database connection)"
    echo "  --skip-validation       Skip schema and deployment validation steps"
    echo "  -v, --verbose           Enable verbose output"
    echo "  -q, --quiet             Suppress non-error output"
    echo "  -h, --help              Show this help message"
    echo ""
    echo "Environment Variables:"
    echo "  NEBULA_HOST             Override host"
    echo "  NEBULA_PORT             Override port"
    echo "  NEBULA_USERNAME         Override username"
    echo "  NEBULA_PASSWORD         Override password"
    echo ""
    echo "Examples:"
    echo "  # Run complete pipeline with default settings"
    echo "  $0"
    echo ""
    echo "  # Run with custom space name"
    echo "  $0 --space-name tourism_test1"
    echo ""
    echo "  # Run in dry-run mode"
    echo "  $0 --dry-run"
    echo ""
    echo "  # Run in mock mode for testing"
    echo "  $0 --mock"
    echo ""
    echo "  # Run for specific environment"
    echo "  $0 --environment production"
    echo ""
    echo "  # Generate timestamped schema"
    echo "  $0 --timestamped"
    echo ""
    echo "  # Skip validation steps"
    echo "  $0 --skip-validation"
    echo ""
    echo "Pipeline Steps:"
    echo "  1. Validate prerequisites (config, ontologies, directories)"
    echo "  2. Generate unified Nebula Graph schema from all ontologies"
    echo "  3. Validate generated schema (structure, content, statements)"
    echo "  4. Commit schema to Nebula Graph database"
    echo "  5. Validate deployment (check space creation, etc.)"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -c|--config)
            CONFIG_FILE="$2"
            shift 2
            ;;
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -s|--space-name)
            SPACE_NAME="$2"
            shift 2
            ;;
        -t|--timestamped)
            TIMESTAMPED=true
            shift
            ;;
        -d|--dry-run)
            DRY_RUN=true
            shift
            ;;
        -m|--mock)
            MOCK_MODE=true
            shift
            ;;
        --skip-validation)
            SKIP_VALIDATION=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -q|--quiet)
            QUIET=true
            shift
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        -*)
            echo "Unknown option: $1"
            show_usage
            exit 1
            ;;
        *)
            echo "Unexpected argument: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Check if Python script exists
if [[ ! -f "run_end_to_end.py" ]]; then
    echo "Error: run_end_to_end.py not found in current directory"
    exit 1
fi

# Check if configuration file exists
if [[ ! -f "$CONFIG_FILE" ]]; then
    echo "Warning: Configuration file $CONFIG_FILE not found"
    echo "The script will use default configuration values"
fi

# Build command
CMD="python run_end_to_end.py"

if [[ -n "$CONFIG_FILE" ]]; then
    CMD="$CMD --config \"$CONFIG_FILE\""
fi

if [[ -n "$ENVIRONMENT" ]]; then
    CMD="$CMD --environment \"$ENVIRONMENT\""
fi

if [[ -n "$SPACE_NAME" ]]; then
    CMD="$CMD --space-name \"$SPACE_NAME\""
fi

if [[ "$TIMESTAMPED" == true ]]; then
    CMD="$CMD --timestamped"
fi

if [[ "$DRY_RUN" == true ]]; then
    CMD="$CMD --dry-run"
fi

if [[ "$MOCK_MODE" == true ]]; then
    CMD="$CMD --mock"
fi

if [[ "$SKIP_VALIDATION" == true ]]; then
    CMD="$CMD --skip-validation"
fi

if [[ "$VERBOSE" == true ]]; then
    CMD="$CMD --verbose"
fi

if [[ "$QUIET" == true ]]; then
    CMD="$CMD --quiet"
fi

# Print pipeline information
echo "End-to-End Nebula Graph Pipeline Runner"
echo "========================================"
echo "Configuration: $CONFIG_FILE"
if [[ -n "$ENVIRONMENT" ]]; then
    echo "Environment: $ENVIRONMENT"
fi
if [[ -n "$SPACE_NAME" ]]; then
    echo "Space Name: $SPACE_NAME"
fi
echo "Execution Mode: $(
    if [[ "$DRY_RUN" == true ]]; then
        echo "DRY RUN"
    elif [[ "$MOCK_MODE" == true ]]; then
        echo "MOCK"
    else
        echo "LIVE"
    fi
)"
if [[ "$TIMESTAMPED" == true ]]; then
    echo "Timestamped Schema: Yes"
fi
if [[ "$SKIP_VALIDATION" == true ]]; then
    echo "Validation: Skipped"
fi
echo ""

# Execute command
echo "Executing: $CMD"
echo ""
eval $CMD

# Check exit code
if [[ $? -eq 0 ]]; then
    echo ""
    echo "✅ Pipeline completed successfully!"
else
    echo ""
    echo "❌ Pipeline failed!"
    exit 1
fi
