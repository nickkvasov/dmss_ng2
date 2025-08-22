#!/bin/bash

# Nebula Graph Management Script
# This script provides easy management of Nebula Graph cluster using Docker Compose

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
NEBULA_DIR="$PROJECT_ROOT/nebula/nebula-docker-compose"
DOCKER_COMPOSE_FILE="$NEBULA_DIR/docker-compose.yaml"
DOCKER_COMPOSE_LITE_FILE="$NEBULA_DIR/docker-compose-lite.yaml"

# Default configuration
MODE="full"  # full or lite
TIMEOUT=120  # Timeout for health checks in seconds

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
    echo -e "${BLUE}  Nebula Graph Management${NC}"
    echo -e "${BLUE}================================${NC}"
}

# Function to check if Docker is running
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
}

# Function to check if Docker Compose is available
check_docker_compose() {
    if ! command -v docker-compose >/dev/null 2>&1 && ! docker compose version >/dev/null 2>&1; then
        print_error "Docker Compose is not available. Please install Docker Compose and try again."
        exit 1
    fi
}

# Function to get docker compose command
get_docker_compose_cmd() {
    if docker compose version >/dev/null 2>&1; then
        echo "docker compose"
    else
        echo "docker-compose"
    fi
}

# Function to get the appropriate docker-compose file
get_compose_file() {
    if [ "$MODE" = "lite" ]; then
        echo "$DOCKER_COMPOSE_LITE_FILE"
    else
        echo "$DOCKER_COMPOSE_FILE"
    fi
}

# Function to wait for service health
wait_for_service() {
    local service=$1
    local timeout=$2
    local elapsed=0
    
    print_status "Waiting for $service to be healthy..."
    
    while [ $elapsed -lt $timeout ]; do
        if docker-compose -f "$(get_compose_file)" ps "$service" | grep -q "healthy"; then
            print_status "$service is healthy"
            return 0
        fi
        
        sleep 2
        elapsed=$((elapsed + 2))
        echo -n "."
    done
    
    print_error "$service failed to become healthy within $timeout seconds"
    return 1
}

# Function to start Nebula Graph
start_nebula() {
    print_header
    print_status "Starting Nebula Graph in $MODE mode..."
    
    check_docker
    check_docker_compose
    
    local compose_file=$(get_compose_file)
    local compose_cmd=$(get_docker_compose_cmd)
    
    if [ ! -f "$compose_file" ]; then
        print_error "Docker Compose file not found: $compose_file"
        exit 1
    fi
    
    # Create necessary directories
    mkdir -p "$NEBULA_DIR/data"
    mkdir -p "$NEBULA_DIR/logs"
    
    # Start services
    print_status "Starting services with $compose_cmd..."
    cd "$NEBULA_DIR"
    
    if [ "$MODE" = "lite" ]; then
        $compose_cmd -f "$(basename "$compose_file")" up -d
    else
        $compose_cmd -f "$(basename "$compose_file")" up -d
    fi
    
    # Wait for services to be healthy
    print_status "Waiting for services to be ready..."
    
    if [ "$MODE" = "lite" ]; then
        wait_for_service "metad0" $TIMEOUT
        wait_for_service "storaged0" $TIMEOUT
        wait_for_service "graphd" $TIMEOUT
    else
        wait_for_service "metad0" $TIMEOUT
        wait_for_service "metad1" $TIMEOUT
        wait_for_service "metad2" $TIMEOUT
        wait_for_service "storaged0" $TIMEOUT
        wait_for_service "storaged1" $TIMEOUT
        wait_for_service "storaged2" $TIMEOUT
        wait_for_service "graphd" $TIMEOUT
        wait_for_service "graphd1" $TIMEOUT
        wait_for_service "graphd2" $TIMEOUT
    fi
    
    print_status "Nebula Graph started successfully!"
    print_status "Graph service is available at: localhost:9669"
    print_status "HTTP service is available at: localhost:19669"
    
    if [ "$MODE" = "lite" ]; then
        print_status "Default credentials: root/nebula"
    else
        print_status "Default credentials: root/nebula"
        print_status "Console service is running to configure storage hosts"
    fi
}

# Function to stop Nebula Graph
stop_nebula() {
    print_header
    print_status "Stopping Nebula Graph..."
    
    check_docker
    check_docker_compose
    
    local compose_file=$(get_compose_file)
    local compose_cmd=$(get_docker_compose_cmd)
    
    if [ ! -f "$compose_file" ]; then
        print_error "Docker Compose file not found: $compose_file"
        exit 1
    fi
    
    cd "$NEBULA_DIR"
    
    print_status "Stopping services..."
    if [ "$MODE" = "lite" ]; then
        $compose_cmd -f "$(basename "$compose_file")" down
    else
        $compose_cmd -f "$(basename "$compose_file")" down
    fi
    
    print_status "Nebula Graph stopped successfully!"
}

