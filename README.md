# LLM-Benchmarker

A comprehensive benchmarking and security testing suite for evaluating locally-hosted Large Language Models (LLMs) on two critical NLP tasks:
1. **Natural Language to SQL Query Translation** - Converts natural language questions into SQL queries
2. **Ambiguity and Intent Detection** - Identifies ambiguity in user queries and determines the intended meaning

## Overview

This repository contains tools and frameworks to systematically benchmark and evaluate **offline, locally-downloaded LLMs** for both functional accuracy and security purposes. The benchmarks download models via **HuggingFace Transformers**, test them comprehensively, and automatically clean up afterward. Each benchmark can be run independently to test specific capabilities without relying on external APIs or cloud-based services.

## Project Structure

```
LLM-Benchmarker/
├── README.md
├── requirements.txt
├── config/
│   ├── config.yaml
│   └── benchmark_config.json
├── benchmarks/
│   ├── nl_to_sql/
│   │   ├── README.md
│   │   ├── data/
│   │   │   ├── test_cases.json
│   │   │   └── expected_outputs.json
│   │   ├── scripts/
│   │   │   ├── run_benchmark.py
│   │   │   ├── evaluate.py
│   │   │   └── utils.py
│   │   └── results/
│   │       └── .gitkeep
│   ├── ambiguity_intent/
│   │   ├── README.md
│   │   ├── data/
│   │   │   ├── test_cases.json
│   │   │   └── expected_outputs.json
│   │   ├── scripts/
│   │   │   ├── run_benchmark.py
│   │   │   ├── evaluate.py
│   │   │   └── utils.py
│   │   └── results/
│   │       └── .gitkeep
└── utils/
    ├── llm_interface.py
    ├── metrics.py
    └── data_loader.py
```

## Benchmarks

### 1. Natural Language to SQL (NL-to-SQL)

Evaluates offline LLM's capability to convert natural language queries into accurate SQL statements while testing for security vulnerabilities (SQL injection patterns, data exposure risks, etc.).

**Use Cases:**
- Text-to-SQL question answering
- Database query generation from user input
- Intent understanding for database operations
- Security validation of SQL generation (no injection vulnerabilities)
- Data protection verification

**Key Metrics:**
- **Accuracy Metrics:**
  - Exact Match (EM) - Query matches expected SQL exactly
  - Execution Accuracy - Query executes correctly and returns expected results
  - Syntactic Correctness - Generated SQL has valid syntax
  - Exactness - How precisely the generated query matches the expected one

- **Performance Metrics:**
  - LLM Gen Time (s) - Time taken by LLM to generate the SQL query
  - Avg Query Latency - Average execution time of generated queries
  - Avg Attempts - Average number of generation attempts to produce valid SQL

- **Resource Metrics:**
  - Avg Rows Read - Average number of rows accessed by queries
  - Avg Data Read - Average amount of data (in bytes) read by queries
  - Score - Overall performance score combining all metrics
  - Efficiency - Resource utilization efficiency ratio

- **Security Metrics:**
  - Security Compliance - No SQL injection patterns detected
  - Data Protection Validation

### 2. Ambiguity and Intent Detection

Evaluates offline LLM's ability to identify ambiguous queries and determine the intended meaning, with security focus on preventing misinterpretation of potentially malicious queries.

**Use Cases:**
- Clarification request generation
- Intent disambiguation
- Confidence scoring for query understanding
- Security validation of intent detection (prevent prompt injection)
- Malicious intent detection capabilities

**Key Metrics:**
- Ambiguity Detection Rate - Correctly identifies ambiguous queries
- Intent Accuracy - Correctly infers the user's intended meaning
- Clarification Quality - Relevant questions asked to resolve ambiguity
- Security Alert Rate - Detects potentially malicious intent patterns

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd LLM-Benchmarker
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set HuggingFace token (optional, for gated models):
```bash
export HF_TOKEN=your_huggingface_token
# or configure in config/config.yaml
```

4. Configure model and benchmark settings in `config/config.yaml`

## Usage

### Run Individual Benchmarks

#### NL-to-SQL Benchmark
```bash
cd benchmarks/nl_to_sql
python scripts/run_benchmark.py --model llama2 --dataset test_cases.json
```

#### Ambiguity and Intent Benchmark
```bash
cd benchmarks/ambiguity_intent
python scripts/run_benchmark.py --model llama2 --dataset test_cases.json
```

### Run All Benchmarks
```bash
python run_all_benchmarks.py
```

### View Results
Results are saved in `benchmarks/<benchmark-name>/results/` directory as JSON files.

## Configuration

Edit `config/config.yaml` to:
- Set local model path and model type
- Configure benchmark parameters
- Set evaluation thresholds
- Define output formats
- Enable security validation checks
- Configure model inference settings (temperature, max tokens, etc.)

## Data Format

### Test Cases (JSON)
```json
[
  {
    "id": "test_001",
    "input": "Show me all customers from New York",
    "expected_output": "SELECT * FROM customers WHERE city = 'New York'",
    "metadata": {}
  }
]
```

### Results
```json
{
  "test_id": "test_001",
  "model": "llama2",
  "predicted_output": "SELECT * FROM customers WHERE city = 'New York'",
  "expected_output": "SELECT * FROM customers WHERE city = 'New York'",
  "metrics": {
    "exact_match": true,
    "execution_accuracy": 1.0,
    "llm_gen_time": 2.35,
    "avg_attempts": 1,
    "avg_query_latency": 0.45,
    "avg_rows_read": 150,
    "avg_data_read": 4096,
    "exactness": 0.95,
    "efficiency": 0.88,
    "score": 0.92
  }
}
```
torch (PyTorch)
- transformers (HuggingFace Transformers)
- pandas
- numpy
- json
- pyyaml

See `requirements.txt` for full list.

## Model Management

Models are automatically:
- **Downloaded** from HuggingFace on first use
- **Cached** in `./models/` directory during benchmarking
- **Cleaned up** after benchmark completion (configurable via `config.yaml`)

This approach allows testing multiple models without requiring manual download/setup for each one
- json
- pyyaml

See `requirements.txt` for full list.

## Security Features

- **No External API Calls** - All processing runs locally
- **Data Privacy** - No data sent to external services
- **Security Scanning** - Tests for SQL injection, prompt injection, and other vulnerabilities
- **Audit Logging** - Complete logging of all test runs and results
- **Model Validation** - Verifies model integrity and expected behavior

## Contributing

1. Create test cases in the appropriate `data/` directory
2. Update evaluation metrics if needed
3. Document any new benchmark cases

## License

MIT License

## Contact

For questions or issues, please open an issue in the repository.
