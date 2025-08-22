# Tests Directory

This directory contains comprehensive test scripts for the Nebula Graph system.

## Available Test Scripts

### `test_nebula.py` - Python Test Script

A comprehensive Python test script that performs various tests on the Nebula Graph system.

#### Features

- **Docker Services Test**: Verifies Docker containers are running
- **HTTP Endpoint Test**: Tests HTTP API connectivity
- **Graph Connection Test**: Tests Graph service port connectivity
- **Health Checks**: Tests health endpoints for all services
- **Performance Metrics**: Collects performance data
- **Nebula Console Test**: Tests console connectivity
- **Basic Operations Test**: Tests basic graph operations

#### Usage

```bash
# Basic usage
python3 tests/test_nebula.py

# With custom parameters
python3 tests/test_nebula.py --host localhost --port 9669 --username root --password nebula

# Save results to JSON file
python3 tests/test_nebula.py --save-results --output results.json

# Show help
python3 tests/test_nebula.py --help
```

#### Options

- `--host HOST`: Nebula Graph host (default: localhost)
- `--port PORT`: Nebula Graph port (default: 9669)
- `--username USER`: Username (default: root)
- `--password PASS`: Password (default: nebula)
- `--save-results`: Save results to JSON file
- `--output FILE`: Output file for results (default: tests/nebula_test_results.json)

### `run_nebula_tests.sh` - Test Runner Script

A shell script wrapper that provides an easy way to run tests with proper setup and error handling.

#### Features

- **Prerequisites Check**: Verifies Python and dependencies
- **Nebula Status Check**: Checks if Nebula is running
- **Auto-start Option**: Can start Nebula if not running
- **Timeout Handling**: Prevents hanging tests
- **Results Summary**: Shows test results summary
- **Logging**: Comprehensive logging to file and console

#### Usage

```bash
# Basic usage
./tests/run_nebula_tests.sh

# With custom parameters
./tests/run_nebula_tests.sh --host 192.168.1.100 --timeout 600

# Don't save results
./tests/run_nebula_tests.sh --no-save

# Show help
./tests/run_nebula_tests.sh --help
```

#### Options

- `--host HOST`: Nebula Graph host (default: localhost)
- `--port PORT`: Nebula Graph port (default: 9669)
- `--username USER`: Username (default: root)
- `--password PASS`: Password (default: nebula)
- `--timeout SEC`: Test timeout in seconds (default: 300)
- `--no-save`: Don't save results to JSON file
- `--help`: Show help message

## Test Coverage

### 1. Docker Services Test
- Verifies Docker is running
- Checks for Nebula containers
- Reports container status

### 2. HTTP Endpoint Test
- Tests HTTP API connectivity
- Verifies status endpoint
- Checks response format

### 3. Graph Connection Test
- Tests Graph service port (9669)
- Uses netcat to verify connectivity
- Reports connection status

### 4. Health Checks
- Tests health endpoints for:
  - metad0 (port 19559)
  - storaged0 (port 19779)
  - graphd (port 19669)
- Reports health status for each service

### 5. Performance Metrics
- Measures HTTP response time
- Collects Docker container stats
- Reports resource usage

### 6. Nebula Python Client Test
- Tests nebula3-python client connectivity
- Executes basic queries using official Python client
- Verifies authentication and connection pool

### 7. Basic Operations Test
- Tests basic graph operations:
  - SHOW HOSTS
  - SHOW SPACES
  - CREATE SPACE
  - USE SPACE
  - DROP SPACE
- Reports query success/failure

## Prerequisites

### System Requirements
- Python 3.6+
- Docker and Docker Compose
- Network connectivity to Nebula Graph
- `nc` (netcat) or similar tool for port testing
- `timeout` command (optional, for timeout protection)
  - Linux: Usually pre-installed
  - macOS: Install with `brew install coreutils` (provides `gtimeout`)

### Python Dependencies
```bash
# Install dependencies
pip3 install -r tests/requirements.txt

# Or install manually
pip3 install requests nebula3-python
```

