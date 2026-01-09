#!/bin/bash
# Main benchmark runner - Automated for all models in models.txt

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$SCRIPT_DIR/logs"
RESULTS_DIR="$SCRIPT_DIR/results"
MODELS_FILE="$SCRIPT_DIR/models.txt"

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
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Detect Python from conda environment
PYTHON_CMD="python3"
if [ -n "$CONDA_PREFIX" ]; then
    # Running in a conda environment
    PYTHON_CMD="$CONDA_PREFIX/bin/python"
    if [ ! -f "$PYTHON_CMD" ]; then
        # Fallback for Windows conda environments
        PYTHON_CMD="$CONDA_PREFIX/python.exe"
    fi
elif [ -n "$CONDA_DEFAULT_ENV" ]; then
    # Conda is active but try to locate it
    if command -v conda &> /dev/null; then
        CONDA_PREFIX=$(conda info --json | grep -o '"conda_prefix": "[^"]*' | cut -d'"' -f4)
        if [ -n "$CONDA_PREFIX" ] && [ -f "$CONDA_PREFIX/bin/python" ]; then
            PYTHON_CMD="$CONDA_PREFIX/bin/python"
        fi
    fi
fi

echo -e "${GREEN}========================================${NC}" | tee -a "$LOG_FILE"
echo -e "${GREEN}LLM Benchmark Runner - Automated${NC}" | tee -a "$LOG_FILE"
echo -e "${GREEN}========================================${NC}" | tee -a "$LOG_FILE"
echo "Timestamp: $TIMESTAMP" | tee -a "$LOG_FILE"
echo "Log file: $LOG_FILE" | tee -a "$LOG_FILE"

# Check models.txt exists
if [ ! -f "$MODELS_FILE" ]; then
    echo -e "${RED}ERROR: models.txt not found${NC}" | tee -a "$LOG_FILE"
    echo "Create models.txt with one model per line" | tee -a "$LOG_FILE"
    exit 1
fi

# Check Python
if ! command -v "$PYTHON_CMD" &> /dev/null && [ ! -f "$PYTHON_CMD" ]; then
    echo -e "${RED}ERROR: Python not found at: $PYTHON_CMD${NC}" | tee -a "$LOG_FILE"
    echo -e "${YELLOW}Please activate a conda environment and try again${NC}" | tee -a "$LOG_FILE"
    exit 1
fi

echo -e "${GREEN}✓ Python found: $PYTHON_CMD${NC}" | tee -a "$LOG_FILE"

# Check dependencies
echo "Checking dependencies..." | tee -a "$LOG_FILE"
"$PYTHON_CMD" -c "import torch, transformers, pandas" 2>/dev/null && \
    echo -e "${GREEN}✓ All dependencies available${NC}" | tee -a "$LOG_FILE" || \
    { echo -e "${YELLOW}Installing dependencies...${NC}" | tee -a "$LOG_FILE"; pip install -r requirements.txt 2>&1 | tee -a "$LOG_FILE"; }

# Read models from models.txt
MODELS=()
while IFS= read -r line; do
    # Skip empty lines and comments
    [[ -z "$line" || "$line" =~ ^#.*$ ]] && continue
    MODELS+=("$line")
done < "$MODELS_FILE"

if [ ${#MODELS[@]} -eq 0 ]; then
    echo -e "${RED}ERROR: No models found in models.txt${NC}" | tee -a "$LOG_FILE"
    exit 1
fi

echo -e "${BLUE}Found ${#MODELS[@]} model(s) to benchmark${NC}" | tee -a "$LOG_FILE"
for model in "${MODELS[@]}"; do
    echo "  - $model" | tee -a "$LOG_FILE"
done
echo "" | tee -a "$LOG_FILE"

# Run benchmark for each model
TOTAL_MODELS=${#MODELS[@]}
CURRENT_MODEL=0

for model in "${MODELS[@]}"; do
    CURRENT_MODEL=$((CURRENT_MODEL + 1))
    echo -e "${BLUE}========================================${NC}" | tee -a "$LOG_FILE"
    echo -e "${BLUE}[$CURRENT_MODEL/$TOTAL_MODELS] Benchmarking: $model${NC}" | tee -a "$LOG_FILE"
    echo -e "${BLUE}========================================${NC}" | tee -a "$LOG_FILE"
    
    "$PYTHON_CMD" "$SCRIPT_DIR/run_benchmark.py" --model "$model" 2>&1 | tee -a "$LOG_FILE"
    
    if [ ${PIPESTATUS[0]} -ne 0 ]; then
        echo -e "${RED}✗ Failed for $model${NC}" | tee -a "$LOG_FILE"
    else
        echo -e "${GREEN}✓ Completed for $model${NC}" | tee -a "$LOG_FILE"
    fi
    echo "" | tee -a "$LOG_FILE"
done

echo -e "${GREEN}========================================${NC}" | tee -a "$LOG_FILE"
echo -e "${GREEN}✓ All benchmarks completed${NC}" | tee -a "$LOG_FILE"
echo -e "${GREEN}========================================${NC}" | tee -a "$LOG_FILE"
echo -e "${GREEN}Results saved to: $RESULTS_DIR${NC}" | tee -a "$LOG_FILE"
echo -e "${GREEN}Logs saved to: $LOG_FILE${NC}" | tee -a "$LOG_FILE"
