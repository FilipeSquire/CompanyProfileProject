revenue_pairs = [
    (
        ["FIND THE VARIABLES 'Revenue' and 'Turnover'. FILES FROM 2024."],
    ),
    (
        ['This section provides the revenue segmentation of the company’s latest available revenue/turnover in the form of a table, using the latest available annual report/financial statement of the company: -- This can be revenue by geography, customer geography, products, type of business, business segments or/and any other type of split. If any of this type is not available, include what the company reports, as it is -- If multiple types of revenue segmentations are available e.g. revenue split by geography and revenue split by business segments, provide both of them, as reported in the report -- For the revenue split, using the actual values of each segment, calculate percentage shares -- Report both actual values and the percentage shares for each -- Make sure the total of the split must always be the same as the total revenue/turnover of the latest year']
    )
]

section4a = """
4a. Products/Services Overview:
- This section details out all the products and service offering of the company, using the latest available annual reports/financial statements of the company as well as Web Search
-- Include each product/service with a high-level brief description, in a sentence format
- Sources to be used for this section: 
-- This information should be sourced through Web Search, using company’s official website. The Web Search can be complemented by using Primary Activity, Business Review, Introduction or Strategic Report section of the annual report
-- If any of the above source suggestions does not return results for any part, please scan and check other sections of the reports or do Web Search to see if relevant information can be found
- Notes for this section:
-- If this information is unavailable, please suggest so, rather than including incorrect information
"""

section4b = """
4b. Geographical Footprint:
- This section details out all the facilities of the company including its offices, manufacturing facilities, sales offices etc., using the latest available annual reports/financial statements of the company as well as Web Search
-- List down the countries the company operates in a table format, which indication of there is an office, manufacturing facility or sales office in that particular country
- Sources to be used for this section: 
-- This information should be sourced through Web Search, using company’s official website. The Web Search can be complemented by using Primary Activity, Business Review, Introduction or Strategic Report section of the annual report 
-- If any of the above source suggestions does not return results for any part, please scan and check other sections of the reports or do Web Search to see if relevant information can be found
- Notes for this section:
-- If this information is unavailable, please suggest so, rather than including incorrect information
"""

section5 = """
5. Key Recent Developments:
- This section includes the latest 8-10 available news of the company in reverse chronological order of release date, using Web Search, complemented by annual reports/financial statements:
-- These news must be formatted in bullet points, with each bullet starting with Mmm-yy (e.g. Jun-24: Ferrari acquired XYZ...), and must contain full proper sentences without the use of semi-colons
-- Each bullet point must start with the company name (e.g. Jun-24: Ferrari acquired XYZ) 
-- Include developments from the last three years maximum, not older than that
-- Everything reported cannot be considered as news. For e.g. “In 2023, Company recorded a profit of £xx” is not considered as a news as it is a trading update. However, “In 2023, the company refinanced its loan maturing in Dec-24” is a news.
-- Following news are priority, other news must not be included: (1) Debt issuance or debt refinancing within the company (2) restructuring (primarily debt but can be operational too)within the company,(3) Mergers, acquisitions and divestments completed by the company (4)Credit Ratings published by Moody’s, Fitch or S&P,(5)Equity investment within the company by owners/acquirers (6) Changes in management personnel within the company (especially CEO, CFO, Directors and Chair), (7) Facility and operations openings/expansion/closures, (8) Dividends payment/share repurchase etc.
- Sources to be used for this section: 
-- Key news should be sourced using Web Search, particularly from the news sections on the company’s official website, as well as news articles posted by news outlet (e.g. Yahoo Finance, BBC etc.). Web Search can be complemented by any important news/developments reported in the annual reports/financial statements
- Notes for this section:
-- If key developments are limited, you can just provide a few of them, not 8-10, as long as they are relevant. However, if there is n
"""

