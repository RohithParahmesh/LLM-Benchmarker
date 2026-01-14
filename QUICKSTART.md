# LLM Benchmarker - Quick Start Guide

## System Overview

Three-agent system for NL→SQL processing:

1. **AmbiguityAgent** - Detects ambiguity in user queries (runs independently)
2. **NLQAgent** - Refines natural language queries for clarity
3. **SQLAgent** - Generates SQL from refined queries

### Processing Flows

```
Independent:
User Query → AmbiguityAgent → Classification (Ambiguous/Clear)

Pipeline:
User Query → NLQAgent → Refined Query → SQLAgent → SQL Query
```

---

## Running Benchmarks

### 1. Benchmark AmbiguityAgent (Independent)

```bash
python benchmark_ambiguity.py
```

**What it does:**
- Loads queries from `test_data/ambiguity_intent.csv`
- Processes each query through AmbiguityAgent
- Classifies as Ambiguous or Clear
- Saves results to `results/ambiguity_benchmark_*.json`

**Time:** ~5-10 seconds per query (depends on model size)

### 2. Benchmark NLQ→SQL Pipeline (Chained)

```bash
python benchmark_nlq_sql_pipeline.py
```

**What it does:**
- Loads query pairs from `test_data/nl_to_sql.csv`
- Stage 1: NLQAgent refines each query
- Stage 2: SQLAgent generates SQL from refined query
- Saves results to `results/nlq_sql_pipeline_*.json`

**Time:** ~10-20 seconds per query (both stages)

---

## Using Custom Instructions

All agents support custom instructions from the registry:

```python
from utils import NLQAgent, SQLAgent, AmbiguityAgent, NLQSQLPipeline

# Initialize agents
nlq_agent = NLQAgent(model_id="TinyLlama/TinyLlama-1.1B-Chat-v1.0")
sql_agent = SQLAgent(model_id="TinyLlama/TinyLlama-1.1B-Chat-v1.0")

# Use with custom instructions
pipeline = NLQSQLPipeline(nlq_agent, sql_agent)
result = pipeline.execute(
    "Get all P2P transactions in 2024",
    nlq_instruction_key="nlq_refinement",    # Uses custom prompt from prompts.ipynb
    sql_instruction_key="sql_generation"     # Uses custom prompt from prompts.ipynb
)

# Access results
print("Original:", result["original_query"])
print("Refined:", result["refined_query"])
print("SQL:", result["sql"])
```

### Available Instructions

- `nlq_refinement` - Custom NLQ refinement prompt (from prompts.ipynb)
- `sql_generation` - Custom SQL generation prompt (from prompts.ipynb)
- `ambiguity_detection` - Custom ambiguity detection prompt (from prompts.ipynb)

---

## Understanding Results

### Ambiguity Benchmark Results

File: `results/ambiguity_benchmark_*.json`

```json
{
  "model": "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
  "task": "ambiguity_detection",
  "total_queries": 10,
  "total_time": 45.23,
  "avg_time_per_query": 4.52,
  "results": [
    {
      "input": "Get users",
      "classification": "Ambiguous",
      "processing_time": 4.52,
      "full_response": "This query is ambiguous because..."
    }
  ]
}
```

**Key Metrics:**
- **total_time**: Total execution time in seconds
- **avg_time_per_query**: Average processing time per query
- **classification**: "Ambiguous" or "Clear"

**How to Interpret:**
- Queries with "Ambiguous" classification contain unclear references, missing context, or multiple interpretations
- Queries with "Clear" classification have specific, well-defined requirements
- Use ambiguity scores to prioritize clarification efforts
- Processing time indicates model efficiency (lower is better)

**Example Analysis:**
```
If 70% classified as Ambiguous:
  → User queries need refinement guidance
  → Consider adding clarification prompts upfront

If 30% classified as Ambiguous:
  → Most queries are specific enough
  → Focus on other quality metrics
```

---

### Pipeline Benchmark Results

File: `results/nlq_sql_pipeline_*.json`

```json
{
  "model": "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
  "task": "nlq_to_sql_pipeline",
  "total_queries": 10,
  "total_time": 89.45,
  "avg_time_per_query": 8.95,
  "results": [
    {
      "original_query": "Get all users",
      "refined_query": "Get all active user records from the database",
      "sql": "SELECT * FROM users WHERE status = 'active'",
      "expected_sql": "SELECT * FROM users WHERE active = 1",
      "processing_time": 8.95,
      "stages": {
        "nlq": {
          "input": "Get all users",
          "refined_query": "Get all active user records from the database",
          "processing_time": 4.20
        },
        "sql": {
          "input": "Get all active user records from the database",
          "sql": "SELECT * FROM users WHERE status = 'active'",
          "processing_time": 4.75
        }
      }
    }
  ]
}
```