### Optional Tools
- `jq`: For JSON result parsing (enhanced output)
- `nebula-console`: For command-line graph operations (optional)

## Output Files

### Log Files
- `tests/nebula_test.log`: Detailed test execution log
- Console output: Real-time test progress

### Result Files
- `tests/nebula_test_results.json`: Detailed test results in JSON format
- Contains:
  - Test timestamp
  - Connection details
  - Individual test results
  - Performance metrics
  - Error details

## Example Output

```
================================
  Nebula Graph Test Runner
================================
[INFO] Checking prerequisites...
[INFO] Prerequisites check passed!
[INFO] Checking if Nebula Graph is running...
[INFO] Nebula Graph is running!
[INFO] Running Nebula Graph tests...
[INFO] Executing test script...
2024-01-15 10:30:00 - INFO - Starting Nebula Graph system tests...
2024-01-15 10:30:01 - INFO - ✅ PASS Docker Services: Found 3 Nebula containers (0.85s)
2024-01-15 10:30:02 - INFO - ✅ PASS HTTP Endpoint: HTTP endpoint is accessible (0.12s)
2024-01-15 10:30:03 - INFO - ✅ PASS Graph Connection: Port 9669 is accessible (0.05s)
2024-01-15 10:30:04 - INFO - ✅ PASS Health Checks: 3/3 services healthy (1.23s)
2024-01-15 10:30:05 - INFO - ✅ PASS Performance Metrics: Performance metrics collected (0.45s)
2024-01-15 10:30:06 - INFO - ✅ PASS Nebula Console: Successfully connected and executed query (0.67s)
2024-01-15 10:30:07 - INFO - ✅ PASS Basic Operations: 6/6 queries succeeded (1.89s)

============================================================
TEST SUMMARY
============================================================
Total Tests: 7
Passed: 7
Failed: 0
Success Rate: 100.0%
Total Duration: 5.26s
============================================================

[INFO] All tests completed!
[INFO] Test results summary:

Total Tests: 7
Passed: 7
Failed: 0
Success Rate: 100%

[INFO] Detailed results saved to: tests/nebula_test_results.json
[INFO] Log file: tests/nebula_test.log
```

## Troubleshooting

### Common Issues

1. **Docker not running**
   ```bash
   # Start Docker Desktop or Docker daemon
   sudo systemctl start docker  # Linux
   # Or start Docker Desktop on macOS/Windows
   ```

2. **Nebula containers not running**
   ```bash
   # Start Nebula Graph
   ./scripts/nebula.sh start --mode lite
   ```

3. **Python dependencies missing**
   ```bash
   # Install dependencies
   pip3 install -r tests/requirements.txt
   
   # Or install manually
   pip3 install requests nebula3-python
   ```

4. **Port conflicts**
   ```bash
   # Check if ports are in use
   netstat -tulpn | grep :9669
   netstat -tulpn | grep :19669
   ```

5. **Permission issues**
   ```bash
   # Make scripts executable
   chmod +x tests/run_nebula_tests.sh
   chmod +x tests/test_nebula.py
   ```

6. **Timeout command not found (macOS)**
   ```bash
   # Install GNU coreutils for timeout command
   brew install coreutils
   
   # Or run without timeout protection
   python3 tests/test_nebula.py --save-results
   ```

### Debug Mode

For detailed debugging, you can run the Python script directly:

```bash
# Run with verbose logging
python3 -u tests/test_nebula.py --save-results 2>&1 | tee debug.log
```

## Integration with CI/CD

The test scripts can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Test Nebula Graph
  run: |
    ./scripts/nebula.sh start --mode lite
    sleep 60  # Wait for services to be ready
    ./tests/run_nebula_tests.sh
```

## Notes

- Tests are designed to be non-destructive (they clean up after themselves)
- The script follows the memory about tests not passing on failures
- All test resources are located in the tests directory
- Tests assume Nebula server is already running (following user preference)
- Results are saved in timestamped format for historical analysis
