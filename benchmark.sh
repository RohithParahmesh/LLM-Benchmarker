#!/bin/bash

# Benchmark script for LLM Benchmarker
# Runs both ambiguity detection and NLQ->SQL pipeline benchmarks

set -e

# Load environment variables
if [ -f .env ]; then
    set -a
    source .env
    set +a
fi

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}LLM Benchmarker${NC}"
echo -e "${GREEN}================================${NC}"
echo ""

# Check if directories exist
if [ ! -d "models" ]; then
    echo -e "${YELLOW}Warning: models directory not found${NC}"
    echo "Running setup first..."
    bash setup_models.sh
    echo ""
fi

if [ ! -d "results" ]; then
    mkdir -p results
    echo "Created results directory"
fi

if [ ! -d "logs" ]; then
    mkdir -p logs
    echo "Created logs directory"
fi

# Parse arguments
RUN_AMBIGUITY=true
RUN_PIPELINE=true
MODELS=("TinyLlama/TinyLlama-1.1B-Chat-v1.0")

while [[ $# -gt 0 ]]; do
    case $1 in
        --ambiguity-only)
            RUN_PIPELINE=false
            shift
            ;;
        --pipeline-only)
            RUN_AMBIGUITY=false
            shift
            ;;
        --model)
            MODELS=("$2")
            shift 2
            ;;
        --help)
            echo "Usage: ./benchmark.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --ambiguity-only    Run only ambiguity detection benchmark"
            echo "  --pipeline-only     Run only NLQ->SQL pipeline benchmark"
            echo "  --model MODEL_ID    Specify model (default: TinyLlama/TinyLlama-1.1B-Chat-v1.0)"
            echo "  --help              Show this help message"
            echo ""
            echo "Examples:"
            echo "  ./benchmark.sh                                    # Run both benchmarks"
            echo "  ./benchmark.sh --ambiguity-only                   # Run ambiguity benchmark only"
            echo "  ./benchmark.sh --model meta-llama/Llama-2-7b-chat # Use Llama-2 model"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Run benchmarks
START_TIME=$(date +%s)

if [ "$RUN_AMBIGUITY" = true ]; then
    echo -e "${YELLOW}Running Ambiguity Detection Benchmark...${NC}"
    python benchmark_ambiguity.py 2>&1 | tee logs/ambiguity_$(date +%Y%m%d_%H%M%S).log
    AMBIGUITY_EXIT=$?
    echo -e "${GREEN}✓ Ambiguity benchmark complete${NC}"
    echo ""
else
    AMBIGUITY_EXIT=0
fi

if [ "$RUN_PIPELINE" = true ]; then
    echo -e "${YELLOW}Running NLQ->SQL Pipeline Benchmark...${NC}"
    python benchmark_nlq_sql_pipeline.py 2>&1 | tee logs/pipeline_$(date +%Y%m%d_%H%M%S).log
    PIPELINE_EXIT=$?
    echo -e "${GREEN}✓ Pipeline benchmark complete${NC}"
    echo ""
else
    PIPELINE_EXIT=0
fi

# Summary
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}Benchmark Summary${NC}"
echo -e "${GREEN}================================${NC}"
echo "Duration: ${DURATION}s"
echo "Results saved to: results/"
echo "Logs saved to: logs/"
echo ""

if [ $AMBIGUITY_EXIT -eq 0 ] && [ $PIPELINE_EXIT -eq 0 ]; then
    echo -e "${GREEN}✓ All benchmarks completed successfully${NC}"
    exit 0
else
    echo -e "${RED}✗ One or more benchmarks failed${NC}"
    exit 1
fi