**Key Metrics:**
- **total_time**: Total end-to-end pipeline time
- **avg_time_per_query**: Average time per query through both stages
- **refined_query**: Output from NLQAgent (query refinement)
- **sql**: Final output from SQLAgent
- **expected_sql**: Reference SQL for comparison

**Stage Breakdown:**
- **NLQ Stage**: Time to refine query (~40% of total)
- **SQL Stage**: Time to generate SQL (~60% of total)

**How to Interpret:**

1. **Refinement Quality:**
   ```
   Original: "Get users"
   Refined:  "Get all active user records from the database"
   
   ✓ Good - More specific and contextual
   ✗ Bad - Same as original or less specific
   ```

2. **SQL Accuracy:**
   - Compare `sql` with `expected_sql`
   - Exact match = Perfect
   - Semantically similar = Good
   - Different logic = Needs improvement

3. **Processing Time Distribution:**
   ```
   If NLQ takes 7s, SQL takes 3s:
     → Refinement is more resource-intensive
     → Consider optimizing prompts
   
   If both take ~5s:
     → Balanced pipeline
     → Good for production use
   ```

4. **Performance Metrics:**
   ```
   Avg time < 5s per query:
     → Fast for interactive use
   
   Avg time 5-10s per query:
     → Moderate, suitable for batch processing
   
   Avg time > 10s per query:
     → Slow, consider smaller models or optimization
   ```

---

## Comparing Results

### Between Different Models

```bash
# Run with different models
python benchmark_nlq_sql_pipeline.py  # Uses default (TinyLlama)
# Edit the script to use different model_id and run again
```

**Compare metrics:**
- Processing time (speed)
- SQL accuracy (quality)
- Refinement clarity (quality)

### Before/After Custom Instructions

**Without custom instructions:**
```python
result = pipeline.execute("Get all P2P transactions")
```

**With custom instructions:**
```python
result = pipeline.execute(
    "Get all P2P transactions",
    nlq_instruction_key="nlq_refinement",
    sql_instruction_key="sql_generation"
)
```

Compare:
- Refinement specificity
- SQL syntax correctness
- Processing time

---

## Common Performance Issues

### Issue: Slow Processing (>15s per query)

**Causes:**
- Model too large for GPU
- GPU not available (using CPU)
- Too many tokens in prompt

**Solutions:**
```python
# Use smaller model
agent = NLQAgent(model_id="TinyLlama/TinyLlama-1.1B-Chat-v1.0")

# Check device
agent = NLQAgent(model_id="...", device="cuda")  # Force GPU
```

### Issue: Low Quality SQL

**Causes:**
- Prompts not specific enough
- Model too small
- Missing context

**Solutions:**
1. Use custom instructions from `prompts.ipynb`
2. Use larger model (Llama-2-7b)
3. Add more context in pipeline

### Issue: High Ambiguity Detection

**Causes:**
- User queries lacking detail
- Missing schema context
- Unclear business requirements

**Solutions:**
1. Improve input queries
2. Add system context to NLQAgent
3. Use clarification prompts

---

## Project Structure

```
LLM-Benchmarker/
├── utils/
│   ├── three_agents.py          # BaseAgent, NLQAgent, SQLAgent, AmbiguityAgent
│   ├── nlq_sql_pipeline.py      # NLQSQLPipeline, AmbiguityPipeline
│   ├── custom_instructions.py   # CustomInstruction registry with your prompts
│   └── __init__.py              # Module exports
├── benchmark_ambiguity.py        # Run independent ambiguity detection
├── benchmark_nlq_sql_pipeline.py # Run chained NLQ→SQL pipeline
├── test_data/
│   ├── ambiguity_intent.csv     # Test queries for ambiguity detection
│   └── nl_to_sql.csv            # Test query pairs for pipeline
├── results/                      # Benchmark results (JSON)
├── models/                       # Cached models directory
├── prompts.ipynb               # Original prompts notebook
├── requirements.txt             # Dependencies
└── models.txt                  # Model listing
```

---

## Next Steps

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run ambiguity benchmark:**
   ```bash
   python benchmark_ambiguity.py
   ```

3. **Run pipeline benchmark:**
   ```bash
   python benchmark_nlq_sql_pipeline.py
   ```

4. **Analyze results:**
   - Open JSON files in `results/`
   - Compare metrics across queries
   - Identify patterns

5. **Iterate on prompts:**
   - Edit custom instructions in `utils/custom_instructions.py`
   - Re-run benchmarks
   - Compare results

---

## Tips

- **Test locally first:** Use small test datasets before running on all data
- **Save results:** Benchmark outputs are timestamped JSON files in `results/`
- **Compare models:** Run same benchmark with different models to see performance trade-offs
- **Use custom instructions:** Your prompts from `prompts.ipynb` are ready to use
- **Monitor GPU:** Use `nvidia-smi` to check GPU usage during runs

