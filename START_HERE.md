# START HERE

## Fully Automated LLM Benchmarking

Your benchmarking system is ready. Everything is automated - you only need to:

### 1. Add Models to Benchmark
Edit `models.txt`:
```
meta-llama/Llama-2-7b
meta-llama/Llama-2-13b
microsoft/phi-2
```

### 2. Add Test Cases
Edit CSV files in `test_data/`:

**test_data/nl_to_sql.csv:**
```csv
input,expected_output
"Get all customers","SELECT * FROM customers"
"Count orders","SELECT COUNT(*) FROM orders"
```

**test_data/ambiguity_intent.csv:**
```csv
input,expected_output
"Show me the data","Ambiguous - which data?"
"Generate report","Not ambiguous - clear task"
```

### 3. Run Everything
```bash
bash benchmark.sh
```

That's it! The script will:
- Read all models from models.txt
- For each model:
  - Download it
  - Run all test cases
  - Save results
  - Cleanup

---

## What's Automated

✅ Download models from HuggingFace  
✅ Setup inference engine  
✅ Create agents  
✅ Run all test cases  
✅ Compare against expected outputs  
✅ Save results as JSON  
✅ Create logs  
✅ Cleanup memory  
✅ Move to next model  

**You don't touch any of this.**

---

## Only Edit These Files

1. **models.txt** - List of models
2. **test_data/nl_to_sql.csv** - NL→SQL test cases
3. **test_data/ambiguity_intent.csv** - Ambiguity test cases
4. (Optional) Create custom agent in utils/

---

## File Structure

```
LLM-Benchmarker/
├── benchmark.sh                # Run this
├── run_benchmark.py            # Main logic (don't touch)
├── models.txt                  # EDIT THIS
├── utils/
│   ├── agent.py               # Agent classes (don't touch)
│   └── agent_template.py       # Copy to create custom agent
├── test_data/
│   ├── nl_to_sql.csv          # EDIT THIS
│   └── ambiguity_intent.csv   # EDIT THIS
├── results/                    # Generated results
└── logs/                       # Generated logs
```

---

## Run Benchmark

### All Models (reads models.txt)
```bash
bash benchmark.sh
```

### Single Model
```bash
python3 run_benchmark.py --model meta-llama/Llama-2-7b
```

---

## Example Session

### 1. Edit models.txt
```bash
echo "meta-llama/Llama-2-7b" > models.txt
```

### 2. Edit test_data/nl_to_sql.csv
```csv
input,expected_output
"List customers","SELECT * FROM customers"
"Count orders","SELECT COUNT(*) FROM orders"
```

### 3. Run
```bash
bash benchmark.sh
```

### 4. Check Results
```bash
cat results/nl_to_sql_*.json
```

---

## Custom Agent (Optional)

To benchmark your own agent:

1. Copy `utils/agent_template.py` to `utils/my_agent.py`
2. Implement your logic in `execute()`
3. Create `test_data/my_task.csv`
4. Register in `run_benchmark.py`:
   ```python
   from utils.my_agent import MyAgent
   register_agent("my_task", MyAgent)
   ```
5. Run: `bash benchmark.sh`

---

## That's All You Need to Know

1. Edit models.txt
2. Edit test_data/*.csv
3. Run: bash benchmark.sh
4. Check results in results/

Everything else is automatic.