finance_pairs = [
    (
        ["FIND THE VARIABLES 'Net cash from operating activities' and 'Net cash used in investing activities' and 'Interest Paid' in the statement of cash flows. FILES FROM 2024."],
        ["FIND THE VARIABLES 'Revenue'/'Turnover'/'Turn Over' in the Income statement. FILES FROM 2024."],
        ["FIND THE VARIABLES 'Gross Profit' and 'Cost of Goods Sold' in the Income statement. FILES FROM 2024."],
        ["FIND THE VARIABLES 'EBITDA' and 'Adjusted EBITDA' and 'Operating Profit' and 'Depreciation and Amortization' in the Income statement. FILES FROM 2024."],
        ["FIND THE VARIABLES 'Revenue'/'Turnover'/'Turn over' and 'RevenueT0' and 'RevenueT' and 'Revenue Growth' in the Income statement. FILES FROM 2024."],
        ["FIND THE VARIABLES 'Gross Profit' and 'Revenue'/Turnover/Turn over and 'Gross Margin' in the Income statement. FILES FROM 2024."],
        ["FIND THE VARIABLES 'EBITDA' and 'Revenue'/Turnover/Turn over  and 'Gross Margin' in the income statement. FILES FROM 2024."],
        ["FIND THE VARIABLES 'Net Cash Flow from Operating Activities' and 'Net Working Capital' in the cash flow statement. FILES FROM 2024."],
        ["FIND THE VARIABLES 'Debtors/Receivables' and 'Inventory/Stock' and 'Creditors/Payables' in Cash Flows from Operating Activities. FILES FROM 2024."],
        ["FIND THE VARIABLES 'Acquisition of Property' and 'Acquisition of Intangible Assets' in Investing Activities in Cash Flows Statement. FILES FROM 2024."],
        ["FIND THE VARIABLES 'Net Cash Flow from Investing Activities' and 'Net Cash Flow from Operating Activities' in Cash Flows Statement. FILES FROM 2024."],
        ["FIND THE VARIABLES 'Net Cash Flow from Financing Activities' and 'debt repayment' and 'debt issuance' and 'share issuance' and 'Interest Paid' in Cash Flows Statement. FILES FROM 2024."],
        ["FIND THE VARIABLES 'opening cash' in the cash flow statement. FILES FROM 2024."],
        ["FIND THE VARIABLES 'change in cash' in the cash flow statement. FILES FROM 2024."],
        ["FIND THE VARIABLES 'foreign exchange gains' and 'foreign exchange losses' in the cash flow statement. FILES FROM 2024."],
        ["FIND THE VARIABLES 'closing cash' in the cash flow statement. FILES FROM 2024."],
        ["FIND THE VARIABLES 'Bank Debt' and 'Lease Liabilities' from Debt/Bank Debt/Borrowings/Creditors section. FILES FROM 2024."],
        ["FIND THE VARIABLES 'Total Debt' and 'Net Debt' and 'Closing Cash'. FILES FROM 2024."],
        ["FIND THE VARIABLES 'Leverage' and 'Net Debt' and 'EBITDA'. FILES FROM 2024."],
    ),
    (
        ['CFADS (calc. Net cash from operating activities + Net cash used in investing activities). In case Interest Paid is reported under Cash Flow from Operating Activities (rather than Cash Flow from Financing Activities), the formula should change to: Net cash from operating activities + Net cash used in investing activities - Interest Paid. Show me the formula with values and final result.'],
        ['Revenue/Turnover/Turn over (Use Income Statement – Always Given)'],
        ['Gross Profit (Use Income Statement – Always Given): Revenue/Turnover/Turn over – Cost of Goods Sold (ONLY use this formula if the report does not already provide the gross profit value)'],
        ['EBITDA (Check all sections of the report, EBITDA or Adjusted EBITDA might be provided – If not provided, calculate manually): Operating Profit + Depreciation and Amortization (ONLY use this formula if the report does not already provide the EBITDA/Adjusted EBITDA value) — Revenue Growth % (Always Calculate Manually): (RevenueT0÷RevenueT−1)−1'],
        ['Revenue/Turnover/Turn over Growth % (Always Calculate Manually): (RevenueT0÷RevenueT−1)−1'],
        ['Gross Margin % (Always Calculate Manually): Gross Profit / Revenue aka Turnover or Turn Over'],
        ['EBITDA Margin % (Always Calculate Manually): EBITDA / Revenue (put n.m. if it is negative)'],
        ['Cash Flow from Operating Activities excl. Net Working Capital (Use Cash Flow Statement – Always Calculate Manually): Net Cash Flow from Operating Activities – Net Working Capital (Net Working Capital should be the one calculated below). In case Interest Paid is reported under Cash Flow from Operating Activities (rather than Cash Flow from Financing Activities), the formula should change to: Net Cash Flow from Operating Activities – Net Working Capital - Interest Paid'],
        ['Net Working Capital (Use Cash Flow Statement – Always Calculate Manually): Increase/Decrease in Debtors/Receivables + Increase/Decrease in Inventory/Stock + Increase/Decrease in Creditors/Payables (These values are usually provided under Cash flows from Operating Activities section of Cash Flow Statement and should be used as it is for calculation (do not change its signs e.g. change from negative to positive))'],
        ['Capex (Use Cash Flow Statement – Always Calculate Manually): Acquisition of Property, Plant, Equipment/Tangible Assets + Acquisition of Intangible Assets (These values are usually provided under Cash flows from Investing Activities section of Cash Flow Statement)'],
        ['Other Cash Flow from Investing Activities (Use Cash Flow Statement – Always Calculate Manually): Net Cash Flow from Investing Activities – Capex (Capex should be the one calculated above)'],
        ['Cash Flow from Financing Activities (Use Cash Flow Statement – Always Given): This should include the net total and below it there should be a breakdown of sub-items comprised in the financing cash flow and their contribution to this net number e.g. debt repayment, debt issuance, share issuance, interest paid etc. If Interest Paid is part of Cash Flow from Operating Activities, calculate Cash Flow from Financing Activities manually using the formula: net cash from financing activities + Interest Paid)'],
        ['Opening Cash (Use Cash Flow Statement – Always Given)'],
        ['Change in Cash (Use Cash Flow Statement – Always Given)'],
        ['Foreign Exchange Gains/Losses (Use Cash Flow Statement – Always Given)'],
        ['Closing Cash (Use Cash Flow Statement – Always Given).'],
        ['Total Debt (From Debt or Bank Debt or Borrowings or Creditors section – Always Calculate Manually): Bank Debt + Lease Liabilities (This only includes external debt e.g. bank loans, bonds, RCFs etc. and lease liabilities (only financial leases, not operating leases), and no internal debt (e.g. shareholder loans, loans from related parties, loans from subsidiaries etc.)) '],
        ['Net Debt (Always Calculate Manually): Net Debt: Total Debt – Closing Cash'],
        ['Leverage (Always Calculate Manually): Net Debt / EBITDA (put n.m. if it is negative)'],
    )
]


