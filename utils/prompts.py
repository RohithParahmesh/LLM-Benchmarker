nlq_prompt_template = """[INST] 
Refine this natural language query into a precise SQL generation command using these guidelines.

### Task ###
Generate:
1. Improved natural language query
2. Combined column list

### Format Requirements ###
Strictly follow:
Refined Query: [text]
required_columns = ["column1", "column2"]

### Database Schema Context ###
{schema_context}

### Conversion Rules ###
1. Map colloquial terms to the schema columns (example: "mobile number" -- "prdmobile", "merchant code" -- "pycode")
2. Explicitly state JOIN conditions using schema relationships.

### Filtering Guidelines ###
1. For all VARCHAR fields in schema mention to use UPPER(TRIM(column_name)) for consistency except for "asdt" 

### Transaction filtering ###
1. For P2P or person to person transactions mentioned in the where conditions use this condition "(trim(pycode)) in ('NULL','0000','')" in where clause
2. For P2M transactions mentioned in the where conditions use this condition "(trim(pycode)) not in ('NULL','0000','7407','')" in where clause
3. For P2PM transactions mentioned in the where conditions use this condition "(trim(pycode)) in ('7407')" in where clause
4. For Autopay transactions mentioned in the where conditions, use this condition "initmode='11' and purposecode='14'" in where clause
5. For UPI International or IUPI transactions in the where conditions, use this condition "initmode='12' and payeracctype in ('NRE', 'NRO')" in where clause
6. For Tap and Pay transactions mentioned in where conditions, use this condition " initmode='06'" in where clause
7. For UPI-LITE-X transactions mentioned in the where conditions, use this condition "initmode='06' and purposecode='45'" in where clause
8. For UPI-LITE transactions mentioned in the where conditions, use this condition "purposecode in ('41','42','43','44') in where clause
9. For RCC_ON_UPI or CC_ON_UPI mentioned in the where conditions, use this condition "payeracctype='CREDIT'" in where clause
10. For Credit Line transactions mentioned in the where conditions, use this condition "payeracctype in ('CREDITLINE',  'CREDITLINE01' , 'CREDITLINE02', 'CREDITLINE03','CREDITLINE04', 'CREDITLINE05','CREDITLINE06', 'CREDITLINE07','CREDITLINE08', 'CREDITLINE09','CREDITLINE10', 'CL01',  'CL02', 'CL03', 'CL04','CL05', 'CL06', 'CL07', 'CL08', 'CL09', 'CL10'     'CL011', 'CL012', 'CL013', 'CL014','CL015' )" in where clause
11. For UPI circle transactions mentioned in the where conditions, use this condition "purposecode='87'" in where clause
12. For UPI IPO transactions mentioned in the where conditions, use this condition "purposecode='01' and pycode='6211' and initmode in ('11','13')" in where clause
13. For UPI-Mandate transactions mentioned in the where conditions, use this condition "purposecode='76' and pycode='6211' and initmode in ('11','13')" in where clause


### SQL condition for VPA filtering ###
1. For PhonePe: split(lower(trim(prfvaddr)),'@')[2] in ('axl','ibl','ybl') then  'phonepe' 
2. For Paytm: split(lower(trim(prfvaddr)),'@')[2] in ('paytm','ptyes','ptaxis','pthdfc','ptsbi','pytm0123456.ifsc.npci') then  'paytm payments bank app'
3. For GooglePay: split(lower(trim(prfvaddr)),'@')[2] in ('okaxis','okhdfcbank','okicici','oksbi','okpayaxis', 'okbizaxis','okbizicici') then  'google pay'
4. For BHIM: split(lower(trim(prfvaddr)),'@')[2] in ('upi') then  'bhim'

### SQL condition for success and failure ###
1. For where conditions on declined or failed transactions, use upper(trim(currstatusdesc)) IN ('FAILURE').
2. For where conditions on technical declined transactions, use upi_masters.upi_new_errorcode_respcd_master.approvedflag = 'TD'.
3. For where conditions on business declined transactions, use upi_masters.upi_new_errorcode_respcd_master.approvedflag = 'BD'.
4. For where conditions on approved or successful transactions, use upper(trim(currstatusdesc)) IN ('SUCCESS', 'DEEMED', 'PARTIAL').

### Formatting Guidelines ###
1. Start with action verb: "Generate/Fetch/Build an SQL query..."
2. Use exact column names from schema.
3. Preserve original query intent. Use exact schema names.
3. Do not give any explanation or do not generate any SQL code. Explicitly convert the user input into SQL command.

### Join Conditions ###
- Join upi_txn.urcs_ft_txns with upi_masters.upi_mcc_master on prcode = mcc_code -- join when payer is merchant and to get code from desription 
- Join upi_txn.urcs_ft_txns with upi_masters.upi_mcc_master on pycode = mcc_code -- join when payee is merchant and to get code from description
- Join upi_txn.urcs_ft_txns with upi_masters.upi_new_errorcode_respcd_master on errorcode = error_code -- join to get the deatils of error description or BUSINESS/TECHNICAL DECLINE flags in approvedflag column
- Join upi_txn.urcs_ft_txns with upi_masters.upi_new_errorcode_respcd_master on finalrespcode = respcd -- join to get the deatils of response code description or BUSINESS/TECHNICAL DECLINE flags in approvedflag column
- Join upi_txn.urcs_ft_txns with upi_masters.ifsc_lgpincode_master on prifsccode = ifsc -- join to get the deatils of location of the payer
- Join upi_txn.urcs_ft_txns with upi_masters.ifsc_lgpincode_master on pyifsccode = ifsc -- join to get the deatils of location of the payee
- Join upi_txn.urcs_ft_txns with upi_masters.urcs_bank_master on prnfsparticipantid = nfsparticipantid -- join to get the deatils of the bank code or bank full name
- Join upi_txn.urcs_ft_txns with upi_masters.urcs_bank_master on drnfsparticipantid = nfsparticipantid -- join to get the deatils of the bank code or bank full name
- Join upi_txn.urcs_ft_txns with upi_masters.urcs_bank_master on crnfsparticipantid = nfsparticipantid -- join to get the deatils of the bank code or bank full name
- Join upi_txn.urcs_ft_txns with upi_masters.urcs_bank_master on pynfsparticipantid = nfsparticipantid -- join to get the deatils of the bank code or bank full name


Examples: {nlq_examples}

### Current Request ###
Convert this: "{user_question}" 
[/INST]
<think>
{user_question}
</think>"""


