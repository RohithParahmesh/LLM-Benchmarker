# Input Data Flow Issue - Analysis & Fix

## Problem Identified

The NLQ and SQL agents were **missing database schema context** in their inputs, which caused them to generate incorrect or incomplete SQL queries.

### Root Causes:

1. **Missing Schema Context**: The agents were not receiving the UPI transaction database schema information (table names, column definitions, transaction types, join conditions, etc.)
   
2. **Context Parameter Not Utilized**: The `context` parameter in the agent's `process()` method was available but not being passed from the pipeline to the agents

3. **Pipeline Not Passing Schema**: The `NLQSQLPipeline` had no way to inject schema context into the agents' prompts

## Changes Made

### 1. Created Schema Context Module (`utils/schema_context.py`)
- Comprehensive UPI transaction database schema definition
- Includes main table (`upi_txn.urcs_ft_txns`), reference tables, and their columns
- Documents transaction types (P2P, P2M, P2PM, Autopay, etc.)
- Defines VPA/wallet identification methods
- Lists all join conditions between tables

### 2. Updated Pipeline (`utils/nlq_sql_pipeline.py`)
**Before:**
```python
def __init__(self, nlq_agent: NLQAgent, sql_agent: SQLAgent):
    self.nlq_agent = nlq_agent
    self.sql_agent = sql_agent

# Only passing user_query, no schema context
nlq_result = self.nlq_agent.process(user_query, custom_instruction_key=nlq_instruction_key)
```

**After:**
```python
def __init__(self, nlq_agent: NLQAgent, sql_agent: SQLAgent, schema_context: Optional[str] = None):
    self.nlq_agent = nlq_agent
    self.sql_agent = sql_agent
    self.schema_context = schema_context  # NEW

# Now passing schema context to both agents
nlq_result = self.nlq_agent.process(
    user_query,
    custom_instruction_key=nlq_instruction_key,
    context=self.schema_context or ""  # NEW
)

sql_result = self.sql_agent.process(
    refined_query,
    custom_instruction_key=sql_instruction_key,
    context=self.schema_context or ""  # NEW - was passing "Refined from: {user_query}"
)
```

### 3. Updated Benchmark Script (`benchmark_nlq_sql_pipeline.py`)
- Added schema context import: `from utils.schema_context import get_schema_context`
- Loads schema context before initializing pipeline
- Passes schema context to `NLQSQLPipeline` initialization

### 4. Updated Custom Instructions (`utils/custom_instructions.py`)
- Updated `render_prompt()` method to properly handle empty context
- Updated NLQ refinement user prompt template to clearly label schema information
- Updated SQL generation user prompt template to clearly label schema information

## Data Flow After Fix

```
User Query
    ↓
NLQAgent.process(user_query, context=SCHEMA_CONTEXT)
    - Receives: original query + complete schema definition
    - Refines query using schema knowledge
    - Returns: refined_query
    ↓
SQLAgent.process(refined_query, context=SCHEMA_CONTEXT)
    - Receives: refined query + complete schema definition
    - Generates SQL using both refined query and schema knowledge
    - Returns: sql
```

## Key Information Now Available to Agents

The schema context includes:
- All table and column names with descriptions
- Data types for each column
- Transaction type definitions and filtering logic
- VPA/wallet identification methods
- Success/failure transaction conditions
- All join conditions between tables
- Real-world examples of proper SQL syntax for this database

This enables the agents to:
1. Use exact column names from the schema
2. Apply correct case transformations (UPPER, TRIM) where needed
3. Generate proper JOIN statements
4. Apply correct transaction filtering logic
5. Handle aggregations correctly
