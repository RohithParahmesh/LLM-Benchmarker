#!/bin/bash
# Quick benchmark runner for single model/task
# Usage: ./quick_benchmark.sh "meta-llama/Llama-2-7b" "nl_to_sql"

MODEL_ID="${1:-meta-llama/Llama-2-7b}"
TASK="${2:-nl_to_sql}"

echo "Quick Benchmark: $MODEL_ID - $TASK"
python3 << EOF
import sys
sys.path.insert(0, '.')
from run_benchmark import SimpleBenchmark, load_test_data, save_results

benchmark = SimpleBenchmark()

# Step 1: Download
if not benchmark.download_model("$MODEL_ID"):
    print("Failed to download model")
    sys.exit(1)

# Step 2: Setup
if not benchmark.setup_inference_engine():
    print("Failed to setup engine")
    sys.exit(1)

# Step 3: Create agent
agent = benchmark.create_agent("$TASK")

# Step 4: Load and run tests
test_data = load_test_data("test_data/$TASK.csv")
results = benchmark.run_tests(agent, test_data)

# Save results
save_results(results, "$MODEL_ID", "$TASK")

# Step 5: Cleanup
benchmark.cleanup()

print(f"Passed: {results['passed']}/{results['total']}")
EOF
