"""
Simple Agents for Basic Benchmarking
- NLQAgent: Refines natural language queries
- SQLAgent: Generates SQL from refined queries
"""

import torch
from typing import Optional, Dict
from transformers import AutoTokenizer, AutoModelForCausalLM


NLQ_RULES = """
Refine this query into a precise SQL command:

Rules:
1. Map terms: "mobile number" → prdmobile, "merchant code" → pycode
2. Use UPPER(TRIM(column)) for VARCHAR fields
3. P2P: "(trim(pycode)) in ('NULL','0000','')"
4. P2M: "(trim(pycode)) not in ('NULL','0000','7407','')"
5. Success: upper(trim(currstatusdesc)) IN ('SUCCESS', 'DEEMED', 'PARTIAL')

Task: Convert query to be SQL-ready
Output: Refined Query: [the refined query]
"""

SQL_RULES = """
Generate SQL from the refined query:

Rules:
1. Use CAST(SUM(txnamount) AS DOUBLE) / 100 for amounts
2. Use COUNT(*) for transaction count
3. Apply upper(trim(column)) to VARCHAR fields
4. Use asdt for dates
5. FROM table: upi_txn.urcs_ft_txns

Task: Generate valid SQL
Output: SQL Query: [the SQL]
"""


class SimpleNLQAgent:
    """Refines natural language queries"""
    
    def __init__(self, model_id: str, models_dir: str = "./models"):
        self.model_id = model_id
        self.models_dir = models_dir
        
        print(f"Loading NLQ Agent: {model_id}")
        self.tokenizer = AutoTokenizer.from_pretrained(model_id, cache_dir=models_dir)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        self.model = AutoModelForCausalLM.from_pretrained(
            model_id,
            torch_dtype="auto",
            device_map="auto",
            cache_dir=models_dir
        )
        self.model.eval()
    
    def process(self, query: str) -> str:
        """Refine the query"""
        prompt = f"""{NLQ_RULES}

Query: {query}

Refined Query:"""
        
        inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512).to(self.model.device)
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=150,
                temperature=0.7,
                top_p=0.95,
                do_sample=True,
                pad_token_id=self.tokenizer.pad_token_id
            )
        
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract refined query
        if "Refined Query:" in response:
            refined = response.split("Refined Query:")[-1].strip()
        else:
            refined = response[len(prompt):].strip() if len(response) > len(prompt) else response.strip()
        
        # Take only first line/sentence
        refined = refined.split('\n')[0].strip()
        return refined if refined else query


class SimpleSQLAgent:
    """Generates SQL from refined queries"""
    
    def __init__(self, model_id: str, models_dir: str = "./models"):
        self.model_id = model_id
        self.models_dir = models_dir
        
        print(f"Loading SQL Agent: {model_id}")
        self.tokenizer = AutoTokenizer.from_pretrained(model_id, cache_dir=models_dir)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        self.model = AutoModelForCausalLM.from_pretrained(
            model_id,
            torch_dtype="auto",
            device_map="auto",
            cache_dir=models_dir
        )
        self.model.eval()
    
    def process(self, refined_query: str) -> str:
        """Generate SQL from refined query"""
        prompt = f"""{SQL_RULES}

Refined Query: {refined_query}

SQL Query:"""
        
        inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512).to(self.model.device)
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=200,
                temperature=0.7,
                top_p=0.95,
                do_sample=True,
                pad_token_id=self.tokenizer.pad_token_id
            )
        
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract SQL
        if "SQL Query:" in response or "SQL:" in response:
            sql = response.split("SQL Query:" if "SQL Query:" in response else "SQL:")[-1].strip()
        else:
            sql = response[len(prompt):].strip() if len(response) > len(prompt) else response.strip()
        
        # Take only first complete SQL statement (up to first semicolon or newline)
        if ';' in sql:
            sql = sql.split(';')[0].strip() + ';'
        else:
            sql = sql.split('\n')[0].strip()
        
        return sql if sql else "SELECT * FROM upi_txn.urcs_ft_txns"


class SimplePipeline:
    """Simple NLQ→SQL pipeline"""
    
    def __init__(self, model_id: str, models_dir: str = "./models"):
        self.nlq_agent = SimpleNLQAgent(model_id, models_dir)
        self.sql_agent = SimpleSQLAgent(model_id, models_dir)
    
    def execute(self, user_query: str) -> Dict:
        """Execute: query → refined_query → sql"""
        # Stage 1: Refine query
        refined_query = self.nlq_agent.process(user_query)
        
        # Stage 2: Generate SQL
        sql = self.sql_agent.process(refined_query)
        
        return {
            "original_query": user_query,
            "refined_query": refined_query,
            "sql": sql
        }