sql_instructions  = """
### Handling Dates ###
1. Read dates from the form: "fromDate: , toDate: "
2. For date fields in the WHERE clause, use date (a VARCHAR column) formatted as YYYY-MM-DD.
3. To convert date to a DATE by using CAST(asdt AS DATE) in SELECT clauses (but do not use CAST in WHERE clauses).
4. If the date is not mentioned anywhere by the user please consider asdt = current date

### Amount and Aggregations ###
1. For total amount, spends, revenue, or sum of amounts, use CAST(SUM(txnamount) AS DOUBLE) / 100.
2. For transaction count or volume, use COUNT(*).
3. Average Transaction Value (ATV): calculate as CAST(SUM(txnamount) AS DOUBLE) / COUNT(*).
4. Unique or distinct user count: calculate as count(prdmobile)
5. GROUP BY clause cannot contain aggregations, window functions or grouping operations

### String Handling Consistency ###
1. Apply upper(trim(column)) to all VARCHAR fields in the schema for consistency except for "asdt"
2. For the merchant conditions kindly use the "like" function instead of "="
3. For bin-based queries, use the first six digits: SUBSTR((praccno), 1, 6).

### SQL condition for success and failure ###
1. For where conditions on declined or failed transactions, use upper(trim(currstatusdesc)) IN ('FAILURE').
2. For where conditions on technical declined transactions, use upi_masters.upi_new_errorcode_respcd_master.approvedflag = 'TD'.
3. For where conditions on business declined transactions, use upi_masters.upi_new_errorcode_respcd_master.approvedflag = 'BD'.
2. For where conditions on approved or successful transactions, use upper(trim(currstatusdesc)) IN ('SUCCESS', 'DEEMED', 'PARTIAL').

### Transaction filtering ###
1. For P2P or person to person transactions mentioned in the where conditions use this condition "(trim(pycode)) in ('NULL','0000','')" in where clause
2. For P2M transactions mentioned in the where conditions use this condition "(trim(pycode)) not in ('NULL','0000','7407','')" in where clause
3. For P2PM transactions mentioned in the where conditions use this condition "(trim(pycode)) in ('7407')" in where clause
4. For Autopay transactions mentioned in the where conditions, use this condition "initmode='11' and purposecode='14'" in where clause
5. For UPI International or IUPI transactions in the where conditions, use this condition "initmode='12' and payeracctype in ('NRE', 'NRO')" in where clause
6. For Tap and Pay transactions mentioned in where conditions, use this condition " initmode='06'" in where clause
7. For UPI-LITE-X transactions mentioned in the where conditions, use this condition "initmode='06' and purposecode='45'" in where clause
8. For UPI-LITE transactions mentioned in the where conditions, use this condition "purposecode in ('41','42','43','44') in where clause
9. For RCC_ON_UPI or CC_ON_UPI mentioned in the where conditions, use this condition "payeracctype='CREDIT'" in where clause
10. For Credit Line transactions mentioned in the where conditions, use this condition "payeracctype in ('CREDITLINE',  'CREDITLINE01' , 'CREDITLINE02', 'CREDITLINE03','CREDITLINE04', 'CREDITLINE05','CREDITLINE06', 'CREDITLINE07','CREDITLINE08', 'CREDITLINE09','CREDITLINE10', 'CL01',  'CL02', 'CL03', 'CL04','CL05', 'CL06', 'CL07', 'CL08', 'CL09', 'CL10'     'CL011', 'CL012', 'CL013', 'CL014','CL015' )" in where clause
11. For UPI circle transactions mentioned in the where conditions, use this condition "purposecode='87'" in where clause
12. For UPI IPO transactions mentioned in the where conditions, use this condition "purposecode='01' and pycode='6211' and initmode in ('11','13')" in where clause
13. For UPI-Mandate transactions mentioned in the where conditions, use this condition "purposecode='76' and pycode='6211' and initmode in ('11','13')" in where clause

### SQL condition for VPA filtering ###
1. For PhonePe: split(lower(trim(prfvaddr)),'@')[2] in ('axl','ibl','ybl') then  'phonepe' 
2. For Paytm: split(lower(trim(prfvaddr)),'@')[2] in ('paytm','ptyes','ptaxis','pthdfc','ptsbi','pytm0123456.ifsc.npci') then  'paytm payments bank app'
3. For GooglePay: split(lower(trim(prfvaddr)),'@')[2] in ('okaxis','okhdfcbank','okicici','oksbi','okpayaxis', 'okbizaxis','okbizicici') then  'google pay'
4. For BHIM: split(lower(trim(prfvaddr)),'@')[2] in ('upi') then  'bhim'

### Join Conditions ###
- Join upi_txn.urcs_ft_txns with upi_masters.upi_mcc_master on prcode = mcc_code -- join when payer is merchant and to get code from desription 
- Join upi_txn.urcs_ft_txns with upi_masters.upi_mcc_master on pycode = mcc_code -- join when payee is merchant and to get code from description
- Join upi_txn.urcs_ft_txns with upi_masters.upi_new_errorcode_respcd_master on errorcode = error_code -- join to get the deatils of  error description or BUSINESS/TECHNICAL DECLINE flags in approvedflag column
- Join upi_txn.urcs_ft_txns with upi_masters.upi_new_errorcode_respcd_master on finalrespcode = respcd -- join to get the deatils of response code description or BUSINESS/TECHNICAL DECLINE flags in approvedflag column
- Join upi_txn.urcs_ft_txns with upi_masters.ifsc_lgpincode_master on prifsccode = ifsc -- join to get the deatils of location of the payer
- Join upi_txn.urcs_ft_txns with upi_masters.ifsc_lgpincode_master on pyifsccode = ifsc -- join to get the deatils of location of the payee
- Join upi_txn.urcs_ft_txns with upi_masters.urcs_bank_master on prnfsparticipantid = nfsparticipantid -- join to get the deatils of the bank code or bank full name
- Join upi_txn.urcs_ft_txns with upi_masters.urcs_bank_master on drnfsparticipantid = nfsparticipantid -- join to get the deatils of the bank code or bank full name
- Join upi_txn.urcs_ft_txns with upi_masters.urcs_bank_master on crnfsparticipantid = nfsparticipantid -- join to get the deatils of the bank code or bank full name
- Join upi_txn.urcs_ft_txns with upi_masters.urcs_bank_master on pynfsparticipantid = nfsparticipantid -- join to get the deatils of the bank code or bank full name

"""



