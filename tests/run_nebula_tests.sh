#!/bin/bash

# Nebula Graph Test Runner Script
# This script runs comprehensive tests for the Nebula Graph system

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
TEST_SCRIPT="$SCRIPT_DIR/test_nebula.py"
LOG_FILE="$SCRIPT_DIR/nebula_test.log"
RESULTS_FILE="$SCRIPT_DIR/nebula_test_results.json"

# Default configuration
HOST="localhost"
PORT=9669
USERNAME="root"
PASSWORD="nebula"
SAVE_RESULTS=true
TIMEOUT=300  # 5 minutes timeout

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}  Nebula Graph Test Runner${NC}"
    echo -e "${BLUE}================================${NC}"
}

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check if Python 3 is available
    if ! command -v python3 >/dev/null 2>&1; then
        print_error "Python 3 is not available. Please install Python 3 and try again."
        exit 1
    fi
    
    # Check if required Python packages are available
    python3 -c "import requests, json, subprocess, logging" 2>/dev/null || {
        print_error "Required Python packages are missing. Please install: requests"
        print_status "You can install them with: pip3 install requests"
        exit 1
    }
    
    # Check if nebula3-python is available (optional but recommended)
    python3 -c "import nebula3" 2>/dev/null || {
        print_warning "nebula3-python package not found. Some tests will be skipped."
        print_status "You can install it with: pip3 install nebula3-python"
    }
    
    # Check if test script exists
    if [ ! -f "$TEST_SCRIPT" ]; then
        print_error "Test script not found: $TEST_SCRIPT"
        exit 1
    fi
    
    # Make test script executable
    chmod +x "$TEST_SCRIPT"
    
    print_status "Prerequisites check passed!"
}

# Function to check if Nebula is running
check_nebula_running() {
    print_status "Checking if Nebula Graph is running..."
    
    # Check if Docker is running
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    
    # Check if Nebula containers are running
    if ! docker ps --filter "name=nebula" --format "table {{.Names}}" | grep -q nebula; then
        print_warning "Nebula containers are not running."
        print_status "You can start them with: ./scripts/nebula.sh start"
        read -p "Do you want to start Nebula Graph now? (y/N): " -n 1 -r
        echo
        
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_status "Starting Nebula Graph..."
            cd "$PROJECT_ROOT"
            ./scripts/nebula.sh start --mode lite
            
            # Wait for services to be ready
            print_status "Waiting for services to be ready..."
            sleep 30
        else
            print_error "Nebula Graph must be running to run tests."
            exit 1
        fi
    else
        print_status "Nebula Graph is running!"
    fi
}

# Function to run tests
run_tests() {
    print_status "Running Nebula Graph tests..."
    
    # Create logs directory if it doesn't exist
    mkdir -p "$SCRIPT_DIR"
    
    # Run the test script with timeout (cross-platform)
    print_status "Executing test script..."
    
    # Check if timeout command is available
    if command -v timeout >/dev/null 2>&1; then
        # Linux/Unix with timeout command
        if timeout "$TIMEOUT" python3 "$TEST_SCRIPT" \
            --host "$HOST" \
            --port "$PORT" \
            --username "$USERNAME" \
            --password "$PASSWORD" \
            --save-results \
            --output "$RESULTS_FILE"; then
            
            print_status "Tests completed successfully!"
            return 0
        else
            exit_code=$?
            if [ $exit_code -eq 124 ]; then
                print_error "Tests timed out after $TIMEOUT seconds"
            else
                print_error "Tests failed with exit code $exit_code"
            fi
            return $exit_code
        fi
    else
        # macOS without timeout command - use gtimeout if available, otherwise run without timeout
        if command -v gtimeout >/dev/null 2>&1; then
            # macOS with GNU timeout installed via Homebrew
            if gtimeout "$TIMEOUT" python3 "$TEST_SCRIPT" \
                --host "$HOST" \
                --port "$PORT" \
                --username "$USERNAME" \
                --password "$PASSWORD" \
                --save-results \
                --output "$RESULTS_FILE"; then
                
                print_status "Tests completed successfully!"
                return 0
            else
                exit_code=$?
                if [ $exit_code -eq 124 ]; then
                    print_error "Tests timed out after $TIMEOUT seconds"
                else
                    print_error "Tests failed with exit code $exit_code"
                fi
                return $exit_code
            fi
        else
            # No timeout available - run without timeout
            print_warning "No timeout command available. Running tests without timeout protection."
            print_warning "To install timeout on macOS: brew install coreutils"
            
            if python3 "$TEST_SCRIPT" \
                --host "$HOST" \
                --port "$PORT" \
                --username "$USERNAME" \
                --password "$PASSWORD" \
                --save-results \
                --output "$RESULTS_FILE"; then
                
                print_status "Tests completed successfully!"
                return 0
            else
                exit_code=$?
                print_error "Tests failed with exit code $exit_code"
                return $exit_code
            fi
        fi
    fi
}

