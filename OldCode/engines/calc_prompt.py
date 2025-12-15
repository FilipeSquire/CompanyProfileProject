
"""
This file defines reusable system prompts for financial calculations.
It provides:
- calc_routing_system: Financial Highlights Table Metrics & Calculations
- Capital_Structure_Calculations: Capital Structure Metrics & Calculations
"""

calc_routing_system = """
Financial Highlights Table Metrics and Calculations:

Use the last three available annual reports/financial statements of the company.
The table should have rows (some provided directly, some calculated using formulae):

- Revenue (Use Income Statement – Always Given)
- Gross Profit (Use Income Statement – Always Given). 
  If not explicitly given, calculate: Revenue – Cost of Goods Sold.
- EBITDA. Check all sections of the report. If not given, calculate: 
  Operating Profit + Depreciation and Amortization.
- Revenue Growth % (Always Calculate Manually): (RevenueT0 ÷ RevenueT−1) − 1
- Gross Margin % (Always Calculate Manually): Gross Profit ÷ Revenue
- EBITDA Margin % (Always Calculate Manually): EBITDA ÷ Revenue (put n.m. if negative)
- Cash Flow from Operating Activities excl. Net Working Capital (Always Calculate): 
  Net Cash Flow from Operating Activities – Net Working Capital
- Net Working Capital (Always Calculate): 
  ΔDebtors/Receivables + ΔInventory + ΔCreditors/Payables 
  (Use the signs as provided in the Cash Flow Statement).
- Capex (Always Calculate): 
  Acquisition of Property, Plant & Equipment + Acquisition of Intangible Assets
- Other Cash Flow from Investing Activities (Always Calculate): 
  Net Cash Flow from Investing Activities – Capex
- CFADS (Always Calculate): 
  Net Cash Flow from Operating Activities + Net Cash Flow from Investing Activities
- Cash Flow from Financing Activities (Always Given): 
  Show sub-items like debt repayment, issuance, share issuance, etc.
- Opening Cash (Always Given)
- Change in Cash (Always Given)
- Closing Cash (Always Given)
- Total Debt (Always Calculate): Bank Debt + Lease Liabilities 
  (external debt only, no shareholder/related party debt).
- Net Debt (Always Calculate): Total Debt – Closing Cash
- Leverage (Always Calculate): Net Debt ÷ EBITDA (put n.m. if negative)
"""

Capital_Structure_Calculations = """
Capital Structure Table Metrics and Calculations:

Use the latest available annual report/financial statement. 
List out all the debt facilities with these columns:

- Name of the Facility (e.g. £300m Term loan, $200m RCF, £100m Senior Secured Notes)
- Interest Rate (e.g. 5.25%, EURIBOR + 3.75%)
- Maturity (format: mmm-yy, e.g. Jun-25)
- Amount Outstanding (in millions, rounded to 1 decimal, e.g. £1.2m)

Notes:
- Lease liabilities count as debt facilities (only financial leases).
- Do NOT include internal loans (shareholder, related parties, subsidiaries).
- All values must be in millions, rounded to 1 decimal.

The table must also include:
- Gross External Debt (sum of all facilities)
- Cash (Closing Cash)
- Net External Debt (Gross Debt – Closing Cash)
- Liquidity (Closing cash + undrawn facilities like RCF/credit lines/overdrafts)
- EBITDA
- Leverage (Net Debt ÷ EBITDA)

Ensure consistency with the Financial Highlights section.
"""
