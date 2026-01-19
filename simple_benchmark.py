"""
Simple Benchmarking Script
Load queries → Execute pipeline → Compare with expected SQL → Save results
"""

import json
import csv
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict

from utils.simple_agents import SimplePipeline


def load_queries(csv_path: str) -> List[Dict]:
    """Load queries and expected SQL from CSV"""
    queries = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Support both formats
            if 'query' in row:
                queries.append({
                    "query": row['query'],
                    "expected_sql": row.get('sql', '')
                })
            elif 'input' in row:
                queries.append({
                    "query": row['input'],
                    "expected_sql": row.get('expected_output', '')
                })
    return queries


def calculate_similarity(generated: str, expected: str) -> float:
    """Simple similarity score (0-1)"""
    gen_words = set(generated.upper().split())
    exp_words = set(expected.upper().split())
    
    if not exp_words:
        return 1.0 if not gen_words else 0.0
    
    intersection = len(gen_words & exp_words)
    union = len(gen_words | exp_words)
    return intersection / union if union > 0 else 0.0


def benchmark(
    model_id: str,
    queries_file: str = "./test_data/benchmark_queries.csv",
    output_dir: str = "./results"
):
    """Run simple benchmark"""
    
    # Setup
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("SIMPLE NLQ→SQL BENCHMARK")
    print("=" * 60)
    print(f"Model: {model_id}")
    print(f"Dataset: {queries_file}")
    print()
    
    # Load queries
    query_pairs = load_queries(queries_file)
    print(f"Loaded {len(query_pairs)} queries\n")
    
    # Initialize pipeline
    pipeline = SimplePipeline(model_id)
    
    # Process queries
    results = []
    start_time = time.time()
    
    for idx, pair in enumerate(query_pairs, 1):
        user_query = pair["query"]
        expected_sql = pair["expected_sql"]
        
        print(f"[{idx}/{len(query_pairs)}] {user_query[:50]}...")
        
        q_start = time.time()
        output = pipeline.execute(user_query)
        q_time = time.time() - q_start
        
        # Calculate similarity
        similarity = calculate_similarity(output["sql"], expected_sql)
        
        result = {
            "query": user_query,
            "refined_query": output["refined_query"],
            "generated_sql": output["sql"],
            "expected_sql": expected_sql,
            "similarity_score": round(similarity, 3),
            "time_seconds": round(q_time, 2)
        }
        results.append(result)
        
        print(f"  Refined: {output['refined_query'][:50]}...")
        print(f"  SQL: {output['sql'][:50]}...")
        print(f"  Match: {similarity:.1%}\n")
    
    total_time = time.time() - start_time
    avg_similarity = sum(r["similarity_score"] for r in results) / len(results) if results else 0
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = output_dir / f"benchmark_{timestamp}.json"
    
    summary = {
        "model": model_id,
        "timestamp": timestamp,
        "total_queries": len(results),
        "total_time_seconds": round(total_time, 2),
        "avg_time_per_query": round(total_time / len(results), 2) if results else 0,
        "avg_similarity_score": round(avg_similarity, 3),
        "results": results
    }
    
    with open(results_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print("=" * 60)
    print("BENCHMARK COMPLETE")
    print("=" * 60)
    print(f"Total Time: {total_time:.2f}s")
    print(f"Avg Similarity: {avg_similarity:.1%}")
    print(f"Results saved: {results_file}")
    print()
    
    return summary


if __name__ == "__main__":
    import sys
    
    model_id = sys.argv[1] if len(sys.argv) > 1 else "infly/OpenCoder-8B-Instruct"
    queries_file = sys.argv[2] if len(sys.argv) > 2 else "./test_data/benchmark_queries.csv"
    
    benchmark(model_id, queries_file)
