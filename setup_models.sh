#!/bin/bash

# Setup script for LLM Benchmarker
# Creates necessary directories and prepares environment

echo "Setting up LLM Benchmarker..."

# Create models directory
mkdir -p models
echo "✓ Created models directory"

# Create results directory
mkdir -p results
echo "✓ Created results directory"

# Create logs directory
mkdir -p logs
echo "✓ Created logs directory"

# Set HuggingFace cache directory
export HF_HOME="$(pwd)/models"
export TRANSFORMERS_CACHE="$(pwd)/models"
echo "✓ Set HuggingFace cache to: $(pwd)/models"

# Create .env file for persistence
cat > .env << EOF
HF_HOME=$(pwd)/models
TRANSFORMERS_CACHE=$(pwd)/models
EOF
echo "✓ Created .env file"

# Install Python dependencies if not already installed
echo ""
echo "Checking Python dependencies..."
pip install -r requirements.txt --quiet
echo "✓ Dependencies installed"

echo ""
echo "Setup complete! You can now run:"
echo "  - python benchmark_ambiguity.py"
echo "  - python benchmark_nlq_sql_pipeline.py"
echo ""
echo "Or use the benchmark script: ./benchmark.sh"
