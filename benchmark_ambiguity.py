"""
Benchmark for independent AmbiguityAgent
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict

from utils import AmbiguityAgent


def load_queries(csv_path: str) -> List[str]:
    """Load queries from CSV"""
    import csv
    queries = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # Skip header
        for row in reader:
            if row:
                queries.append(row[0])
    return queries


def benchmark_ambiguity(
    model_id: str = "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
    queries_file: str = "./test_data/ambiguity_intent.csv",
    output_dir: str = "./results",
    custom_instruction_key: str = None
):
    """
    Benchmark AmbiguityAgent on test queries
    
    Args:
        model_id: HuggingFace model ID
        queries_file: Path to test queries CSV
        output_dir: Directory to save results
        custom_instruction_key: Optional custom instruction key
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("AMBIGUITY AGENT BENCHMARK")
    print("=" * 60)
    print(f"Model: {model_id}")
    print(f"Queries: {queries_file}")
    print(f"Custom Instruction: {custom_instruction_key or 'Default'}")
    print()
    
    # Load queries
    queries = load_queries(queries_file)
    print(f"Loaded {len(queries)} queries")
    print()
    
    # Initialize agent
    agent = AmbiguityAgent(model_id)
    
    # Process queries
    results = []
    start_time = time.time()
    
    for idx, query in enumerate(queries, 1):
        print(f"Processing [{idx}/{len(queries)}]: {query[:60]}...")
        
        stage_start = time.time()
        result = agent.process(query, custom_instruction_key=custom_instruction_key)
        stage_time = time.time() - stage_start
        
        result["processing_time"] = stage_time
        results.append(result)
        
        print(f"  Classification: {result['classification']} ({stage_time:.2f}s)")
    
    total_time = time.time() - start_time
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = output_dir / f"ambiguity_benchmark_{timestamp}.json"
    
    summary = {
        "model": model_id,
        "task": "ambiguity_detection",
        "total_queries": len(queries),
        "total_time": total_time,
        "avg_time_per_query": total_time / len(queries),
        "custom_instruction": custom_instruction_key,
        "timestamp": timestamp,
        "results": results
    }
    
    with open(results_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print()
    print("=" * 60)
    print("BENCHMARK SUMMARY")
    print("=" * 60)
    print(f"Total queries processed: {len(queries)}")
    print(f"Total time: {total_time:.2f}s")
    print(f"Average time per query: {total_time / len(queries):.2f}s")
    print()
    
    # Count classifications
    ambiguous_count = sum(1 for r in results if r["classification"] == "Ambiguous")
    clear_count = sum(1 for r in results if r["classification"] == "Clear")
    unknown_count = len(results) - ambiguous_count - clear_count
    
    print("Classification Distribution:")
    print(f"  Ambiguous: {ambiguous_count}")
    print(f"  Clear: {clear_count}")
    print(f"  Unknown: {unknown_count}")
    print()
    print(f"Results saved to: {results_file}")
    print()


if __name__ == "__main__":
    benchmark_ambiguity()
