"""
Custom instruction prompts for agent pipelines.
Allows flexible instruction setup for each agent in a chain.
"""

from typing import Dict, Optional


class CustomInstruction:
    """Represents a custom instruction for an agent"""
    
    def __init__(self, name: str, system_prompt: str, user_prompt_template: str, 
                 description: str = ""):
        self.name = name
        self.system_prompt = system_prompt
        self.user_prompt_template = user_prompt_template  # Can use {input} and {context}
        self.description = description
    
    def render_prompt(self, user_input: str, context: str = "") -> tuple:
        """
        Render both system and user prompts.
        Returns: (system_prompt, user_prompt)
        """
        user_prompt = self.user_prompt_template.format(
            input=user_input,
            context=context
        )
        return self.system_prompt, user_prompt


class InstructionRegistry:
    """Registry for custom instructions"""
    
    def __init__(self):
        self.instructions: Dict[str, CustomInstruction] = {}
        self._register_defaults()
    
    def _register_defaults(self):
        """Register default instructions"""
        
        # NLQ Refinement - Refine natural language queries
        self.register(
            "nlq_refinement",
            CustomInstruction(
                name="nlq_refinement",
                system_prompt="""[INST] 
You are an expert at refining natural language queries into precise SQL generation commands.

### Task ###
Generate:
1. Improved natural language query
2. Combined column list

### Format Requirements ###
Strictly follow:
Refined Query: [text]
required_columns = ["column1", "column2"]

### Database Schema Context ###
Map colloquial terms to schema columns (example: "mobile number" -- "prdmobile", "merchant code" -- "pycode")
Explicitly state JOIN conditions using schema relationships.

### Filtering Guidelines ###
For all VARCHAR fields in schema mention to use UPPER(TRIM(column_name)) for consistency except for "asdt"

### Transaction filtering ###
1. For P2P or person to person transactions: "(trim(pycode)) in ('NULL','0000','')"
2. For P2M transactions: "(trim(pycode)) not in ('NULL','0000','7407','')"
3. For P2PM transactions: "(trim(pycode)) in ('7407')"
4. For Autopay transactions: "initmode='11' and purposecode='14'"
5. For UPI International or IUPI transactions: "initmode='12' and payeracctype in ('NRE', 'NRO')"
6. For Tap and Pay transactions: "initmode='06'"
7. For UPI-LITE-X transactions: "initmode='06' and purposecode='45'"
8. For UPI-LITE transactions: "purposecode in ('41','42','43','44')"
9. For RCC_ON_UPI or CC_ON_UPI: "payeracctype='CREDIT'"
10. For Credit Line transactions: "payeracctype in ('CREDITLINE', 'CREDITLINE01', ... 'CL015')"
11. For UPI circle transactions: "purposecode='87'"
12. For UPI IPO transactions: "purposecode='01' and pycode='6211' and initmode in ('11','13')"
13. For UPI-Mandate transactions: "purposecode='76' and pycode='6211' and initmode in ('11','13')"

### SQL condition for VPA filtering ###
1. For PhonePe: split(lower(trim(prfvaddr)),'@')[2] in ('axl','ibl','ybl')
2. For Paytm: split(lower(trim(prfvaddr)),'@')[2] in ('paytm','ptyes','ptaxis','pthdfc','ptsbi','pytm0123456.ifsc.npci')
3. For GooglePay: split(lower(trim(prfvaddr)),'@')[2] in ('okaxis','okhdfcbank','okicici','oksbi','okpayaxis', 'okbizaxis','okbizicici')
4. For BHIM: split(lower(trim(prfvaddr)),'@')[2] in ('upi')

### SQL condition for success and failure ###
1. For declined or failed transactions: upper(trim(currstatusdesc)) IN ('FAILURE')
2. For technical declined transactions: upi_masters.upi_new_errorcode_respcd_master.approvedflag = 'TD'
3. For business declined transactions: upi_masters.upi_new_errorcode_respcd_master.approvedflag = 'BD'
4. For approved or successful transactions: upper(trim(currstatusdesc)) IN ('SUCCESS', 'DEEMED', 'PARTIAL')

### Formatting Guidelines ###
1. Start with action verb: "Generate/Fetch/Build an SQL query..."
2. Use exact column names from schema.
3. Preserve original query intent.
4. Do not give any explanation or generate any SQL code.
[/INST]""",
                user_prompt_template="""Refine this natural language query:

{input}

{context}

Refined Query:""",
                description="NLQ refinement with SQL preparation"
            )
        )
        
        # SQL Generation - Generate SQL from refined NLQ
        self.register(
            "sql_generation",
            CustomInstruction(
                name="sql_generation",
                system_prompt="""[INST] 
You are an expert SQL query generator for UPI transaction analysis.

### Handling Dates ###
1. For date fields in WHERE clause, use date (VARCHAR column) formatted as YYYY-MM-DD
2. To convert date to DATE, use CAST(asdt AS DATE) in SELECT clauses (not in WHERE)
3. If date not mentioned, consider asdt = current date

### Amount and Aggregations ###
1. For total amount/spends/revenue: CAST(SUM(txnamount) AS DOUBLE) / 100
2. For transaction count/volume: COUNT(*)
3. Average Transaction Value (ATV): CAST(SUM(txnamount) AS DOUBLE) / COUNT(*)
4. Unique/distinct user count: count(prdmobile)
5. GROUP BY cannot contain aggregations, window functions or grouping operations

### String Handling Consistency ###
1. Apply upper(trim(column)) to all VARCHAR fields except "asdt"
2. For merchant conditions use "like" instead of "="
3. For bin-based queries, use first six digits: SUBSTR((praccno), 1, 6)

### SQL condition for success and failure ###
1. For declined or failed: upper(trim(currstatusdesc)) IN ('FAILURE')
2. For technical declined: upi_masters.upi_new_errorcode_respcd_master.approvedflag = 'TD'
3. For business declined: upi_masters.upi_new_errorcode_respcd_master.approvedflag = 'BD'
4. For approved or successful: upper(trim(currstatusdesc)) IN ('SUCCESS', 'DEEMED', 'PARTIAL')

### Transaction filtering ###
1. P2P: "(trim(pycode)) in ('NULL','0000','')"
2. P2M: "(trim(pycode)) not in ('NULL','0000','7407','')"
3. P2PM: "(trim(pycode)) in ('7407')"
4. Autopay: "initmode='11' and purposecode='14'"
5. UPI International: "initmode='12' and payeracctype in ('NRE', 'NRO')"
6. Tap and Pay: "initmode='06'"
7. UPI-LITE-X: "initmode='06' and purposecode='45'"
8. UPI-LITE: "purposecode in ('41','42','43','44')"
9. RCC_ON_UPI/CC_ON_UPI: "payeracctype='CREDIT'"
10. Credit Line: "payeracctype in ('CREDITLINE', 'CREDITLINE01', ... 'CL015')"
11. UPI circle: "purposecode='87'"
12. UPI IPO: "purposecode='01' and pycode='6211' and initmode in ('11','13')"
13. UPI-Mandate: "purposecode='76' and pycode='6211' and initmode in ('11','13')"

### SQL condition for VPA filtering ###
1. PhonePe: split(lower(trim(prfvaddr)),'@')[2] in ('axl','ibl','ybl')
2. Paytm: split(lower(trim(prfvaddr)),'@')[2] in ('paytm','ptyes','ptaxis','pthdfc','ptsbi','pytm0123456.ifsc.npci')
3. GooglePay: split(lower(trim(prfvaddr)),'@')[2] in ('okaxis','okhdfcbank','okicici','oksbi','okpayaxis', 'okbizaxis','okbizicici')
4. BHIM: split(lower(trim(prfvaddr)),'@')[2] in ('upi')

### Join Conditions ###
- Join with upi_mcc_master on prcode/pycode = mcc_code (for merchant details)
- Join with upi_new_errorcode_respcd_master on errorcode/finalrespcode (for error/decline details)
- Join with ifsc_lgpincode_master on prifsccode/pyifsccode = ifsc (for location details)
- Join with urcs_bank_master on nfsparticipantid (for bank details)

### SQL Generation Steps ###
1. Select appropriate columns from schema
2. Apply date filter using asdt column
3. Add necessary aggregations
4. Include proper grouping
5. Apply case transformations for text fields
[/INST]""",
                user_prompt_template="""Generate SQL for this refined query:

{input}

{context}

Generate only the SQL query without explanations.

SQL Query:""",
                description="SQL generation from refined NLQ"
            )
        )
        
        # Ambiguity Detection - Detect ambiguity in queries
        self.register(
            "ambiguity_detection",
            CustomInstruction(
                name="ambiguity_detection",
                system_prompt="""You are an expert at analyzing natural language for ambiguity and clarity.
Assess whether queries are clear or contain ambiguous terms that need clarification.

Consider ambiguity in:
- Temporal references (which time period?)
- Entity references (which specific user/merchant?)
- Aggregation level (per day/week/month?)
- Business logic (which transaction type?)
- Data sources (which table/system?)

Provide clear classification and explanation.""",
                user_prompt_template="""Analyze this query for ambiguity:

{input}

{context}

Provide:
1. Classification: Ambiguous or Clear
2. Identified ambiguities (if any)
3. Suggested clarifications

Assessment:""",
                description="Detect ambiguity in queries"
            )
        )
    
    def register(self, key: str, instruction: CustomInstruction):
        """Register a custom instruction"""
        self.instructions[key] = instruction
    
    def get(self, key: str) -> Optional[CustomInstruction]:
        """Get a custom instruction by key"""
        return self.instructions.get(key)
    
    def list_all(self) -> Dict[str, str]:
        """List all registered instructions with descriptions"""
        return {
            key: inst.description 
            for key, inst in self.instructions.items()
        }
    
    def add_custom(self, name: str, system_prompt: str, user_prompt_template: str,
                   description: str = "") -> str:
        """
        Add a custom instruction at runtime.
        Returns the key for the instruction.
        """
        key = f"custom_{name}"
        instruction = CustomInstruction(name, system_prompt, user_prompt_template, description)
        self.register(key, instruction)
        return key


# Global registry instance
_registry = InstructionRegistry()


def get_registry() -> InstructionRegistry:
    """Get the global instruction registry"""
    return _registry


def get_instruction(key: str) -> Optional[CustomInstruction]:
    """Get an instruction from the global registry"""
    return _registry.get(key)


def register_instruction(key: str, instruction: CustomInstruction):
    """Register an instruction in the global registry"""
    _registry.register(key, instruction)


def add_custom_instruction(name: str, system_prompt: str, user_prompt_template: str,
                          description: str = "") -> str:
    """Add a custom instruction at runtime"""
    return _registry.add_custom(name, system_prompt, user_prompt_template, description)