# CAPITAL STRUCTURE

capital_pairs = [
    (
        [f"FIND THE VARIABLES 'Term Loan' and 'Senior Secured Notes' and 'debt facilities' and 'RCF'. FILES FROM {datetime.now().year - 1 }."],
        [f"FIND THE VARIABLES 'Interest Rate' and 'EURIBOR'. FILES FROM {datetime.now().year - 1 }."],
        [f"FIND THE VARIABLES 'Debt Facility' and 'Maturity'. FILES FROM {datetime.now().year - 1 }."],
        [f"FIND THE VARIABLES 'Debt Facility' and 'Maturity' and 'Amount Outstanding'. FILES FROM {datetime.now().year - 1 }."],
        [f"FIND THE VARIABLES 'Gross External Debt' and 'Debt' and 'debt facilities' and 'facility'. FILES FROM {datetime.now().year - 1 }."],
        [f"FIND THE VARIABLES 'Cash' and 'Closing Cash' and 'facilities' and 'facility'. FILES FROM {datetime.now().year - 1 }."],
        [f"FIND THE VARIABLES 'Gross Debt' and 'Closing Cash' and 'facilities' and 'facility'. FILES FROM {datetime.now().year - 1 }."],
        [f"FIND THE VARIABLES 'Closing Cash' and 'RCF' and 'facilities' and 'facility'. FILES FROM {datetime.now().year - 1 }."],
        [f"FIND THE VARIABLES 'EBITDA' and 'facilities' and 'facility'. FILES FROM {datetime.now().year - 1 }."],
        [f"FIND THE VARIABLES 'EBITDA' and 'Net Debt' and 'facilities' and 'facility'. FILES FROM {datetime.now().year - 1 }."]
    ),
    (
        ['Name of the Facility (e.g. £300m Term loan, $200m RCF, £100m Senior Secured Notes etc.)'],
        ['Interest Rate (e.g. 5.25%, EURIBOR + 3.75% etc.)'],
        ['Maturity (This is the latest repayment date of the debt facility. It should be provided in the format mmm-yy e.g. Jun-25)'],
        ['Amount Outstanding - This is the amount utilized and needs to be repaid (Provide it in millions, rounded to 1 decimal point e.g. £1.2m)'],
        ['Gross External Debt (Sum of amount outstanding for all debt facilities). Lease liabilities is also counted as a debt facility (only financial leases, no operational leases). Internal loans such as Shareholder loans, loans from related parties, loans from subsidiaries MUST never be included.'],
        ['Closing Cash . Lease liabilities is also counted as a debt facility (only financial leases, no operational leases). Internal loans such as Shareholder loans, loans from related parties, loans from subsidiaries MUST never be included.'],
        ['Net External Debt (Gross Debt – Closing Cash).Always calculate manually. Lease liabilities is also counted as a debt facility (only financial leases, no operational leases). Internal loans such as Shareholder loans, loans from related parties, loans from subsidiaries MUST never be included.'], 
        ['Liquidity (Closing cash + any undrawn facilities, e.g. undrawn amount of RCF, credit lines or overdrafts). Provide this in millions, rounded to 1 decimal place (e.g. £1.2m). E.g. liquidity can be £2.5m closing cash + £35m undrawn RCF, a total of £37.5m of liquidity'],
        ['EBITDA'],
        ['Leverage (Net Debt / EBITDA)']
    )
]