sql_prompt_template = """ [INST] 

### Instructions:
### Filtering Guidelines:
1. For all VARCHAR fields in schema mention to use UPPER(TRIM(column_name)) for consistency except for "asdt" 

{sql_instructions}

### Examples:
{examples}

### SQL Generation Steps:
1. Select appropriate columns from schema
2. Apply date filter using asdt column
3. Add necessary aggregations
4. Include proper grouping
5. Apply case transformations for text fields

### Schema:
{schema_context}

### Current Request:
Refined NLQ: {ai_nlq}
Required columns: {required_columns}

[/INST]
<think>
{ai_nlq}
</think>retrieved_examples
### Final SQL Query:
"""

sql_prompt_template_chat = """ [INST] 

### Instructions:
You are given a sequence of past user queries, follow-ups and SQLs that were generated for them.

{prev_chat}

Now the user says:
"{user_question}"

### Task:
1. Generate an SQL satisfying the users current follow-up question, taking the chat history into consideration.

{sql_instructions}

### SQL Generation Steps:
1. Select appropriate columns from schema
2. Apply date filter using asdt column
3. Add necessary aggregations
4. Include proper grouping
5. Apply case transformations for text fields

### Schema:
{schema_context}

[/INST]
<think>
{prev_chat}

Now the user says:
"{user_question}"

Generate an SQL satisfying the users current follow-up question, taking the chat history into consideration.
</think>
### Final SQL Query:
"""


def get_nlq_prompt_template():
    return nlq_prompt_template

def get_sql_prompt_template():
    return sql_prompt_template

def get_sql_prompt_template_chat():
    return sql_prompt_template_chat

def get_sql_instructions():
    return sql_instructions

