# Setup Complete - Automated Benchmarking System

## What You Have

✅ **Fully Automated** - One command runs all benchmarks  
✅ **Model List in File** - Edit `models.txt` to change models  
✅ **CSV Test Data** - Edit test_data/*.csv for test cases  
✅ **Agent-Based** - Benchmark your custom agents, not just LLMs  
✅ **Minimal Setup** - Only 3 Python files, 1 bash script  

## File Structure

```
LLM-Benchmarker/
├── benchmark.sh                  # Run all benchmarks
├── run_benchmark.py              # Main runner
├── models.txt                    # Model list (YOU EDIT THIS)
│
├── utils/
│   ├── agent.py                 # BaseAgent + built-in agents
│   └── agent_template.py         # Copy to create your agent
│
├── test_data/
│   ├── nl_to_sql.csv            # NL→SQL tests (YOU EDIT THIS)
│   ├── ambiguity_intent.csv     # Ambiguity tests (YOU EDIT THIS)
│   └── (your custom tests)
│
├── results/                      # Generated JSON results
├── logs/                         # Generated logs
├── models/                       # Downloaded models cache
└── QUICKSTART.md                 # Getting started guide
```

## Only 3 Things to Change

### 1. models.txt - Your Model List

```
# HuggingFace models to benchmark
meta-llama/Llama-2-7b
meta-llama/Llama-2-13b
microsoft/phi-2
```

### 2. test_data/nl_to_sql.csv - Your Test Cases

```csv
input,expected_output
"Get all users","SELECT * FROM users"
"Count orders","SELECT COUNT(*) FROM orders"
```

### 3. (Optional) Create Custom Agent

Copy `utils/agent_template.py`, implement `execute()`, register it.

## How to Run

### Automated (All Models in models.txt)
```bash
bash benchmark.sh
```

The script will:
- Read all models from models.txt
- For each model:
  - Download it
  - Setup inference engine
  - Create agents
  - Run all test_data/*.csv tests
  - Save results
  - Cleanup
  - Move to next model

### Single Model
```bash
python3 run_benchmark.py --model meta-llama/Llama-2-7b
```

### Custom Tasks
```bash
python3 run_benchmark.py --model meta-llama/Llama-2-7b --tasks nl_to_sql,my_task
```

## Benchmark Workflow

For each model in models.txt:
```
1. Download model from HuggingFace
   ↓
2. Setup inference engine (GPU/CPU)
   ↓
3. Create agent for each task
   ↓
4. Run all test cases from CSV
   ↓
5. Save results to JSON
   ↓
6. Cleanup memory
   ↓
7. Next model (repeat)
```

## Results

Each run creates JSON files in `results/`:
```json
{
  "model": "meta-llama/Llama-2-7b",
  "task": "nl_to_sql",
  "total": 5,
  "passed": 4,
  "failed": 1,
  "results": [
    {
      "index": 0,
      "input": "Get all users",
      "expected": "SELECT * FROM users",
      "output": "SELECT * FROM users",
      "time": 2.34,
      "passed": true
    }
  ]
}
```

## Quick Example

### Step 1: Edit models.txt
```
meta-llama/Llama-2-7b
```

### Step 2: Edit test_data/nl_to_sql.csv
```csv
input,expected_output
"List customers","SELECT * FROM customers"
"Count orders","SELECT COUNT(*) FROM orders"
```

### Step 3: Run
```bash
bash benchmark.sh
```

### Step 4: Check results
```bash
cat results/nl_to_sql_meta-llama_Llama-2-7b_*.json
```

## Built-in Agents

- **NLToSQLAgent** - Converts natural language to SQL
- **AmbiguityDetectionAgent** - Detects ambiguous queries

See `utils/agent.py` for implementations.

## Create Custom Agent

1. Copy `utils/agent_template.py` to `utils/my_agent.py`
2. Modify `execute()` method
3. In `run_benchmark.py`, import and register:
   ```python
   from utils.my_agent import MyCustomAgent
   register_agent("my_task", MyCustomAgent)
   ```
4. Create `test_data/my_task.csv`
5. Run: `bash benchmark.sh`

## That's It!

Everything is automated. Just:
1. Edit `models.txt` with your models
2. Edit `test_data/*.csv` with your test cases
3. Run `bash benchmark.sh`

All benchmarking, logging, result saving is automatic.

See QUICKSTART.md for more details.
