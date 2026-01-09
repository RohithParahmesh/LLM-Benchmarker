"""
Agent Base Class - Extend this for your custom agents
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseAgent(ABC):
    """
    Base class for benchmark agents
    
    Extend this class to create your custom agent for benchmarking.
    Your agent will be instantiated with a model and tokenizer,
    then execute() will be called for each test case.
    """
    
    def __init__(self, model, tokenizer, device: str = "cuda"):
        """
        Initialize agent with model and tokenizer
        
        Args:
            model: Transformer model
            tokenizer: Model tokenizer
            device: Device to run on (cuda/cpu)
        """
        self.model = model
        self.tokenizer = tokenizer
        self.device = device
    
    @abstractmethod
    def execute(self, input_text: str) -> str:
        """
        Execute agent logic on input
        
        Args:
            input_text: Input from CSV test case
            
        Returns:
            str: Agent output/response
        """
        pass
    
    def setup(self):
        """Optional: Setup before running tests"""
        pass
    
    def teardown(self):
        """Optional: Cleanup after running tests"""
        pass


# ============================================================================
# EXAMPLE AGENTS - Copy and modify for your use cases
# ============================================================================

class NLToSQLAgent(BaseAgent):
    """Example: NL to SQL translation agent"""
    
    def execute(self, input_text: str) -> str:
        prompt = f"Convert to SQL:\nQ: {input_text}\nSQL:"
        inputs = self.tokenizer.encode(prompt, return_tensors="pt").to(self.device)
        
        import torch
        with torch.no_grad():
            outputs = self.model.generate(
                inputs,
                max_new_tokens=256,
                temperature=0.0,
                top_p=0.95,
                do_sample=False
            )
        
        result = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        # Remove the prompt from output
        return result[len(prompt):].strip() if result.startswith(prompt) else result


class AmbiguityDetectionAgent(BaseAgent):
    """Example: Ambiguity detection agent"""
    
    def execute(self, input_text: str) -> str:
        prompt = f"Is this ambiguous?\nQuery: {input_text}\nAnalysis:"
        inputs = self.tokenizer.encode(prompt, return_tensors="pt").to(self.device)
        
        import torch
        with torch.no_grad():
            outputs = self.model.generate(
                inputs,
                max_new_tokens=256,
                temperature=0.0,
                top_p=0.95,
                do_sample=False
            )
        
        result = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return result[len(prompt):].strip() if result.startswith(prompt) else result


class SummarizationAgent(BaseAgent):
    """Example: Text summarization agent"""
    
    def execute(self, input_text: str) -> str:
        prompt = f"Summarize:\n{input_text}\n\nSummary:"
        inputs = self.tokenizer.encode(prompt, return_tensors="pt").to(self.device)
        
        import torch
        with torch.no_grad():
            outputs = self.model.generate(
                inputs,
                max_new_tokens=128,
                temperature=0.0,
                top_p=0.95,
                do_sample=False
            )
        
        result = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return result[len(prompt):].strip() if result.startswith(prompt) else result


# ============================================================================
# HOW TO CREATE YOUR OWN AGENT
# ============================================================================
"""
1. Extend BaseAgent
2. Implement execute() method
3. Optional: override setup() and teardown()

Example:

class MyCustomAgent(BaseAgent):
    def execute(self, input_text: str) -> str:
        # Your agent logic here
        prompt = f"Your prompt template: {input_text}"
        inputs = self.tokenizer.encode(prompt, return_tensors="pt").to(self.device)
        
        import torch
        with torch.no_grad():
            outputs = self.model.generate(inputs, max_new_tokens=256)
        
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    def setup(self):
        # Optional initialization
        print("Setting up my agent")
    
    def teardown(self):
        # Optional cleanup
        print("Cleaning up my agent")
"""
