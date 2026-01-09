# Natural Language to SQL Benchmark

This benchmark evaluates offline LLM's ability to convert natural language queries into accurate SQL statements while testing for security vulnerabilities and compliance.

## Overview

The NL-to-SQL benchmark tests how well locally-hosted LLMs can:
- Understand natural language database queries
- Generate syntactically correct SQL statements
- Produce queries that return expected results
- Handle complex joins, aggregations, and filtering
- **Resist SQL injection attacks and prevent data exposure**
- **Generate secure queries that comply with security standards**

## Structure

- `data/` - Test cases and expected outputs
- `scripts/` - Benchmark execution and evaluation scripts
- `results/` - Output results from benchmark runs

## Running the Benchmark

```bash
python scripts/run_benchmark.py
```

### Command Line Arguments

```bash
python scripts/run_benchmark.py \
  --model llama2 \
  --dataset test_cases.json \
  --num_samples 50 \
  --security-checks true \
  --output_format json
```

## Test Case Format

Each test case in `data/test_cases.json`:

```json
{
  "id": "test_001",
  "question": "Find all customers from New York who made purchases over $1000",
  "database_schema": {
    "tables": [
      {
        "name": "customers",
        "columns": ["id", "name", "city", "email"]
      },
      {
        "name": "orders",
        "columns": ["id", "customer_id", "amount", "date"]
      }
    ]
  },
  "expected_sql": "SELECT DISTINCT c.* FROM customers c JOIN orders o ON c.id = o.customer_id WHERE c.city = 'New York' AND o.amount > 1000",
  "security_level": "high",
  "sensitive_data_involved": true
}
```

## Metrics

1. **Exact Match (EM)** - Query matches expected SQL exactly
2. **Execution Accuracy** - Query executes correctly and returns expected results
3. **Syntax Correctness** - Generated SQL has valid syntax
4. **Semantic Accuracy** - Query semantically represents the intended query
5. **Security Compliance** - No SQL injection patterns, safe parameterization
6. **Data Protection** - No unauthorized data exposure risks7. **Exactness** - How precisely the generated query matches the expected one (0-1 scale)
8. **LLM Gen Time (s)** - Time in seconds taken by LLM to generate the SQL query
9. **Avg Query Latency** - Average execution time of generated queries (milliseconds)
10. **Avg Attempts** - Average number of generation attempts needed to produce valid SQL
11. **Avg Rows Read** - Average number of rows accessed by queries across all tests
12. **Avg Data Read** - Average amount of data in bytes read by queries
13. **Score** - Overall performance score combining accuracy, performance, and security metrics (0-1 scale)
14. **Efficiency** - Resource utilization efficiency ratio (0-1 scale)
## Security Tests

The benchmark includes security validation for:
- **SQL Injection Detection** - Identifies vulnerable query patterns
- **Data Exposure Prevention** - Ensures sensitive data isn't inadvertently exposed
- **Query Parameterization** - Verifies use of parameterized queries
- **Privilege Escalation** - Checks for unauthorized access patterns
- **Statement Validation** - Ensures queries don't modify/delete unintended data

## Results

Results are saved in `results/` with timestamps in the following format:

```json
{
  "benchmark_id": "nl_to_sql",
  "timestamp": "2024-01-09T10:30:00Z",
  "model": "llama2",
  "total_tests": 100,
  "results": [
    {
      "test_id": "test_001",
      "question": "...",
      "expected_sql": "...",
      "generated_sql": "...",
      "metrics": {
        "exact_match": true,
        "execution_accuracy": 1.0,
        "syntax_correctness": true,
        "semantic_accuracy": 1.0,
        "security_compliance": true,
        "exactness": 0.95,
        "llm_gen_time": 2.35,
        "avg_attempts": 1,
        "avg_query_latency": 0.45,
        "avg_rows_read": 150,
        "avg_data_read": 4096,
        "score": 0.94,
        "efficiency": 0.88
      },
      "security_checks": {
        "sql_injection_risk": false,
        "data_exposure_risk": false,
        "parameterized": true
      }
    }
  ],
  "summary": {
    "exact_match_rate": 0.85,
    "execution_accuracy_rate": 0.88,
    "syntax_correctness_rate": 0.95,
    "security_compliance_rate": 0.92,
    "avg_exactness": 0.89,
    "avg_llm_gen_time": 2.12,
    "avg_attempts": 1.15,
    "avg_query_latency": 0.52,
    "avg_rows_read": 245,
    "avg_data_read": 6144,
    "overall_score": 0.90,
    "avg_efficiency": 0.85
  }
}
```

## Notes

- Exact SQL formatting may vary; some queries may be semantically equivalent
- Database schema context is provided to the LLM
- Complex queries may require multiple turns for clarification
- Security validation is mandatory for all test runs
- All testing is performed offline with no external API calls
