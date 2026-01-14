"""
NLQ→SQL Pipeline: Chains NLQAgent and SQLAgent together
Separate benchmark for independent AmbiguityAgent
"""

from typing import Dict, Optional, List
from .three_agents import NLQAgent, SQLAgent, AmbiguityAgent


class NLQSQLPipeline:
    """
    Pipeline that chains NLQAgent → SQLAgent
    
    Flow:
    1. Take user query
    2. Pass through NLQAgent for refinement
    3. Pass refined query through SQLAgent for SQL generation
    """
    
    def __init__(self, nlq_agent: NLQAgent, sql_agent: SQLAgent):
        """
        Initialize pipeline with two agents.
        
        Args:
            nlq_agent: NLQAgent instance for query refinement
            sql_agent: SQLAgent instance for SQL generation
        """
        self.nlq_agent = nlq_agent
        self.sql_agent = sql_agent
    
    def execute(self, user_query: str, 
                nlq_instruction_key: Optional[str] = None,
                sql_instruction_key: Optional[str] = None) -> Dict:
        """
        Execute pipeline on user query.
        
        Args:
            user_query: Original user query
            nlq_instruction_key: Optional custom instruction for NLQ stage
            sql_instruction_key: Optional custom instruction for SQL stage
        
        Returns:
            Dictionary with:
            - original_query: User's input
            - refined_query: Output from NLQAgent
            - sql: Generated SQL from SQLAgent
            - stages: Details from each stage
        """
        # Stage 1: NLQ Refinement
        nlq_result = self.nlq_agent.process(
            user_query,
            custom_instruction_key=nlq_instruction_key
        )
        refined_query = nlq_result["refined_query"]
        
        # Stage 2: SQL Generation
        sql_result = self.sql_agent.process(
            refined_query,
            custom_instruction_key=sql_instruction_key,
            context=f"Refined from: {user_query}"
        )
        
        return {
            "original_query": user_query,
            "refined_query": refined_query,
            "sql": sql_result["sql"],
            "stages": {
                "nlq": nlq_result,
                "sql": sql_result
            }
        }


class AmbiguityPipeline:
    """Standalone pipeline for AmbiguityAgent (independent execution)"""
    
    def __init__(self, ambiguity_agent: AmbiguityAgent):
        """
        Initialize with ambiguity agent.
        
        Args:
            ambiguity_agent: AmbiguityAgent instance
        """
        self.ambiguity_agent = ambiguity_agent
    
    def execute(self, user_query: str, 
                instruction_key: Optional[str] = None) -> Dict:
        """
        Execute ambiguity detection on query.
        
        Args:
            user_query: Query to analyze
            instruction_key: Optional custom instruction
        
        Returns:
            Dictionary with ambiguity classification
        """
        return self.ambiguity_agent.process(
            user_query,
            custom_instruction_key=instruction_key
        )
