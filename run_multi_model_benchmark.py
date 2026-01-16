"""
Multi-Model Benchmarking Script
Runs NLQ→SQL Pipeline benchmarks on multiple models from a configuration list
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict
import csv
from benchmark_nlq_sql_pipeline import benchmark_nlq_sql_pipeline


class BenchmarkConfig:
    """Configuration for running benchmarks on multiple models"""
    
    def __init__(self, config_file: str = "benchmark_config.json"):
        """Load configuration from JSON file"""
        self.config_file = config_file
        self.models = []
        self.benchmark_dataset = None
        self.output_dir = "./results"
        self.load_config()
    
    def load_config(self):
        """Load or create default configuration"""
        if Path(self.config_file).exists():
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                self.models = config.get('models', [])
                self.benchmark_dataset = config.get('benchmark_dataset', 'test_data/benchmark_queries.csv')
                self.output_dir = config.get('output_dir', './results')
        else:
            self.create_default_config()
    
    def create_default_config(self):
        """Create a default configuration file"""
        config = {
            "models": [
                {
                    "model_id": "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
                    "enabled": True,
                    "nlq_instruction_key": None,
                    "sql_instruction_key": None
                },
                {
                    "model_id": "infly/OpenCoder-8B-Instruct",
                    "enabled": True,
                    "nlq_instruction_key": None,
                    "sql_instruction_key": None
                },
                {
                    "model_id": "meta-llama/Llama-3.1-8B-Instruct",
                    "enabled": True,
                    "nlq_instruction_key": None,
                    "sql_instruction_key": None
                },
                {
                    "model_id": "Qwen/Qwen2.5-7B-Instruct",
                    "enabled": True,
                    "nlq_instruction_key": None,
                    "sql_instruction_key": None
                },
                {
                    "model_id": "mistralai/Mistral-7B-Instruct-v0.3",
                    "enabled": True,
                    "nlq_instruction_key": None,
                    "sql_instruction_key": None
                }
            ],
            "benchmark_dataset": "test_data/benchmark_queries.csv",
            "output_dir": "./results",
            "notes": "Edit this file to enable/disable models or customize instructions"
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        self.models = config['models']
        self.benchmark_dataset = config['benchmark_dataset']
        self.output_dir = config['output_dir']
        
        print(f"Created default configuration: {self.config_file}")
        print("Edit the file to enable/disable models or add custom instructions")


class MultiModelBenchmark:
    """Run benchmarks across multiple models"""
    
    def __init__(self, config_file: str = "benchmark_config.json"):
        self.config = BenchmarkConfig(config_file)
        self.results = {
            "start_time": datetime.now().isoformat(),
            "models": [],
            "summary": {}
        }
    
    def run_all_benchmarks(self):
        """Run benchmarks for all enabled models"""
        enabled_models = [m for m in self.config.models if m.get('enabled', True)]
        
        if not enabled_models:
            print("❌ No models enabled in configuration!")
            return
        
        print("\n" + "=" * 70)
        print("MULTI-MODEL BENCHMARK RUNNER")
        print("=" * 70)
        print(f"Configuration: {self.config.config_file}")
        print(f"Benchmark Dataset: {self.config.benchmark_dataset}")
        print(f"Output Directory: {self.config.output_dir}")
        print(f"Total Models to Run: {len(enabled_models)}")
        print("=" * 70 + "\n")
        
        model_results = []
        total_start = time.time()
        
        for idx, model_config in enumerate(enabled_models, 1):
            model_id = model_config['model_id']
            print(f"\n[{idx}/{len(enabled_models)}] Running benchmark for: {model_id}")
            print("-" * 70)
            
            try:
                model_start = time.time()
                
                # Run the benchmark
                benchmark_nlq_sql_pipeline(
                    model_id=model_id,
                    queries_file=self.config.benchmark_dataset,
                    output_dir=self.config.output_dir,
                    nlq_instruction_key=model_config.get('nlq_instruction_key'),
                    sql_instruction_key=model_config.get('sql_instruction_key')
                )
                
                model_time = time.time() - model_start
                
                result = {
                    "model": model_id,
                    "status": "completed",
                    "time_taken": model_time,
                    "nlq_instruction": model_config.get('nlq_instruction_key'),
                    "sql_instruction": model_config.get('sql_instruction_key')
                }
                model_results.append(result)
                
                print(f"✅ Completed in {model_time:.2f}s\n")
                
            except Exception as e:
                print(f"❌ Error benchmarking {model_id}: {str(e)}\n")
                result = {
                    "model": model_id,
                    "status": "failed",
                    "error": str(e)
                }
                model_results.append(result)
        
        total_time = time.time() - total_start
        
        # Save summary
        self.results['end_time'] = datetime.now().isoformat()
        self.results['models'] = model_results
        self.results['total_time_seconds'] = total_time
        self.results['dataset'] = self.config.benchmark_dataset
        
        self.save_summary()
        self.print_summary(model_results, total_time)
    
    def save_summary(self):
        """Save benchmark summary to JSON"""
        output_dir = Path(self.config.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        summary_file = output_dir / f"multi_model_benchmark_summary_{timestamp}.json"
        
        with open(summary_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"📊 Summary saved to: {summary_file}")
    
    def print_summary(self, model_results: List[Dict], total_time: float):
        """Print benchmark summary"""
        print("\n" + "=" * 70)
        print("BENCHMARK SUMMARY")
        print("=" * 70)
        print(f"Dataset: {self.config.benchmark_dataset}")
        print(f"Total Time: {total_time:.2f}s ({total_time/60:.2f}m)")
        print()
        
        print("MODEL RESULTS:")
        for result in model_results:
            status = "✅" if result['status'] == 'completed' else "❌"
            model_short = result['model'].split('/')[-1]
            
            if result['status'] == 'completed':
                time_str = f"{result['time_taken']:.2f}s"
                print(f"  {status} {model_short:40} - {time_str}")
            else:
                error = result.get('error', 'Unknown error')[:50]
                print(f"  {status} {model_short:40} - Error: {error}")
        
        completed = sum(1 for r in model_results if r['status'] == 'completed')
        print(f"\nCompleted: {completed}/{len(model_results)}")
        print("=" * 70 + "\n")


def main():
    """Main entry point"""
    import sys
    
    config_file = sys.argv[1] if len(sys.argv) > 1 else "benchmark_config.json"
    
    benchmark = MultiModelBenchmark(config_file)
    benchmark.run_all_benchmarks()


if __name__ == "__main__":
    main()
