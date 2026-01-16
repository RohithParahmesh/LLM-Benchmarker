"""
Benchmark for NLQ→SQL Pipeline (NLQAgent → SQLAgent)
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict

from utils import NLQAgent, SQLAgent, NLQSQLPipeline
from utils.schema_context import get_schema_context


def load_queries(csv_path: str) -> List[Dict]:
    """Load queries from CSV with expected SQL"""
    import csv
    queries = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # Skip header
        for row in reader:
            if row and len(row) >= 2:
                queries.append({
                    "natural_language": row[0],
                    "expected_sql": row[1] if len(row) > 1 else ""
                })
    return queries


def benchmark_nlq_sql_pipeline(
    model_id: str = "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
    queries_file: str = "./test_data/nl_to_sql.csv",
    output_dir: str = "./results",
    nlq_instruction_key: str = None,
    sql_instruction_key: str = None
):
    """
    Benchmark NLQ→SQL Pipeline on test queries
    
    Args:
        model_id: HuggingFace model ID
        queries_file: Path to test queries CSV
        output_dir: Directory to save results
        nlq_instruction_key: Optional custom instruction for NLQ stage
        sql_instruction_key: Optional custom instruction for SQL stage
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("NLQ→SQL PIPELINE BENCHMARK")
    print("=" * 60)
    print(f"Model: {model_id}")
    print(f"Queries: {queries_file}")
    print(f"NLQ Instruction: {nlq_instruction_key or 'Default'}")
    print(f"SQL Instruction: {sql_instruction_key or 'Default'}")
    print()
    
    # Load queries
    query_pairs = load_queries(queries_file)
    print(f"Loaded {len(query_pairs)} query pairs")
    print()
    
    # Load schema context
    schema_context = get_schema_context()
    
    # Initialize agents
    nlq_agent = NLQAgent(model_id)
    sql_agent = SQLAgent(model_id)
    pipeline = NLQSQLPipeline(nlq_agent, sql_agent, schema_context=schema_context)
    
    # Process queries
    results = []
    start_time = time.time()
    
    for idx, pair in enumerate(query_pairs, 1):
        print(f"Processing [{idx}/{len(query_pairs)}]: {pair['natural_language'][:60]}...")
        
        stage_start = time.time()
        result = pipeline.execute(
            pair["natural_language"],
            nlq_instruction_key=nlq_instruction_key,
            sql_instruction_key=sql_instruction_key
        )
        stage_time = time.time() - stage_start
        
        result["expected_sql"] = pair.get("expected_sql", "")
        result["processing_time"] = stage_time
        results.append(result)
        
        print(f"  Refined: {result['refined_query'][:50]}...")
        print(f"  SQL: {result['sql'][:50]}...")
        print(f"  Time: {stage_time:.2f}s")
    
    total_time = time.time() - start_time
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = output_dir / f"nlq_sql_pipeline_{timestamp}.json"
    
    summary = {
        "model": model_id,
        "task": "nlq_to_sql_pipeline",
        "total_queries": len(query_pairs),
        "total_time": total_time,
        "avg_time_per_query": total_time / len(query_pairs),
        "nlq_instruction": nlq_instruction_key,
        "sql_instruction": sql_instruction_key,
        "timestamp": timestamp,
        "results": results
    }
    
    with open(results_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print()
    print("=" * 60)
    print("PIPELINE SUMMARY")
    print("=" * 60)
    print(f"Total queries processed: {len(query_pairs)}")
    print(f"Total time: {total_time:.2f}s")
    print(f"Average time per query: {total_time / len(query_pairs):.2f}s")
    print()
    print(f"Results saved to: {results_file}")
    print()


if __name__ == "__main__":
    benchmark_nlq_sql_pipeline()
