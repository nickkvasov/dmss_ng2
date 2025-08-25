#!/bin/bash

# POI Ingestion Workflow Script
# This script runs the complete POI ingestion process

set -e  # Exit on any error

echo "=== POI Ingestion Workflow ==="
echo ""

# Configuration
ONTOLOGY_DIR="../../ontology/poi"
DATA_DIR="../../data/generated"
CONFIG_FILE="config.yaml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

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

# Check if required directories exist
if [ ! -d "$ONTOLOGY_DIR" ]; then
    print_error "Ontology directory not found: $ONTOLOGY_DIR"
    exit 1
fi

if [ ! -d "$DATA_DIR" ]; then
    print_error "Data directory not found: $DATA_DIR"
    exit 1
fi

# Step 1: Check ontology and schema generator
print_status "Step 1: Checking ontology and schema generator..."
cd "$ONTOLOGY_DIR"

if [ ! -f "poi_ontology.yaml" ]; then
    print_error "Ontology file not found: poi_ontology.yaml"
    exit 1
fi

print_status "Ontology file found: poi_ontology.yaml"
echo ""

# Step 2: Check schema generator
print_status "Step 2: Checking schema generator..."
cd - > /dev/null  # Return to original directory

if [ ! -f "nebula_schema_generator.py" ]; then
    print_error "Schema generator not found: nebula_schema_generator.py"
    exit 1
fi

print_status "Schema generator found: nebula_schema_generator.py"
echo ""

# Step 3: Check for available data directories
print_status "Step 3: Checking for available data..."

# Find all subdirectories in the data directory
DATA_SUBDIRS=($(find "$DATA_DIR" -maxdepth 1 -type d -name "*" | grep -v "^$DATA_DIR$"))

if [ ${#DATA_SUBDIRS[@]} -eq 0 ]; then
    print_error "No data subdirectories found in $DATA_DIR"
    exit 1
fi

print_status "Found ${#DATA_SUBDIRS[@]} data directories:"
for dir in "${DATA_SUBDIRS[@]}"; do
    dirname=$(basename "$dir")
    echo "  - $dirname"
done
echo ""

# Step 4: Ask user which data to ingest
echo "Which data directory would you like to ingest?"
for i in "${!DATA_SUBDIRS[@]}"; do
    dirname=$(basename "${DATA_SUBDIRS[$i]}")
    echo "  $((i+1)). $dirname"
done
echo "  $(( ${#DATA_SUBDIRS[@]} + 1 )). All directories"

read -p "Enter your choice (1-$(( ${#DATA_SUBDIRS[@]} + 1 ))): " choice

# Validate choice
if ! [[ "$choice" =~ ^[0-9]+$ ]] || [ "$choice" -lt 1 ] || [ "$choice" -gt $(( ${#DATA_SUBDIRS[@]} + 1 )) ]; then
    print_error "Invalid choice"
    exit 1
fi

# Determine which directories to process
if [ "$choice" -eq $(( ${#DATA_SUBDIRS[@]} + 1 )) ]; then
    # Process all directories
    SELECTED_DIRS=("${DATA_SUBDIRS[@]}")
    print_status "Selected all data directories"
else
    # Process single directory
    SELECTED_DIRS=("${DATA_SUBDIRS[$((choice-1))]}")
    dirname=$(basename "${SELECTED_DIRS[0]}")
    print_status "Selected directory: $dirname"
fi

echo ""

# Step 5: Check Nebula Graph connection
print_status "Step 5: Checking Nebula Graph connection..."
print_warning "Please ensure Nebula Graph is running and accessible"
print_warning "The ingestion process will automatically setup the schema from the ontology"
echo ""

read -p "Press Enter when Nebula Graph is ready, or Ctrl+C to cancel..."

# Step 6: Run ingestion for selected directories
print_status "Step 6: Running POI ingestion..."

for data_dir in "${SELECTED_DIRS[@]}"; do
    dirname=$(basename "$data_dir")
    print_status "Ingesting data from: $dirname"
    
    # Check if directory contains JSON files
    json_files=$(find "$data_dir" -name "*.json" | wc -l)
    if [ "$json_files" -eq 0 ]; then
        print_warning "No JSON files found in $dirname, skipping..."
        continue
    fi
    
    # Run ingestion
    python3 poi_ingestor.py --data-dir "$data_dir" --config "$CONFIG_FILE"
    
    if [ $? -eq 0 ]; then
        print_status "Successfully ingested data from $dirname"
    else
        print_error "Failed to ingest data from $dirname"
    fi
    
    echo ""
done

print_status "POI ingestion workflow completed!"
echo ""
print_status "You can now query your POI data in Nebula Graph:"
echo "  MATCH (p:POI) RETURN p LIMIT 10;"
echo "  MATCH (p:POI) WHERE p.category == \"museums\" RETURN p;"
echo "  MATCH (p:POI)-[r:IS_OF_TYPE]->(t:POI_TYPE) RETURN p.name, t.name, r.confidence LIMIT 10;"