# Function to show test results
show_results() {
    if [ -f "$RESULTS_FILE" ]; then
        print_status "Test results summary:"
        echo ""
        
        # Extract and display summary from JSON
        if command -v jq >/dev/null 2>&1; then
            # Check if the file has the expected structure
            if jq -e '.test_results' "$RESULTS_FILE" >/dev/null 2>&1; then
                echo "Total Tests: $(jq '.test_results | length' "$RESULTS_FILE")"
                echo "Passed: $(jq '[.test_results[] | select(.success == true)] | length' "$RESULTS_FILE")"
                echo "Failed: $(jq '[.test_results[] | select(.success == false)] | length' "$RESULTS_FILE")"
                echo "Success Rate: $(jq '([.test_results[] | select(.success == true)] | length / (.test_results | length) * 100) | round' "$RESULTS_FILE")%"
            else
                print_warning "Unexpected JSON structure, showing raw results file:"
                cat "$RESULTS_FILE"
            fi
        else
            print_warning "jq not available, showing raw results file:"
            cat "$RESULTS_FILE"
        fi
        
        echo ""
        print_status "Detailed results saved to: $RESULTS_FILE"
        print_status "Log file: $LOG_FILE"
    else
        print_warning "No results file found"
    fi
}

# Function to show help
show_help() {
    print_header
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --host HOST        Nebula Graph host (default: localhost)"
    echo "  --port PORT        Nebula Graph port (default: 9669)"
    echo "  --username USER    Username (default: root)"
    echo "  --password PASS    Password (default: nebula)"
    echo "  --timeout SEC      Test timeout in seconds (default: 300)"
    echo "  --no-save          Don't save results to JSON file"
    echo "  --help             Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                                    # Run tests with defaults"
    echo "  $0 --host 192.168.1.100              # Test remote host"
    echo "  $0 --timeout 600                     # 10 minute timeout"
    echo "  $0 --no-save                         # Don't save results"
    echo ""
    echo "Prerequisites:"
    echo "  - Python 3 with requests module"
    echo "  - Docker running with Nebula containers"
    echo "  - Network connectivity to Nebula Graph"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --host)
            HOST="$2"
            shift 2
            ;;
        --port)
            PORT="$2"
            shift 2
            ;;
        --username)
            USERNAME="$2"
            shift 2
            ;;
        --password)
            PASSWORD="$2"
            shift 2
            ;;
        --timeout)
            TIMEOUT="$2"
            shift 2
            ;;
        --no-save)
            SAVE_RESULTS=false
            shift
            ;;
        --help)
            show_help
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Main execution
main() {
    print_header
    
    # Check prerequisites
    check_prerequisites
    
    # Check if Nebula is running
    check_nebula_running
    
    # Run tests
    if run_tests; then
        print_status "All tests completed!"
        show_results
        exit 0
    else
        print_error "Tests failed!"
        show_results
        exit 1
    fi
}

# Run main function
main "$@"