# Function to restart Nebula Graph
restart_nebula() {
    print_header
    print_status "Restarting Nebula Graph..."
    
    stop_nebula
    sleep 2
    start_nebula
}

# Function to show status
show_status() {
    print_header
    print_status "Nebula Graph Status:"
    
    check_docker
    check_docker_compose
    
    local compose_file=$(get_compose_file)
    local compose_cmd=$(get_docker_compose_cmd)
    
    if [ ! -f "$compose_file" ]; then
        print_error "Docker Compose file not found: $compose_file"
        exit 1
    fi
    
    cd "$NEBULA_DIR"
    
    print_status "Service status:"
    if [ "$MODE" = "lite" ]; then
        $compose_cmd -f "$(basename "$compose_file")" ps
    else
        $compose_cmd -f "$(basename "$compose_file")" ps
    fi
    
    echo ""
    print_status "Container logs (last 10 lines):"
    if [ "$MODE" = "lite" ]; then
        $compose_cmd -f "$(basename "$compose_file")" logs --tail=10
    else
        $compose_cmd -f "$(basename "$compose_file")" logs --tail=10
    fi
}

# Function to show logs
show_logs() {
    print_header
    print_status "Showing Nebula Graph logs..."
    
    check_docker
    check_docker_compose
    
    local compose_file=$(get_compose_file)
    local compose_cmd=$(get_docker_compose_cmd)
    
    if [ ! -f "$compose_file" ]; then
        print_error "Docker Compose file not found: $compose_file"
        exit 1
    fi
    
    cd "$NEBULA_DIR"
    
    if [ "$MODE" = "lite" ]; then
        $compose_cmd -f "$(basename "$compose_file")" logs -f
    else
        $compose_cmd -f "$(basename "$compose_file")" logs -f
    fi
}

# Function to clean up (remove containers, networks, and volumes)
cleanup() {
    print_header
    print_warning "This will remove all Nebula Graph containers, networks, and volumes!"
    print_warning "All data will be lost!"
    
    read -p "Are you sure you want to continue? (y/N): " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_status "Cleanup cancelled."
        exit 0
    fi
    
    check_docker
    check_docker_compose
    
    local compose_file=$(get_compose_file)
    local compose_cmd=$(get_docker_compose_cmd)
    
    if [ ! -f "$compose_file" ]; then
        print_error "Docker Compose file not found: $compose_file"
        exit 1
    fi
    
    cd "$NEBULA_DIR"
    
    print_status "Stopping and removing containers..."
    if [ "$MODE" = "lite" ]; then
        $compose_cmd -f "$(basename "$compose_file")" down -v
    else
        $compose_cmd -f "$(basename "$compose_file")" down -v
    fi
    
    print_status "Removing data and logs directories..."
    rm -rf "$NEBULA_DIR/data" "$NEBULA_DIR/logs"
    
    print_status "Cleanup completed successfully!"
}

# Function to show help
show_help() {
    print_header
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  start     Start Nebula Graph cluster"
    echo "  stop      Stop Nebula Graph cluster"
    echo "  restart   Restart Nebula Graph cluster"
    echo "  status    Show cluster status"
    echo "  logs      Show cluster logs (follow mode)"
    echo "  cleanup   Remove all containers, networks, volumes, and data"
    echo "  help      Show this help message"
    echo ""
    echo "Options:"
    echo "  --mode MODE    Set cluster mode: full (default) or lite"
    echo "  --timeout SEC  Set health check timeout in seconds (default: 120)"
    echo ""
    echo "Examples:"
    echo "  $0 start                    # Start full cluster"
    echo "  $0 start --mode lite        # Start lite cluster"
    echo "  $0 stop                     # Stop cluster"
    echo "  $0 status                   # Show status"
    echo "  $0 logs                     # Show logs"
    echo ""
    echo "Cluster Modes:"
    echo "  full: 3x metad, 3x storaged, 3x graphd (production-ready)"
    echo "  lite: 1x metad, 1x storaged, 1x graphd (development)"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --mode)
            MODE="$2"
            shift 2
            ;;
        --timeout)
            TIMEOUT="$2"
            shift 2
            ;;
        start|stop|restart|status|logs|cleanup|help)
            COMMAND="$1"
            shift
            ;;
        *)
            print_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Validate mode
if [ "$MODE" != "full" ] && [ "$MODE" != "lite" ]; then
    print_error "Invalid mode: $MODE. Use 'full' or 'lite'."
    exit 1
fi

# Execute command
case ${COMMAND:-help} in
    start)
        start_nebula
        ;;
    stop)
        stop_nebula
        ;;
    restart)
        restart_nebula
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    cleanup)
        cleanup
        ;;
    help|*)
        show_help
        ;;
esac