stakeholders_pairs = [
    (
        ["FIND THE VARIABLES 'Parent' and 'Ultimate Parent' and 'Immediate Parent'. FILES FROM 2024."],
        ["FIND THE VARIABLES 'Directors' and 'Company Information' FILES FROM 2024."],
        ["FIND THE VARIABLES 'Bank loans' and 'loan' and 'borrowings' and 'bank' and 'creditors' and 'bank borrowings' and 'bonds' and 'syndicate' and 'secured notes' and 'unsecured notes' and 'facility agent'. FILES FROM 2024."],
        ["FIND THE VARIABLES 'Auditor' and 'Independent Auditor' and 'Company Information'. FILES FROM 2024."],
        ["FIND THE VARIABLES 'Company Information' and 'Solicitors' and 'Bankers' and 'Facility Agent'. FILES FROM 2024."],
        ),
    (
        ['Shareholders (Provide the immediate parent company and ultimate parent company of the target company in the case of a private company. In the case of a public company, provide top 5 shareholders of the company with % owned) '],
        ['Management (Include the name of the chairman, Chief Executive Officer and Chief Financial Officer. If these three are not available provide the name of the Directors listed in the report) '],
        ['Lenders (Include the name of the lenders of the company for each of the debt facility, if reported). No need to add lenders for internal debt (shareholder loans, loans from related parties etc.)'],
        ['Auditors (Provide the name of the independent auditor/auditor of the company mentioned in the report)'],
        ['Advisors (Provide any financial or legal advisors, solicitors, bankers, facility agent listed in the report). Do not include lenders'],
    )
]

