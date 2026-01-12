#!/bin/bash

# Script to download and setup models for benchmarking
# Reads model IDs from models.txt and downloads them using huggingface-hub

set -e  # Exit on any error

# Activate conda environment if available
CONDA_ENV_NAME="llms"  # Change this to your conda env name if different
if command -v conda &> /dev/null; then
    eval "$(conda shell.bash hook)"
    if conda env list | grep -q "$CONDA_ENV_NAME"; then
        conda activate "$CONDA_ENV_NAME"
        echo "Activated conda environment: $CONDA_ENV_NAME"
    fi
fi

MODELS_FILE="models.txt"
MODELS_DIR="./models"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if models.txt exists
if [ ! -f "$MODELS_FILE" ]; then
    echo -e "${RED}Error: $MODELS_FILE not found!${NC}"
    exit 1
fi

# Create models directory if it doesn't exist
mkdir -p "$MODELS_DIR"

echo -e "${YELLOW}Starting model setup...${NC}"
echo "Models directory: $MODELS_DIR"
echo ""

# Read models.txt and download each model
model_count=0
while IFS= read -r model_id; do
    # Skip empty lines and comments
    if [ -z "$model_id" ] || [[ "$model_id" =~ ^[[:space:]]*# ]]; then
        continue
    fi
    
    # Trim whitespace
    model_id=$(echo "$model_id" | xargs)
    
    echo -e "${YELLOW}Processing: $model_id${NC}"
    
    # Use Python to download the model using huggingface_hub
    python << EOF
import os
from huggingface_hub import snapshot_download
from transformers import AutoTokenizer, AutoModelForCausalLM

model_id = "$model_id"
models_dir = "$MODELS_DIR"

try:
    print(f"  Downloading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    print(f"  Tokenizer saved")
    
    print(f"  Downloading model (this may take a while)...")
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype="auto",
        device_map="auto",
        trust_remote_code=True
    )
    print(f"  Model downloaded successfully")
    
    print(f"  Caching model locally...")
    snapshot_download(repo_id=model_id, cache_dir=models_dir)
    
except Exception as e:
    print(f"  Error downloading {model_id}: {str(e)}")
    exit(1)
EOF
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Successfully setup: $model_id${NC}"
        ((model_count++))
    else
        echo -e "${RED}✗ Failed to setup: $model_id${NC}"
    fi
    echo ""
    
done < "$MODELS_FILE"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Setup complete! Processed $model_count model(s)${NC}"
echo -e "${GREEN}Models cached in: $MODELS_DIR${NC}"
echo -e "${GREEN}========================================${NC}"
