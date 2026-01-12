#!/bin/bash

# Benchmark runner wrapper for conda environments
# This ensures the conda environment is properly activated before running benchmarks

set -e

# Configuration
CONDA_ENV_NAME="llms"  # Change this to your conda env name if different

# Activate conda
if command -v conda &> /dev/null; then
    eval "$(conda shell.bash hook)"
    if conda env list | grep -q "$CONDA_ENV_NAME"; then
        conda activate "$CONDA_ENV_NAME"
        echo "✓ Activated conda environment: $CONDA_ENV_NAME"
    else
        echo "⚠ Conda environment '$CONDA_ENV_NAME' not found. Using current environment."
    fi
else
    echo "⚠ Conda not found. Make sure you have activated the correct Python environment."
fi

# Verify Python is from the right environment
echo "Using Python from: $(which python)"
python --version

# Run the benchmark
echo ""
echo "Starting benchmark..."
python run_benchmark.py "$@"
