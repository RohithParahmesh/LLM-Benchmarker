#!/usr/bin/env python3
"""
Benchmark script for testing LLM agents on various tasks.
Creates agents, tests them on datasets, and logs results.
"""

import os
import json
import csv
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple
import torch
from tqdm import tqdm

from utils.agent import Agent


class BenchmarkRunner:
    """Runs benchmarks on LLM agents"""
    
    def __init__(self, models_dir: str = "./models", results_dir: str = "./results"):
        self.models_dir = models_dir
        self.results_dir = results_dir
        self.logs_dir = "./logs"
        
        # Create directories if they don't exist
        Path(self.results_dir).mkdir(exist_ok=True)
        Path(self.logs_dir).mkdir(exist_ok=True)
        
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.results = {}
        
    def load_models(self) -> List[str]:
        """Load model IDs from models.txt"""
        models = []
        with open("models.txt", "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    models.append(line)
        return models
    
    def load_test_data(self, data_file: str) -> List[Dict]:
        """Load test data from CSV file"""
        data = []
        with open(data_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)
        return data
    
    def evaluate_response(self, predicted: str, expected: str) -> Dict:
        """
        Evaluate a single response.
        Returns metrics including exact match and similarity.
        """
        # Normalize strings
        pred_norm = predicted.lower().strip()
        exp_norm = expected.lower().strip()
        
        # Exact match
        exact_match = pred_norm == exp_norm
        
        # Partial match (check if expected is substring of predicted)
        partial_match = exp_norm in pred_norm
        
        # Calculate similarity (simple token overlap)
        pred_tokens = set(pred_norm.split())
        exp_tokens = set(exp_norm.split())
        if pred_tokens and exp_tokens:
            overlap = len(pred_tokens & exp_tokens)
            similarity = overlap / len(exp_tokens)
        else:
            similarity = 1.0 if exact_match else 0.0
        
        return {
            "exact_match": exact_match,
            "partial_match": partial_match,
            "similarity": similarity
        }
    
    def run_test_on_dataset(self, agent: Agent, dataset_name: str, test_data: List[Dict]) -> Dict:
        """Run tests on a single dataset"""
        results = {
            "dataset": dataset_name,
            "total_tests": len(test_data),
            "passed": 0,
            "failed": 0,
            "exact_matches": 0,
            "partial_matches": 0,
            "avg_similarity": 0.0,
            "avg_response_time": 0.0,
            "details": []
        }
        
        similarities = []
        response_times = []
        
        print(f"\n  Testing on {dataset_name}...")
        for i, test_case in enumerate(tqdm(test_data, desc=f"    {dataset_name}", leave=False)):
            input_text = test_case["input"]
            expected = test_case["expected_output"]
            
            # Generate response
            start_time = time.time()
            try:
                response = agent.generate(input_text)
                response_time = time.time() - start_time
            except Exception as e:
                response = f"Error: {str(e)}"
                response_time = time.time() - start_time
            
            # Evaluate
            evaluation = self.evaluate_response(response, expected)
            
            if evaluation["exact_match"]:
                results["passed"] += 1
                results["exact_matches"] += 1
            elif evaluation["partial_match"]:
                results["partial_matches"] += 1
            else:
                results["failed"] += 1
            
            similarities.append(evaluation["similarity"])
            response_times.append(response_time)
            
            # Store details
            results["details"].append({
                "input": input_text,
                "expected": expected,
                "predicted": response,
                "exact_match": evaluation["exact_match"],
                "partial_match": evaluation["partial_match"],
                "similarity": evaluation["similarity"],
                "response_time": response_time
            })
        
        # Calculate averages
        results["avg_similarity"] = sum(similarities) / len(similarities) if similarities else 0.0
        results["avg_response_time"] = sum(response_times) / len(response_times) if response_times else 0.0
        
        return results
    
    def run_benchmark_for_model(self, model_id: str) -> Dict:
        """Run complete benchmark for a single model"""
        print(f"\n{'='*60}")
        print(f"Benchmarking: {model_id}")
        print(f"{'='*60}")
        
        model_results = {
            "model": model_id,
            "timestamp": datetime.now().isoformat(),
            "datasets": {}
        }
        
        try:
            # Create agent
            print(f"\nInitializing agent...")
            agent = Agent(model_id=model_id, models_dir=self.models_dir)
            
            # Load and test on all datasets
            dataset_files = [
                ("ambiguity_intent", "test_data/ambiguity_intent.csv"),
                ("nl_to_sql", "test_data/nl_to_sql.csv")
            ]
            
            for dataset_name, dataset_path in dataset_files:
                if os.path.exists(dataset_path):
                    test_data = self.load_test_data(dataset_path)
                    dataset_results = self.run_test_on_dataset(agent, dataset_name, test_data)
                    model_results["datasets"][dataset_name] = dataset_results
                    
                    # Print summary
                    print(f"\n  Results for {dataset_name}:")
                    print(f"    Exact matches: {dataset_results['exact_matches']}/{dataset_results['total_tests']}")
                    print(f"    Partial matches: {dataset_results['partial_matches']}/{dataset_results['total_tests']}")
                    print(f"    Avg similarity: {dataset_results['avg_similarity']:.3f}")
                    print(f"    Avg response time: {dataset_results['avg_response_time']:.3f}s")
            
            # Clean up
            del agent
            torch.cuda.empty_cache()
            
        except Exception as e:
            print(f"Error benchmarking {model_id}: {str(e)}")
            model_results["error"] = str(e)
        
        return model_results
    
    def run(self):
        """Run complete benchmark suite"""
        print("\n" + "="*60)
        print("LLM Benchmark Suite")
        print("="*60)
        
        models = self.load_models()
        print(f"\nFound {len(models)} model(s) to benchmark")
        
        all_results = {
            "timestamp": self.timestamp,
            "total_models": len(models),
            "models": []
        }
        
        for i, model_id in enumerate(models, 1):
            print(f"\n[{i}/{len(models)}]", end=" ")
            model_results = self.run_benchmark_for_model(model_id)
            all_results["models"].append(model_results)
            
            # Save results after each model
            self.save_results(all_results)
        
        print("\n" + "="*60)
        print("Benchmark Complete!")
        print("="*60)
        print(f"Results saved to: {self.results_dir}")
        
        return all_results
    
    def save_results(self, results: Dict):
        """Save benchmark results to JSON"""
        results_file = os.path.join(
            self.results_dir,
            f"benchmark_results_{self.timestamp}.json"
        )
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2)
        print(f"Results saved to: {results_file}")


if __name__ == "__main__":
    runner = BenchmarkRunner()
    results = runner.run()
