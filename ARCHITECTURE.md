# LLM Benchmarker - Simplified Architecture

## Clean Project Structure

```
LLM-Benchmarker/
├── run_benchmark.py          # Main benchmark runner
├── quick_benchmark.sh         # Quick test script
├── run_benchmark.sh          # Full benchmark script
│
├── utils/
│   ├── agent.py              # BaseAgent class + built-in examples
│   └── agent_template.py      # Template to copy for custom agents
│
├── test_data/
│   ├── nl_to_sql.csv         # NL→SQL test cases
│   └── ambiguity_intent.csv  # Ambiguity detection test cases
│
├── results/                  # Generated benchmark results
│   └── *.json
│
├── models/                   # Downloaded model cache
│   └── (auto-managed)
│
├── AGENT_GUIDE.md           # Complete guide for custom agents
└── README.md                # Original project docs
```

## What Was Removed

- `model_downloader.py` → Integrated into main script
- `inference_engine.py` → Simplified into main script
- `agent_factory.py` → Replaced with agent registry in main script
- `test_runner.py` → Simplified into main script
- `benchmark_orchestrator.py` → Simplified into main script

## Why This Works Better

✅ **Single file runner** - Everything in one place  
✅ **Agent-focused** - Benchmark YOUR agent, not just the LLM  
✅ **CSV/Excel input** - Easy to manage test data  
✅ **Extensible** - Create custom agents easily  
✅ **No complexity** - ~300 lines of Python total  

## Quick Reference

### Create Custom Agent
1. Copy `utils/agent_template.py` to `utils/my_agent.py`
2. Modify `execute()` method with your logic
3. Create `test_data/my_task.csv` with test cases
4. Import and register in `run_benchmark.py`
5. Run: `python3 run_benchmark.py`

### Run Benchmark
```bash
# Full run
python3 run_benchmark.py

# Or with bash
bash run_benchmark.sh
```

### Test Data Format
```csv
input,expected_output
"question 1","answer 1"
"question 2","answer 2"
```

## Benchmark Flow

For each model:
```
1. Download model
   ↓
2. Setup inference engine
   ↓
3. Create your agent
   ↓
4. Run tests from CSV
   ↓
5. Save JSON results
   ↓
6. Cleanup memory
   ↓
7. Next model (repeat)
```

## Key Files

- **run_benchmark.py** - Main entry point
- **utils/agent.py** - BaseAgent class, inherit from this
- **AGENT_GUIDE.md** - Complete guide for custom agents

## Start Here

1. Read [AGENT_GUIDE.md](./AGENT_GUIDE.md)
2. Copy `utils/agent_template.py` to create your agent
3. Create test data CSV
4. Register in `run_benchmark.py`
5. Run!
