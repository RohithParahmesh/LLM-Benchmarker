"""
Run simple benchmark for all enabled models in config
"""

import json
from pathlib import Path
from simple_benchmark import benchmark


def run_all():
    """Load config and benchmark all enabled models"""
    
    # Load config
    config_file = Path("benchmark_config.json")
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    models = [m for m in config['models'] if m.get('enabled', True)]
    dataset = config.get('benchmark_dataset', './test_data/benchmark_queries.csv')
    
    if not models:
        print("No enabled models in config")
        return
    
    print(f"\n{'='*60}")
    print(f"RUNNING BENCHMARKS FOR {len(models)} MODELS")
    print(f"{'='*60}\n")
    
    results_summary = []
    
    for idx, model_config in enumerate(models, 1):
        model_id = model_config['model_id']
        print(f"\n[{idx}/{len(models)}] Benchmarking: {model_id}\n")
        
        try:
            summary = benchmark(model_id, dataset)
            results_summary.append({
                "model": model_id,
                "status": "completed",
                "similarity": summary.get('avg_similarity_score', 0),
                "time_seconds": summary.get('total_time_seconds', 0)
            })
        except Exception as e:
            print(f"❌ Error with {model_id}: {e}\n")
            results_summary.append({
                "model": model_id,
                "status": "failed",
                "error": str(e)
            })
    
    # Print summary
    print(f"\n{'='*60}")
    print("OVERALL SUMMARY")
    print(f"{'='*60}\n")
    
    for result in results_summary:
        status = "✅" if result['status'] == 'completed' else "❌"
        model_short = result['model'].split('/')[-1]
        
        if result['status'] == 'completed':
            print(f"{status} {model_short:40} - Similarity: {result['similarity']:.1%} - Time: {result['time_seconds']:.1f}s")
        else:
            print(f"{status} {model_short:40} - {result['error']}")
    
    completed = sum(1 for r in results_summary if r['status'] == 'completed')
    print(f"\nCompleted: {completed}/{len(results_summary)}\n")


if __name__ == "__main__":
    run_all()
