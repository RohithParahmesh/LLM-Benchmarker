# Custom Agent Benchmarking Guide

## Overview

The benchmark system benchmarks **your agent**, not just the LLM. Your agent orchestrates how the LLM is used for a specific task.

## Quick Start: Create a Custom Agent

### 1. Create Your Agent Class

Create a new file in `utils/` directory:

```python
# utils/my_agent.py
from utils.agent import BaseAgent
import torch

class MyCustomAgent(BaseAgent):
    def execute(self, input_text: str) -> str:
        # Your agent logic here
        prompt = f"Your prompt: {input_text}\nOutput:"
        inputs = self.tokenizer.encode(prompt, return_tensors="pt").to(self.device)
        
        with torch.no_grad():
            outputs = self.model.generate(inputs, max_new_tokens=256)
        
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
```

### 2. Create Test Data

Create CSV file in `test_data/`:

```csv
input,expected_output
"What is 2+2?","4"
"What is the capital of France?","Paris"
```

Or use Excel: `test_data/my_task.xlsx`

### 3. Register and Run

Edit `run_benchmark.py`:

```python
# At the top, import your agent
from utils.my_agent import MyCustomAgent

# Register it
register_agent("my_task_name", MyCustomAgent)

# In main(), add to TASKS:
TASKS = [
    "my_task_name",  # Your custom task
    "nl_to_sql",
    "ambiguity_intent",
]
```

### 4. Run Benchmark

```bash
python3 run_benchmark.py
```

## Agent Base Class

All agents inherit from `BaseAgent`:

```python
class BaseAgent(ABC):
    def __init__(self, model, tokenizer, device: str = "cuda"):
        self.model = model           # Transformer model
        self.tokenizer = tokenizer   # Model tokenizer
        self.device = device         # "cuda" or "cpu"
    
    @abstractmethod
    def execute(self, input_text: str) -> str:
        """Called for each test case. Must return string."""
        pass
    
    def setup(self):
        """Optional: Called once before tests"""
        pass
    
    def teardown(self):
        """Optional: Called after all tests"""
        pass
```

## Example: Question Answering Agent

```python
# utils/qa_agent.py
from utils.agent import BaseAgent
import torch

class QAAgent(BaseAgent):
    def setup(self):
        print("Initializing QA agent")
    
    def execute(self, input_text: str) -> str:
        prompt = f"""Answer the question:
Q: {input_text}
A:"""
        
        inputs = self.tokenizer.encode(prompt, return_tensors="pt").to(self.device)
        
        with torch.no_grad():
            outputs = self.model.generate(
                inputs,
                max_new_tokens=128,
                temperature=0.7,
                top_p=0.9
            )
        
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        # Extract answer only (remove prompt)
        return response.split("A:")[-1].strip()
    
    def teardown(self):
        print("QA agent done")
```

## Example: Code Generation Agent

```python
# utils/codegen_agent.py
from utils.agent import BaseAgent
import torch

class CodeGenAgent(BaseAgent):
    def execute(self, input_text: str) -> str:
        prompt = f"""Generate Python code:
# {input_text}
def solution():"""
        
        inputs = self.tokenizer.encode(prompt, return_tensors="pt").to(self.device)
        
        with torch.no_grad():
            outputs = self.model.generate(
                inputs,
                max_new_tokens=256,
                temperature=0.2,
                do_sample=True
            )
        
        code = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return code[len(prompt):].strip()
```

## Test Data Format

### CSV Format
```csv
input,expected_output
"test input 1","expected output 1"
"test input 2","expected output 2"
```

### Excel Format
Same columns, save as `.xlsx` or `.xls` in `test_data/` folder

### Columns Required
- `input`: The test input (required)
- `expected_output`: Expected output for comparison (optional)

## Benchmark Results

Results are saved to `results/` directory:

```
results/
  nl_to_sql_meta-llama_Llama-2-7b_20260109_120000.json
  ambiguity_intent_meta-llama_Llama-2-7b_20260109_120000.json
  my_task_name_meta-llama_Llama-2-7b_20260109_120000.json
```

Each result file contains:
- `total`: Total test cases
- `passed`: Number of exact matches
- `failed`: Number of mismatches
- `results`: Detailed results for each test

## Workflow

For each model and each task:

1. **Download** model from HuggingFace
2. **Setup** inference engine (move to GPU, eval mode)
3. **Create** your custom agent
4. **Run** agent on all test cases from CSV
5. **Save** results to JSON
6. **Cleanup** memory
7. **Repeat** for next task or model

## Performance Tips

- Use `temperature=0.0` for deterministic outputs
- Use `temperature>0` for diverse outputs
- Adjust `max_new_tokens` based on task
- Use `do_sample=False` for greedy decoding
- Add `fp16=True` for faster inference

## Built-in Example Agents

See `utils/agent.py` for example implementations:
- `NLToSQLAgent` - SQL generation
- `AmbiguityDetectionAgent` - Ambiguity analysis
- `SummarizationAgent` - Text summarization

## File Structure

```
LLM-Benchmarker/
├── run_benchmark.py           # Main runner
├── utils/
│   ├── agent.py              # Base class + examples
│   ├── agent_template.py      # Template for custom agents
│   └── my_agent.py           # Your custom agent
├── test_data/
│   ├── nl_to_sql.csv
│   ├── ambiguity_intent.csv
│   └── my_task_name.csv      # Your test data
└── results/
    └── *.json                # Benchmark results
```
