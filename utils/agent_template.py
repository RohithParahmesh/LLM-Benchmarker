"""
CUSTOM AGENT TEMPLATE
Copy this file and modify for your custom benchmarking agent
"""

from utils.agent import BaseAgent
import torch


class MyCustomAgent(BaseAgent):
    """
    Your custom benchmarking agent
    
    This agent will be instantiated with:
    - model: The downloaded transformer model
    - tokenizer: The model's tokenizer
    - device: cuda or cpu
    """
    
    def setup(self):
        """Optional: Called once before running tests"""
        print("Setting up my custom agent")
    
    def execute(self, input_text: str) -> str:
        """
        Execute your agent logic
        
        Args:
            input_text: Input from CSV test case
            
        Returns:
            str: Your agent's output/response
        """
        # Your agent logic here
        # This will be called for each row in your CSV
        
        # Example: Create a prompt
        prompt = f"Your task: {input_text}\nResponse:"
        
        # Tokenize
        inputs = self.tokenizer.encode(prompt, return_tensors="pt").to(self.device)
        
        # Generate
        with torch.no_grad():
            outputs = self.model.generate(
                inputs,
                max_new_tokens=256,
                temperature=0.0,
                top_p=0.95,
                do_sample=False
            )
        
        # Decode and return
        result = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        # Remove prompt from output if needed
        return result[len(prompt):].strip() if result.startswith(prompt) else result
    
    def teardown(self):
        """Optional: Called after all tests complete"""
        print("Cleaning up my custom agent")


# ============================================================================
# TO USE THIS AGENT:
# ============================================================================
# 1. Save as: utils/my_agent.py
# 2. In run_benchmark.py, add this to the top:
#    from utils.my_agent import MyCustomAgent
# 3. Register it:
#    register_agent("my_task", MyCustomAgent)
# 4. Create test_data/my_task.csv with columns: input, expected_output
# 5. Add "my_task" to TASKS in run_benchmark.py
# 6. Run: python3 run_benchmark.py
