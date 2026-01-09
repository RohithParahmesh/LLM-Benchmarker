# LLM Benchmark - Quick Start

## Fully Automated Benchmarking

The entire system is automated. You only need to modify:
1. **models.txt** - List of models to benchmark
2. **test_data/*.csv** - Test cases and expected outputs

## Setup

### 1. Add Models to Benchmark

Edit `models.txt`:
```
# List of HuggingFace models to benchmark
meta-llama/Llama-2-7b
meta-llama/Llama-2-13b
microsoft/phi-2
```

Comments (starting with #) and empty lines are ignored.

### 2. Add Test Cases

Create CSV files in `test_data/`:

```csv
input,expected_output
"What is 2+2?","4"
"What is Paris?","The capital of France"
```

Built-in tasks:
- **nl_to_sql.csv** - Natural Language to SQL
- **ambiguity_intent.csv** - Ambiguity Detection

### 3. Create Custom Agent (Optional)

Create `utils/my_agent.py`:

```python
from utils.agent import BaseAgent
import torch

class MyAgent(BaseAgent):
    def execute(self, input_text: str) -> str:
        prompt = f"Your task: {input_text}\nResponse:"
        inputs = self.tokenizer.encode(prompt, return_tensors="pt").to(self.device)
        
        with torch.no_grad():
            outputs = self.model.generate(inputs, max_new_tokens=256)
        
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
```

Then in `run_benchmark.py`, add at the top:
```python
from utils.my_agent import MyAgent
register_agent("my_task", MyAgent)
```

And create `test_data/my_task.csv` with test cases.

## Run Benchmark

### Automated (All Models)
```bash
bash benchmark.sh
```

This runs all models in `models.txt` through all tasks.

### Single Model
```bash
python3 run_benchmark.py --model meta-llama/Llama-2-7b
```

### Custom Tasks
```bash
python3 run_benchmark.py --model meta-llama/Llama-2-7b --tasks nl_to_sql,ambiguity_intent,my_task
```

## Output

Results are saved to `results/` as JSON files:
```
results/
  nl_to_sql_meta-llama_Llama-2-7b_20260109_120000.json
  ambiguity_intent_meta-llama_Llama-2-7b_20260109_120000.json
```

Logs are saved to `logs/benchmark_*.log`

## Project Structure

```
LLM-Benchmarker/
├── benchmark.sh                  # Run all models (auto-reads models.txt)
├── run_benchmark.py              # Main runner
├── models.txt                    # Your model list (EDIT THIS)
│
├── utils/
│   ├── agent.py                 # Base agent + built-in examples
│   └── agent_template.py         # Template for custom agents
│
├── test_data/                    # Your test cases (EDIT THESE)
│   ├── nl_to_sql.csv
│   ├── ambiguity_intent.csv
│   └── my_task.csv              # Your custom tests
│
├── results/                      # Generated benchmarks
├── logs/                         # Generated logs
└── models/                       # Downloaded models cache
```

## Workflow

```
1. Edit models.txt with models to test
2. Edit test_data/*.csv with test cases
3. Optionally create custom agent in utils/
4. Run: bash benchmark.sh
5. Check results/ for JSON results
```

That's it! Everything else is automated.

## Example: NL-to-SQL Task

**models.txt:**
```
meta-llama/Llama-2-7b
meta-llama/Llama-2-13b
```

**test_data/nl_to_sql.csv:**
```csv
input,expected_output
"Get all customers","SELECT * FROM customers"
"Count orders from 2023","SELECT COUNT(*) FROM orders WHERE YEAR(date) = 2023"
```

**Run:**
```bash
bash benchmark.sh
```

That's it! The bash script will:
1. Read all models from models.txt
2. Download each model
3. Run nl_to_sql tests
4. Run ambiguity_intent tests
5. Save all results
6. Move to next model
