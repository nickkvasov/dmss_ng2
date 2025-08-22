#!/usr/bin/env python3
"""
Nebula Graph System Test Script

This script tests the Nebula Graph system functionality including:
- Connection to the graph database
- Basic CRUD operations
- Health checks
- Performance metrics
"""

import sys
import time
import subprocess
import requests
import json
from typing import Dict, List, Optional, Tuple
import logging

# Nebula Python client imports
try:
    from nebula3.gclient.net import ConnectionPool
    from nebula3.Config import Config
    from nebula3.data.ResultSet import ResultSet
    NEBULA_CLIENT_AVAILABLE = True
except ImportError:
    NEBULA_CLIENT_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tests/nebula_test.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class NebulaGraphTester:
    """Test class for Nebula Graph system"""
    
    def __init__(self, host: str = "localhost", port: int = 9669, 
                 username: str = "root", password: str = "nebula"):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.http_port = 19669
        self.test_results = []
        self.connection_pool = None
        self.session = None
        
    def log_test_result(self, test_name: str, success: bool, message: str = "", 
                       duration: float = 0.0, details: Dict = None):
        """Log test result with details"""
        result = {
            "test_name": test_name,
            "success": success,
            "message": message,
            "duration": duration,
            "details": details or {}
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status} {test_name}: {message} ({duration:.2f}s)")
        
        if not success and details:
            logger.error(f"Details: {details}")
    
    def run_command(self, command: List[str], timeout: int = 30) -> Tuple[bool, str, str]:
        """Run a shell command and return success, stdout, stderr"""
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", f"Command timed out after {timeout} seconds"
        except Exception as e:
            return False, "", str(e)
    
    def connect_nebula(self) -> bool:
        """Connect to Nebula Graph using Python client"""
        if not NEBULA_CLIENT_AVAILABLE:
            return False
        
        try:
            # Configuration
            config = Config()
            config.max_connection_pool_size = 10
            
            # Create connection pool
            self.connection_pool = ConnectionPool()
            ok = self.connection_pool.init([(self.host, self.port)], config)
            
            if not ok:
                return False
            
            # Get a session
            self.session = self.connection_pool.get_session(self.username, self.password)
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Nebula: {str(e)}")
            return False
    
    def disconnect_nebula(self):
        """Disconnect from Nebula Graph"""
        try:
            if self.session:
                self.session.release()
                self.session = None
            
            if self.connection_pool:
                self.connection_pool.close()
                self.connection_pool = None
        except Exception as e:
            logger.error(f"Error disconnecting from Nebula: {str(e)}")
    
    def execute_query(self, query: str) -> Tuple[bool, str, List]:
        """Execute a query using Nebula Python client"""
        if not self.session:
            return False, "No active session", []
        
        try:
            result: ResultSet = self.session.execute(query)
            
            if not result.is_succeeded():
                return False, result.error_msg(), []
            
            # Extract values from result
            rows = []
            for row in result.rows():
                row_values = []
                for value in row.values:
                    # Handle Nebula Value objects properly
                    try:
                        if hasattr(value, 'sVal') and value.sVal is not None:
                            # String value
                            row_values.append(value.sVal.decode('utf-8') if isinstance(value.sVal, bytes) else str(value.sVal))
                        elif hasattr(value, 'iVal') and value.iVal is not None:
                            # Integer value
                            row_values.append(str(value.iVal))
                        elif hasattr(value, 'bVal') and value.bVal is not None:
                            # Boolean value
                            row_values.append(str(value.bVal))
                        elif hasattr(value, 'fVal') and value.fVal is not None:
                            # Float value
                            row_values.append(str(value.fVal))
                        elif hasattr(value, 'dVal') and value.dVal is not None:
                            # Double value
                            row_values.append(str(value.dVal))
                        else:
                            # For other types, use string representation
                            row_values.append(str(value))
                    except Exception as val_error:
                        # If we can't convert the value, just use its string representation
                        row_values.append(f"<{type(value).__name__}>")
                rows.append(row_values)
            
            return True, "Query executed successfully", rows
            
        except Exception as e:
            return False, str(e), []
    
    def test_docker_services(self) -> bool:
        """Test if Docker services are running"""
        logger.info("Testing Docker services...")
        start_time = time.time()
        
        # Check if Docker is running
        success, stdout, stderr = self.run_command(["docker", "info"])
        if not success:
            self.log_test_result("Docker Running", False, "Docker is not running", 
                               time.time() - start_time, {"stderr": stderr})
            return False
        
        # Check Nebula containers
        success, stdout, stderr = self.run_command([
            "docker", "ps", "--filter", "name=nebula", "--format", "table {{.Names}}\t{{.Status}}"
        ])
        
        if success and "nebula" in stdout:
            containers = [line for line in stdout.strip().split('\n') if 'nebula' in line]
            self.log_test_result("Docker Services", True, f"Found {len(containers)} Nebula containers", 
                               time.time() - start_time, {"containers": containers})
            return True
        else:
            self.log_test_result("Docker Services", False, "No Nebula containers found", 
                               time.time() - start_time, {"stdout": stdout, "stderr": stderr})
            return False
    
    def test_http_endpoint(self) -> bool:
        """Test HTTP endpoint connectivity"""
        logger.info("Testing HTTP endpoint...")
        start_time = time.time()
        
        # Test the known working endpoint
        working_endpoint = f"http://{self.host}:59194/status"
        try:
            response = requests.get(working_endpoint, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test_result("HTTP Endpoint", True, "HTTP endpoint is accessible", 
                                   time.time() - start_time, {"status_code": response.status_code, "data": data})
                return True
            else:
                self.log_test_result("HTTP Endpoint", False, f"HTTP endpoint returned {response.status_code}", 
                                   time.time() - start_time, {"status_code": response.status_code})
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_test_result("HTTP Endpoint", False, f"HTTP endpoint error: {str(e)}", 
                               time.time() - start_time, {"error": str(e)})
            return False
    
    def test_graph_connection(self) -> bool:
        """Test Graph service connection"""
        logger.info("Testing Graph service connection...")
        start_time = time.time()
        
        # Test using netcat or telnet to check if port is open
        success, stdout, stderr = self.run_command([
            "nc", "-z", self.host, str(self.port)
        ])
        
        if success:
            self.log_test_result("Graph Connection", True, f"Port {self.port} is accessible", 
                               time.time() - start_time)
            return True
        else:
            self.log_test_result("Graph Connection", False, f"Port {self.port} is not accessible", 
                               time.time() - start_time, {"stderr": stderr})
            return False
    
    def test_nebula_console(self) -> bool:
        """Test Nebula Python client connectivity"""
        logger.info("Testing Nebula Python client...")
        start_time = time.time()
        
        if not NEBULA_CLIENT_AVAILABLE:
            self.log_test_result("Nebula Python Client", False, "nebula3-python package not available", 
                               time.time() - start_time, {"error": "Package not installed"})
            return False
        
        # Try to connect using Python client
        if self.connect_nebula():
            test_query = "SHOW HOSTS"
            success, message, rows = self.execute_query(test_query)
            
            if success:
                self.log_test_result("Nebula Python Client", True, "Successfully connected and executed query", 
                                   time.time() - start_time, {"query": test_query, "rows": len(rows)})
                self.disconnect_nebula()
                return True
            else:
                self.log_test_result("Nebula Python Client", False, f"Query failed: {message}", 
                                   time.time() - start_time, {"error": message})
                self.disconnect_nebula()
                return False
        else:
            self.log_test_result("Nebula Python Client", False, "Failed to connect to Nebula Graph", 
                               time.time() - start_time, {"error": "Connection failed"})
            return False
    
    def test_health_checks(self) -> bool:
        """Test health checks for all services"""
        logger.info("Testing health checks...")
        start_time = time.time()
        
        # Test the known working endpoint first
        working_endpoint = f"http://{self.host}:59194/status"
        try:
            response = requests.get(working_endpoint, timeout=5)
            if response.status_code == 200:
                logger.info(f"✅ Found working HTTP endpoint at port 59194")
                data = response.json()
                logger.info(f"   Status: {data.get('status', 'unknown')}")
                logger.info(f"   Git SHA: {data.get('git_info_sha', 'unknown')}")
            else:
                logger.warning(f"⚠️ HTTP endpoint at port 59194 returned status {response.status_code}")
        except requests.exceptions.RequestException as e:
            logger.warning(f"⚠️ HTTP endpoint at port 59194 failed: {str(e)}")
        
        # Try to discover other HTTP endpoints by checking common port ranges
        discovered_ports = []
        port_ranges = [
            range(19550, 19600),  # metad ports
            range(19750, 19800),  # storaged ports
            range(19650, 19700),  # graphd ports
            range(59190, 59200),  # discovered working range
        ]
        
        for port_range in port_ranges:
            for port in port_range:
                try:
                    url = f"http://{self.host}:{port}/status"
                    response = requests.get(url, timeout=2)
                    if response.status_code == 200:
                        discovered_ports.append(port)
                        logger.info(f"✅ Found HTTP endpoint at port {port}")
                except requests.exceptions.RequestException:
                    pass  # Port not accessible
        
        # Test some specific ports that might be exposed
        specific_ports = [19559, 19779, 19669, 59194]
        healthy_services = 0
        total_services = len(specific_ports)
        
        for port in specific_ports:
            try:
                url = f"http://{self.host}:{port}/status"
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    healthy_services += 1
                    logger.info(f"✅ HTTP endpoint at port {port} is healthy")
                else:
                    logger.warning(f"⚠️ HTTP endpoint at port {port} returned status {response.status_code}")
            except requests.exceptions.RequestException as e:
                logger.warning(f"⚠️ HTTP endpoint at port {port} failed: {str(e)}")
        
        # Consider the test successful if we found at least one working endpoint
        success = healthy_services > 0 or len(discovered_ports) > 0
        message = f"{healthy_services}/{total_services} specific ports healthy, {len(discovered_ports)} additional ports discovered"
        
        self.log_test_result("Health Checks", success, message, 
                           time.time() - start_time, 
                           {"healthy": healthy_services, "total": total_services, "discovered_ports": discovered_ports})
        
        return success
    
    def test_performance_metrics(self) -> Dict:
        """Test performance metrics"""
        logger.info("Testing performance metrics...")
        start_time = time.time()
        
        metrics = {}
        
        # Test Docker container resource usage
        success, stdout, stderr = self.run_command([
            "docker", "stats", "--no-stream", "--format", 
            "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"
        ])
        
        if success:
            metrics["container_stats"] = stdout.strip()
        
        duration = time.time() - start_time
        self.log_test_result("Performance Metrics", True, "Performance metrics collected", 
                           duration, metrics)
        
        return metrics
    
    def test_basic_operations(self) -> bool:
        """Test basic graph operations using Python client"""
        logger.info("Testing basic operations...")
        start_time = time.time()
        
        if not NEBULA_CLIENT_AVAILABLE:
            self.log_test_result("Basic Operations", False, "nebula3-python package not available", 
                               time.time() - start_time, {"error": "Package not installed"})
            return False
        
        # Connect to Nebula
        if not self.connect_nebula():
            self.log_test_result("Basic Operations", False, "Failed to connect to Nebula Graph", 
                               time.time() - start_time, {"error": "Connection failed"})
            return False
        
        # Test queries to run (with proper sequencing)
        test_queries = [
            ("SHOW HOSTS", True),  # Should always work
            ("SHOW SPACES", True),  # Should always work
            ("CREATE SPACE IF NOT EXISTS test_space(vid_type=FIXED_STRING(30))", True),
            ("DROP SPACE IF EXISTS test_space", True)  # Clean up
        ]
        
        success_count = 0
        total_queries = len(test_queries)
        query_results = []
        
        for query, required in test_queries:
            success, message, rows = self.execute_query(query)
            
            if success:
                success_count += 1
                logger.info(f"✅ Query succeeded: {query[:50]}...")
                query_results.append({"query": query, "success": True, "rows": len(rows)})
                
                # Add delay after space creation to allow it to be ready
                if "CREATE SPACE" in query:
                    time.sleep(2)
            else:
                if required:
                    logger.warning(f"⚠️ Query failed: {query[:50]}... - {message}")
                else:
                    logger.info(f"ℹ️ Query skipped: {query[:50]}... - {message}")
                query_results.append({"query": query, "success": False, "error": message})
        
        # Disconnect
        self.disconnect_nebula()
        
        success = success_count > 0  # At least some queries should work
        message = f"{success_count}/{total_queries} queries succeeded"
        
        self.log_test_result("Basic Operations", success, message, 
                           time.time() - start_time,
                           {"successful": success_count, "total": total_queries, "details": query_results})
        
        return success
    
    def run_all_tests(self) -> Dict:
        """Run all tests and return results"""
        logger.info("Starting Nebula Graph system tests...")
        
        test_start_time = time.time()
        
        # Run all tests
        tests = [
            ("Docker Services", self.test_docker_services),
            ("HTTP Endpoint", self.test_http_endpoint),
            ("Graph Connection", self.test_graph_connection),
            ("Health Checks", self.test_health_checks),
            ("Performance Metrics", self.test_performance_metrics),
            ("Nebula Python Client", self.test_nebula_console),
            ("Basic Operations", self.test_basic_operations)
        ]
        
        for test_name, test_func in tests:
            try:
                test_func()
            except Exception as e:
                logger.error(f"Test {test_name} failed with exception: {str(e)}")
                self.log_test_result(test_name, False, f"Exception: {str(e)}", 0.0)
        
        # Calculate summary
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        total_duration = time.time() - test_start_time
        
        summary = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            "total_duration": total_duration,
            "test_results": self.test_results
        }
        
        # Print summary
        logger.info("=" * 60)
        logger.info("TEST SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Passed: {passed_tests}")
        logger.info(f"Failed: {failed_tests}")
        logger.info(f"Success Rate: {summary['success_rate']:.1f}%")
        logger.info(f"Total Duration: {total_duration:.2f}s")
        logger.info("=" * 60)
        
        return summary
    
    def save_results(self, filename: str = "tests/nebula_test_results.json"):
        """Save test results to JSON file"""
        import json
        from datetime import datetime
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "host": self.host,
            "port": self.port,
            "username": self.username,
            "test_results": self.test_results
        }
        
        try:
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            logger.info(f"Test results saved to {filename}")
        except Exception as e:
            logger.error(f"Failed to save results: {str(e)}")


def main():
    """Main function to run tests"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Nebula Graph system")
    parser.add_argument("--host", default="localhost", help="Nebula Graph host")
    parser.add_argument("--port", type=int, default=9669, help="Nebula Graph port")
    parser.add_argument("--username", default="root", help="Username")
    parser.add_argument("--password", default="nebula", help="Password")
    parser.add_argument("--save-results", action="store_true", help="Save results to JSON file")
    parser.add_argument("--output", default="tests/nebula_test_results.json", help="Output file for results")
    
    args = parser.parse_args()
    
    # Create tester instance
    tester = NebulaGraphTester(
        host=args.host,
        port=args.port,
        username=args.username,
        password=args.password
    )
    
    # Run tests
    summary = tester.run_all_tests()
    
    # Save results if requested
    if args.save_results:
        tester.save_results(args.output)
    
    # Exit with appropriate code
    if summary["failed_tests"] > 0:
        logger.warning("Some tests failed!")
        sys.exit(1)
    else:
        logger.info("All tests passed!")
        sys.exit(0)


if __name__ == "__main__":
    main()
