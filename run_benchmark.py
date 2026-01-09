#!/usr/bin/env python3
"""
Simple LLM Benchmark Runner
Orchestrates: Download → Setup Engine → Create Agent → Run Tests → Cleanup → Next Model
"""

import os
import sys
import json
import pandas as pd
import logging
import time
from pathlib import Path
from typing import List, Dict, Any, Type
from datetime import datetime
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from utils.agent import BaseAgent, NLToSQLAgent, AmbiguityDetectionAgent

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Registry of available agents
AGENT_REGISTRY: Dict[str, Type[BaseAgent]] = {
    "nl_to_sql": NLToSQLAgent,
    "ambiguity_intent": AmbiguityDetectionAgent,
}


class SimpleBenchmark:
    def __init__(self, cache_dir="./models", device="cuda"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.device = self._setup_device(device)
        self.model = None
        self.tokenizer = None
        
    def _setup_device(self, device):
        """Setup device - fallback to CPU if CUDA unavailable"""
        if device == "cuda" and torch.cuda.is_available():
            logger.info(f"Using CUDA: {torch.cuda.get_device_name(0)}")
            return "cuda"
        logger.info("Using CPU")
        return "cpu"
    
    def download_model(self, model_id: str) -> bool:
        """Step 1: Download model from HuggingFace"""
        logger.info(f"[Step 1] Downloading model: {model_id}")
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
            self.model = AutoModelForCausalLM.from_pretrained(
                model_id, 
                trust_remote_code=True,
                cache_dir=str(self.cache_dir)
            )
            logger.info(f"✓ Model downloaded: {model_id}")
            return True
        except Exception as e:
            logger.error(f"✗ Download failed: {e}")
            return False
    
    def setup_inference_engine(self) -> bool:
        """Step 2: Setup inference engine"""
        logger.info("[Step 2] Setting up inference engine")
        try:
            self.model.to(self.device)
            self.model.eval()
            for param in self.model.parameters():
                param.requires_grad = False
            logger.info(f"✓ Inference engine ready on {self.device}")
            return True
        except Exception as e:
            logger.error(f"✗ Engine setup failed: {e}")
            return False
    
    def create_agent(self, task_type: str) -> BaseAgent:
        """Step 3: Create agent for the task"""
        logger.info(f"[Step 3] Creating agent for task: {task_type}")
        
        if task_type not in AGENT_REGISTRY:
            raise ValueError(
                f"Unknown task: {task_type}. Available: {list(AGENT_REGISTRY.keys())}"
            )
        
        agent_class = AGENT_REGISTRY[task_type]
        agent = agent_class(self.model, self.tokenizer, self.device)
        agent.setup()
        return agent
    
    def run_tests(self, agent: BaseAgent, test_data: pd.DataFrame) -> Dict[str, Any]:
        """Step 4: Run tests"""
        logger.info(f"[Step 4] Running tests ({len(test_data)} cases)")
        
        results = {
            "total": len(test_data),
            "passed": 0,
            "failed": 0,
            "results": []
        }
        
        for idx, row in test_data.iterrows():
            try:
                start = time.time()
                output = agent.execute(row['input'])
                elapsed = time.time() - start
                
                test_result = {
                    "index": idx,
                    "input": row['input'],
                    "expected": row.get('expected_output', ''),
                    "output": output,
                    "time": elapsed,
                    "passed": output.strip() == str(row.get('expected_output', '')).strip() if 'expected_output' in row else None
                }
                
                if test_result['passed']:
                    results["passed"] += 1
                elif test_result['passed'] is False:
                    results["failed"] += 1
                
                results["results"].append(test_result)
                logger.info(f"  Test {idx+1}: {elapsed:.2f}s")
                
            except Exception as e:
                logger.error(f"  Test {idx+1} failed: {e}")
                results["failed"] += 1
                results["results"].append({
                    "index": idx,
                    "error": str(e)
                })
        
        return results
    
    def cleanup(self):
        """Step 5: Cleanup resources"""
        logger.info("[Step 5] Cleaning up resources")
        if self.model:
            del self.model
        if self.tokenizer:
            del self.tokenizer
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        logger.info("✓ Cleanup complete")


def register_agent(task_name: str, agent_class: Type[BaseAgent]):
    """Register a custom agent"""
    AGENT_REGISTRY[task_name] = agent_class
    logger.info(f"Registered agent: {task_name}")


def load_test_data(csv_file: str) -> pd.DataFrame:
    """Load test data from CSV or Excel"""
    filepath = Path(csv_file)
    
    if not filepath.exists():
        logger.error(f"Test data file not found: {csv_file}")
        return pd.DataFrame()
    
    if filepath.suffix == '.xlsx' or filepath.suffix == '.xls':
        return pd.read_excel(csv_file)
    else:
        return pd.read_csv(csv_file)


def save_results(results: Dict, model_id: str, task_type: str):
    """Save results to JSON"""
    filename = f"results/{task_type}_{model_id.replace('/', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    Path("results").mkdir(exist_ok=True)
    
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"✓ Results saved: {filename}")


def run_benchmark(models: List[str], tasks: List[str], test_data_dir: str = "test_data"):
    """
    Main benchmark runner
    Flow: Download → Setup → Agent → Tests → Cleanup → Next Model
    """
    logger.info("="*70)
    logger.info("LLM BENCHMARK RUNNER")
    logger.info("="*70)
    
    for model_id in models:
        logger.info(f"\n{'='*70}")
        logger.info(f"MODEL: {model_id}")
        logger.info(f"{'='*70}")
        
        benchmark = SimpleBenchmark()
        
        # Step 1: Download
        if not benchmark.download_model(model_id):
            logger.error(f"Skipping {model_id}")
            continue
        
        # Step 2: Setup engine
        if not benchmark.setup_inference_engine():
            logger.error(f"Skipping {model_id}")
            continue
        
        # Run each task
        for task_type in tasks:
            logger.info(f"\n--- Task: {task_type} ---")
            
            # Load test data
            csv_file = f"{test_data_dir}/{task_type}.csv"
            test_data = load_test_data(csv_file)
            
            if test_data.empty:
                logger.warning(f"No test data for {task_type}")
                continue
            
            try:
                # Step 3: Create agent
                agent = benchmark.create_agent(task_type)
                
                # Step 4: Run tests
                results = benchmark.run_tests(agent, test_data)
                results["model"] = model_id
                results["task"] = task_type
                
                # Save results
                save_results(results, model_id, task_type)
                
                logger.info(f"Results: {results['passed']}/{results['total']} passed")
                
            except Exception as e:
                logger.error(f"Task failed: {e}")
        
        # Step 5: Cleanup
        benchmark.cleanup()
        logger.info("")
    
    logger.info("="*70)
    logger.info("BENCHMARK COMPLETE")
    logger.info("="*70)


if __name__ == "__main__":
    # Configure models and tasks
    MODELS = [
        "meta-llama/Llama-2-7b",
        # "microsoft/phi-2",
    ]
    
    TASKS = [
        "nl_to_sql",
        "ambiguity_intent",
    ]
    
    TEST_DATA_DIR = "test_data"
    
    run_benchmark(MODELS, TASKS, TEST_DATA_DIR)
