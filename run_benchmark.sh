#!/bin/bash
# Main benchmark runner script
# Usage: ./run_benchmark.sh [model_id] [task]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$SCRIPT_DIR/logs"
RESULTS_DIR="$SCRIPT_DIR/results"

# Create directories
mkdir -p "$LOG_DIR"
mkdir -p "$RESULTS_DIR"
mkdir -p "$SCRIPT_DIR/models"

# Timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="$LOG_DIR/benchmark_$TIMESTAMP.log"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}LLM Benchmark Runner${NC}"
echo -e "${GREEN}========================================${NC}"
echo "Timestamp: $TIMESTAMP" | tee -a "$LOG_FILE"
echo "Log file: $LOG_FILE" | tee -a "$LOG_FILE"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}ERROR: Python3 not found${NC}" | tee -a "$LOG_FILE"
    exit 1
fi

echo -e "${GREEN}✓ Python3 found${NC}" | tee -a "$LOG_FILE"

# Check required Python packages
echo "Checking dependencies..." | tee -a "$LOG_FILE"
python3 -c "import torch, transformers, pandas" 2>/dev/null && \
    echo -e "${GREEN}✓ All dependencies available${NC}" | tee -a "$LOG_FILE" || \
    { echo -e "${YELLOW}Installing dependencies...${NC}"; pip install -r requirements.txt 2>&1 | tee -a "$LOG_FILE"; }

# Run benchmark
echo -e "${YELLOW}Starting benchmark...${NC}" | tee -a "$LOG_FILE"
python3 "$SCRIPT_DIR/run_benchmark.py" 2>&1 | tee -a "$LOG_FILE"

STATUS=$?

if [ $STATUS -eq 0 ]; then
    echo -e "${GREEN}Benchmark completed successfully${NC}" | tee -a "$LOG_FILE"
else
    echo -e "${RED}Benchmark failed with status $STATUS${NC}" | tee -a "$LOG_FILE"
fi

echo -e "${GREEN}Results saved to: $RESULTS_DIR${NC}" | tee -a "$LOG_FILE"
exit $STATUS
