"""
Three-Agent System:
1. AmbiguityAgent - Independent ambiguity detection
2. NLQAgent - Natural Language Query refinement
3. SQLAgent - SQL generation from refined queries
"""

import os
from typing import Optional, Dict
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

from .custom_instructions import get_instruction


class BaseAgent:
    """Base class for all agents"""
    
    def __init__(self, model_id: str, models_dir: str = "./models", device: Optional[str] = None):
        """Initialize agent with model"""
        self.model_id = model_id
        self.models_dir = models_dir
        
        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"
        self.device = device
        
        os.environ["HF_HOME"] = models_dir
        os.environ["TRANSFORMERS_CACHE"] = models_dir
        
        print(f"Loading {self.__class__.__name__}: {model_id}")
        
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_id,
            trust_remote_code=True,
            cache_dir=models_dir
        )
        
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        self.model = AutoModelForCausalLM.from_pretrained(
            model_id,
            torch_dtype="auto",
            device_map="auto" if self.device == "cuda" else self.device,
            trust_remote_code=True,
            cache_dir=models_dir,
            attn_implementation="flash_attention_2" if self.device == "cuda" else None
        )
        
        self.model.eval()
    
    def generate(self, prompt: str, max_length: int = 256, temperature: float = 0.7) -> str:
        """Generate response from prompt"""
        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=512
        ).to(self.model.device)
        
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
        
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        if prompt in response:
            response = response[len(prompt):].strip()
        
        return response


class AmbiguityAgent(BaseAgent):
    """Independent agent for detecting ambiguity in user queries"""
    
    def __init__(self, model_id: str, models_dir: str = "./models", device: Optional[str] = None):
        super().__init__(model_id, models_dir, device)
        self.task = "ambiguity_detection"
    
    def process(self, input_text: str, custom_instruction_key: Optional[str] = None) -> Dict:
        """
        Detect ambiguity in input.
        
        Args:
            input_text: User input to analyze
            custom_instruction_key: Optional custom instruction key
        
        Returns:
            Dictionary with ambiguity assessment
        """
        if custom_instruction_key:
            instruction = get_instruction(custom_instruction_key)
            if instruction:
                system_prompt, user_prompt = instruction.render_prompt(input_text, "")
                prompt = f"{system_prompt}\n\n{user_prompt}"
            else:
                prompt = self._get_default_prompt(input_text)
        else:
            prompt = self._get_default_prompt(input_text)
        
        response = self.generate(prompt, max_length=256)
        
        return {
            "input": input_text,
            "classification": self._extract_classification(response),
            "full_response": response,
            "task": self.task
        }
    
    def _get_default_prompt(self, input_text: str) -> str:
        """Default ambiguity detection prompt - uses custom instruction"""
        instruction = get_instruction("ambiguity_detection")
        if instruction:
            system_prompt, user_prompt = instruction.render_prompt(input_text, "")
            return f"{system_prompt}\n\n{user_prompt}"
        return f"""Analyze if this query is ambiguous or clear:

Query: {input_text}

Is this ambiguous? Provide classification (Ambiguous/Clear) and brief reason."""
    
    @staticmethod
    def _extract_classification(response: str) -> str:
        """Extract classification from response"""
        response_lower = response.lower()
        
        if "ambiguous" in response_lower and "not ambiguous" not in response_lower:
            return "Ambiguous"
        elif "clear" in response_lower or "not ambiguous" in response_lower:
            return "Clear"
        else:
            return "Unknown"


class NLQAgent(BaseAgent):
    """Natural Language Query refinement agent"""
    
    def __init__(self, model_id: str, models_dir: str = "./models", device: Optional[str] = None):
        super().__init__(model_id, models_dir, device)
        self.task = "nlq_refinement"
    
    def process(self, input_text: str, custom_instruction_key: Optional[str] = None, 
                context: str = "") -> Dict:
        """
        Refine natural language query.
        
        Args:
            input_text: Original user query
            custom_instruction_key: Optional custom instruction key
            context: Optional context (e.g., ambiguity assessment)
        
        Returns:
            Dictionary with refined query
        """
        if custom_instruction_key:
            instruction = get_instruction(custom_instruction_key)
            if instruction:
                system_prompt, user_prompt = instruction.render_prompt(input_text, context)
                prompt = f"{system_prompt}\n\n{user_prompt}"
            else:
                prompt = self._get_default_prompt(input_text, context)
        else:
            prompt = self._get_default_prompt(input_text, context)
        
        response = self.generate(prompt, max_length=256)
        refined_query = response.strip()
        
        return {
            "input": input_text,
            "refined_query": refined_query,
            "full_response": response,
            "task": self.task
        }
    
    def _get_default_prompt(self, input_text: str, context: str = "") -> str:
        """Default NLQ refinement prompt - uses custom instruction"""
        instruction = get_instruction("nlq_refinement")
        if instruction:
            system_prompt, user_prompt = instruction.render_prompt(input_text, context)
            return f"{system_prompt}\n\n{user_prompt}"
        return f"""Refine this user query to make it clearer and more specific:

Original Query: {input_text}

{f'Context: {context}' if context else ''}

Provide a refined version of the query that is:
- More specific and complete
- Includes necessary details
- Clear about intent

Refined Query:"""


class SQLAgent(BaseAgent):
    """SQL generation agent that takes refined NLQ and generates SQL"""
    
    def __init__(self, model_id: str, models_dir: str = "./models", device: Optional[str] = None):
        super().__init__(model_id, models_dir, device)
        self.task = "sql_generation"
    
    def process(self, input_text: str, custom_instruction_key: Optional[str] = None,
                context: str = "") -> Dict:
        """
        Generate SQL from refined NLQ.
        
        Args:
            input_text: Refined NLQ query
            custom_instruction_key: Optional custom instruction key
            context: Optional context (e.g., previous results)
        
        Returns:
            Dictionary with generated SQL
        """
        if custom_instruction_key:
            instruction = get_instruction(custom_instruction_key)
            if instruction:
                system_prompt, user_prompt = instruction.render_prompt(input_text, context)
                prompt = f"{system_prompt}\n\n{user_prompt}"
            else:
                prompt = self._get_default_prompt(input_text, context)
        else:
            prompt = self._get_default_prompt(input_text, context)
        
        response = self.generate(prompt, max_length=200)
        sql = self._extract_sql(response)
        
        return {
            "input": input_text,
            "sql": sql,
            "full_response": response,
            "task": self.task
        }
    
    def _get_default_prompt(self, input_text: str, context: str = "") -> str:
        """Default SQL generation prompt - uses custom instruction"""
        instruction = get_instruction("sql_generation")
        if instruction:
            system_prompt, user_prompt = instruction.render_prompt(input_text, context)
            return f"{system_prompt}\n\n{user_prompt}"
        return f"""Generate a SQL query for this request:

Request: {input_text}

{f'Context: {context}' if context else ''}

Rules:
- Generate valid SQL syntax
- Include appropriate clauses (WHERE, GROUP BY, ORDER BY as needed)
- Return only the SQL query without explanations

SQL Query:"""
    
    @staticmethod
    def _extract_sql(response: str) -> str:
        """Extract SQL from response"""
        response = response.strip()
        for prefix in ["SQL:", "sql:", "QUERY:", "Query:", "SELECT", "select"]:
            if response.startswith(prefix):
                response = response[len(prefix):].strip()
                break
        
        lines = response.split('\n')
        sql = lines[0].strip() if lines else response
        
        return sql
