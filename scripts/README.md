# Scripts Directory

This directory contains utility scripts for managing the knowledge graph project.

## Available Scripts

### `nebula.sh` - Nebula Graph Management

A comprehensive script for managing Nebula Graph cluster using Docker Compose.

#### Features

- **Start/Stop/Restart** Nebula Graph cluster
- **Status monitoring** with health checks
- **Log viewing** with follow mode
- **Cleanup functionality** for complete reset
- **Two cluster modes**: full (production) and lite (development)
- **Colored output** for better readability
- **Error handling** and validation

#### Usage

```bash
# Basic usage
./scripts/nebula.sh [COMMAND] [OPTIONS]

# Start the cluster (default: full mode)
./scripts/nebula.sh start

# Start in lite mode (development)
./scripts/nebula.sh start --mode lite

# Stop the cluster
./scripts/nebula.sh stop

# Restart the cluster
./scripts/nebula.sh restart

# Show cluster status
./scripts/nebula.sh status

# Show logs (follow mode)
./scripts/nebula.sh logs

# Clean up everything (removes data)
./scripts/nebula.sh cleanup

# Show help
./scripts/nebula.sh help
```

#### Options

- `--mode MODE`: Set cluster mode (`full` or `lite`)
- `--timeout SEC`: Set health check timeout in seconds (default: 120)

#### Cluster Modes

**Full Mode** (default):
- 3x metad (metadata service)
- 3x storaged (storage service)
- 3x graphd (graph service)
- Production-ready with high availability

**Lite Mode**:
- 1x metad
- 1x storaged
- 1x graphd
- Suitable for development and testing

#### Prerequisites

- Docker installed and running
- Docker Compose available (`docker-compose` or `docker compose`)

#### Default Access

After starting the cluster:
- **Graph service**: `localhost:9669`
- **HTTP service**: `localhost:19669`
- **Default credentials**: `root/nebula`

#### Examples

```bash
# Start full cluster for production
./scripts/nebula.sh start

# Start lite cluster for development
./scripts/nebula.sh start --mode lite

# Check status
./scripts/nebula.sh status

# View logs
./scripts/nebula.sh logs

# Stop cluster
./scripts/nebula.sh stop

# Complete cleanup (removes all data)
./scripts/nebula.sh cleanup
```

#### Troubleshooting

1. **Docker not running**: Start Docker Desktop or Docker daemon
2. **Port conflicts**: Ensure ports 9669 and 19669 are available
3. **Health check failures**: Increase timeout with `--timeout 300`
4. **Permission issues**: Ensure script is executable (`chmod +x scripts/nebula.sh`)

#### Notes

- The script automatically creates necessary directories (`data/`, `logs/`)
- Health checks ensure all services are ready before reporting success
- Cleanup removes all containers, networks, volumes, and data directories
- The script supports both `docker-compose` and `docker compose` commands