biz_overview_pairs = [
    (
        ["Find the variables 'Primary Activity', 'Business Review', 'Introduction', 'Bank Debt/Borrowings/Creditors'"],
        ),
    (
        ["This section provides a high-level overview on what the company does, its operations, locations, products, customers and any ongoing debt/financial issues, in a bullet point format consisting of 6-7 bullet points with sentences, using the latest available annual reports/financial statements of the company — Include 1-2 bullet point sentences on what the company does — Include 1 bullet point on the products/services the company offers — Include 1 bullet point on where the company has its operations (e.g. manufacturing facilities, operating plants, offices, customers) — Include 1 bullet point on who are the customers of the company — If available, include 1 bullet point on any important key news of the company in the last one year (e.g. new owner, important acquisition/divestment, refinancing etc.) - Include 1 bullet point on stress triggers of the company (e.g., 40% revenue from top 1 customer; high fixed costs; collateral shortfall; aggressive capex; covenant breach; dropping profitability; mass lay-offs, approaching maturities etc.)"],
    )
]

biz_overview_web = """
- This section provides a high-level overview on what the company does, its operations, locations, products, customers and any ongoing debt/financial issues, in a bullet point format consisting of 5-6 bullet points with sentences:
-- Include 1-2 bullet point sentences on what the company does
-- Include 1 bullet point on the products/services the company offers
—- If the company is owned by a private equity firm, include 1 bullet point on who owns its and when they bought the stake in the company
-- Include 1 bullet point on where the company has its operations (e.g. manufacturing facilities, operating plants, offices, customers)
-- Include 1 bullet point on who are the customers of the company 
—- If available, include 1 bullet point on any important key news of the company in the last one year (e.g. new owner, important acquisition/divestment, refinancing etc.)
-- Include 1 bullet point on the latest Credit Ratings from all three outlets (Moody’s, S&P and Fitch), where available (e.g. Fitch rated Company BBB+/Stable in Oct-25; Moody’s downgraded Company Rating to B-/Negative in Aug-25 etc.)
- Each bullet must begin with the company name, "The company", or “It”. Make sure each bullet point is a proper sentence, which do not contain any sub-headings, colon or semi-colons
- Sources to be used for this section: 
-- The bullet points regarding what the company does, its products/services, operations, customers can be sourced through Web Search, using the company’s official website. The Web Search can be complemented by using Primary Activity, Business Review, Introduction or Strategic Report section of the annual report
-- The bullet point regarding Credit Ratings can be sourced through Web Search, using press articles from Moody’s, S&P and Fitch
- Notes for this section:
-- If information for any of the bullet point is not available through Web Search, do not include that specific bullet point as incorrect information is strictly prohibited
"""

stakeholders_web = """ 

6. Key Stakeholders:
- This section provides key stakeholders of the company in a table format, including the following, using the available annual reports/financial statements of the company, as well as Web Search:
-- Shareholders (Provide the immediate parent company and ultimate parent company of the target company in the case of a private company. In the case of a public company, provide top 5 shareholders of the company with % owned)
-- Management (Include the name of the chairman, Chief Executive Officer and Chief Financial Officer. If these three are not available provide the name of the Directors listed in the annual report)
-- Lenders (Include the name of the lenders of the company for each of the debt facility, if reported)
-- Advisors (Provide any financial or legal advisors, solicitors or bankers of the company)
-- Charges (Provide the list of Charges (Outstanding ONLY), their issue date and persons entitled using Companies House website)


- Sources to be used for this section: 
-- Shareholders will be available under the Parent Company section of the annual report, or throughout text in different sections, for private companies. For public limited companies, the top shareholders will be listed in the Shareholders section of the annual report. However, for public limited companies if it is not available in the report, Use Web Search to obtain to this information, as a backup option
-- Management will be available on the company’s official website, using Web Search. If a website is not available, check Company Information or Strategic Report or Key Management or Board of Directors section of the annual report
-- Use Web Search to search for press articles that has name of lenders for the debt facilities
-- Advisors need to be checked using Web Search, particularly for press articles related to debt issuance or M&A, that might provide name of the advisors, in addition to offering memorandum of debt if available. 


- Notes for this section:
-- Put n/a for any part not available in the report or through Web Search, rather than reporting incorrect information

"""