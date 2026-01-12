"""
Agent module for LLM inference and task execution.
"""

import os
from typing import Optional
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    pipeline
)


class Agent:
    """LLM Agent for running benchmarks"""
    
    def __init__(self, model_id: str, models_dir: str = "./models", device: Optional[str] = None):
        """
        Initialize the agent with a specific model.
        
        Args:
            model_id: HuggingFace model ID (e.g., "meta-llama/Llama-2-7b")
            models_dir: Directory where models are cached
            device: Device to run on (cuda, cpu, auto). Auto-detects if not specified.
        """
        self.model_id = model_id
        self.models_dir = models_dir
        
        # Set device
        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"
        self.device = device
        
        # Set cache directory
        os.environ["HF_HOME"] = models_dir
        os.environ["TRANSFORMERS_CACHE"] = models_dir
        
        print(f"Loading model: {model_id}")
        print(f"Device: {self.device}")
        
        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_id,
            trust_remote_code=True,
            cache_dir=models_dir
        )
        
        # Set pad token if not set
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        # Load model
        self.model = AutoModelForCausalLM.from_pretrained(
            model_id,
            torch_dtype="auto",
            device_map="auto" if self.device == "cuda" else self.device,
            trust_remote_code=True,
            cache_dir=models_dir,
            attn_implementation="flash_attention_2" if self.device == "cuda" else None
        )
        
        self.model.eval()
        print(f"Model loaded successfully")
    
    def generate(self, prompt: str, max_length: int = 256, temperature: float = 0.7) -> str:
        """
        Generate a response for the given prompt.
        
        Args:
            prompt: Input text prompt
            max_length: Maximum length of generated text
            temperature: Sampling temperature (higher = more creative)
        
        Returns:
            Generated text response
        """
        # Prepare inputs
        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=512
        ).to(self.model.device)
        
        # Generate
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_length,
                temperature=temperature,
                top_p=0.95,
                do_sample=True,
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id
            )
        
        # Decode
        response = self.tokenizer.decode(
            outputs[0],
            skip_special_tokens=True
        )
        
        # Remove the prompt from the response
        if response.startswith(prompt):
            response = response[len(prompt):].strip()
        
        return response
    
    def __del__(self):
        """Cleanup when agent is destroyed"""
        if hasattr(self, 'model'):
            del self.model
        if hasattr(self, 'tokenizer'):
            del self.tokenizer
        torch.cuda.empty_cache()
