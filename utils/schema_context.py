"""
Database schema context for UPI transaction analysis
"""

SCHEMA_CONTEXT = """
### Database Schema ###

**Main Table: upi_txn.urcs_ft_txns**
UPI transaction details with columns:
- prdmobile: Payer mobile number (VARCHAR)
- prdfname: Payer first name (VARCHAR)
- prdlname: Payer last name (VARCHAR)
- prfvaddr: Payer VPA/virtual address (VARCHAR)
- prifsccode: Payer IFSC code (VARCHAR)
- praccno: Payer account number (VARCHAR)
- prcode: Payer merchant code (VARCHAR)
- prnfsparticipantid: Payer bank NFS participant ID (VARCHAR)
- pramount: Payer amount (DOUBLE)
- transdesc: Transaction description (VARCHAR)
- currstatusdesc: Current status description (VARCHAR) - VALUES: 'SUCCESS', 'FAILURE', 'DEEMED', 'PARTIAL'
- asdt: Transaction date (VARCHAR, format: YYYY-MM-DD)
- errorcode: Error code (VARCHAR)
- finalrespcode: Final response code (VARCHAR)

- pydmobile: Payee mobile number (VARCHAR)
- pydfname: Payee first name (VARCHAR)
- pydlname: Payee last name (VARCHAR)
- prfvaddr: Payee VPA/virtual address (VARCHAR)
- pyifsccode: Payee IFSC code (VARCHAR)
- pyaccno: Payee account number (VARCHAR)
- pycode: Payee merchant code (VARCHAR) - '0000' = Non-merchant, 'NULL' = Non-merchant
- pynfsparticipantid: Payee bank NFS participant ID (VARCHAR)
- txnamount: Transaction amount (BIGINT, in paise - divide by 100 for rupees)
- payeracctype: Payer account type (VARCHAR)
- purposecode: Purpose code for transaction (VARCHAR)
- initmode: Initiation mode (VARCHAR)

**Reference Tables:**

1. **upi_mcc_master** - Merchant Category Code master
   - mcc_code: MCC code (VARCHAR)
   - mcc_description: Description (VARCHAR)

2. **upi_new_errorcode_respcd_master** - Error/Response code master
   - error_code: Error code (VARCHAR)
   - respcd: Response code (VARCHAR)
   - error_description: Error description (VARCHAR)
   - approvedflag: Approval flag (VARCHAR) - VALUES: 'TD' (Technical Decline), 'BD' (Business Decline), 'A' (Approved)

3. **ifsc_lgpincode_master** - Bank location master
   - ifsc: IFSC code (VARCHAR)
   - bankname: Bank name (VARCHAR)
   - state: State (VARCHAR)
   - city: City (VARCHAR)

4. **urcs_bank_master** - Bank master
   - nfsparticipantid: Bank NFS participant ID (VARCHAR)
   - bankname: Bank name (VARCHAR)
   - bankcode: Bank code (VARCHAR)

### Transaction Types ###
- P2P (Person-to-Person): pycode IN ('NULL', '0000', '')
- P2M (Person-to-Merchant): pycode NOT IN ('NULL', '0000', '7407', '')
- P2PM (Person-to-Payment Manager): pycode IN ('7407')
- Autopay: initmode='11' AND purposecode='14'
- UPI International (IUPI): initmode='12' AND payeracctype IN ('NRE', 'NRO')
- Tap and Pay: initmode='06'
- UPI-LITE-X: initmode='06' AND purposecode='45'
- UPI-LITE: purposecode IN ('41','42','43','44')
- RCC/CC on UPI: payeracctype='CREDIT'
- Credit Line: payeracctype IN ('CREDITLINE', 'CREDITLINE01', ..., 'CL015')
- UPI Circle: purposecode='87'
- UPI IPO: purposecode='01' AND pycode='6211' AND initmode IN ('11','13')
- UPI-Mandate: purposecode='76' AND pycode='6211' AND initmode IN ('11','13')

### App/Wallet Identification (via VPA domain) ###
Extract domain from prfvaddr using: split(lower(trim(prfvaddr)),'@')[2]
- PhonePe: domains = ('axl', 'ibl', 'ybl')
- Paytm: domains = ('paytm', 'ptyes', 'ptaxis', 'pthdfc', 'ptsbi', 'pytm0123456.ifsc.npci')
- Google Pay: domains = ('okaxis', 'okhdfcbank', 'okicici', 'oksbi', 'okpayaxis', 'okbizaxis', 'okbizicici')
- BHIM: domain = 'upi'

### Transaction Status ###
- Successful/Approved: currstatusdesc IN ('SUCCESS', 'DEEMED', 'PARTIAL')
- Failed/Declined: currstatusdesc IN ('FAILURE')
- Technical Decline: approvedflag = 'TD' (from upi_new_errorcode_respcd_master)
- Business Decline: approvedflag = 'BD' (from upi_new_errorcode_respcd_master)

### Key Join Conditions ###
- Transaction + MCC Master: prcode = mcc_code OR pycode = mcc_code
- Transaction + Error Master: errorcode = error_code OR finalrespcode = respcd
- Transaction + IFSC Master: prifsccode = ifsc OR pyifsccode = ifsc
- Transaction + Bank Master: prnfsparticipantid = nfsparticipantid OR pynfsparticipantid = nfsparticipantid
"""


def get_schema_context() -> str:
    """Get the complete schema context for UPI transactions"""
    return SCHEMA_CONTEXT
