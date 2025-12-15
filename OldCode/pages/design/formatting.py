business_overview_formatting = """
Follow the formatting and instructions for each section of the output.

**1. Business Overview**
------

- This section provides a high-level overview on what the company does, its operations, locations, products, customers and any ongoing debt/financial issues, in a bullet point format consisting of 5-6 bullet points with sentences, using the latest available annual reports/financial statements of the company as well as Web Search:
- Add a single blank line, then a heading line: **1. Business Overview**
-- Include 1-2 bullet point sentences on what the company does
-- Include 1 bullet point on the products/services the company offers
-- Include 1 bullet point on where the company has its operations (e.g. manufacturing facilities, operating plants, offices, customers)
-- Include 1 bullet point on who are the customers of the company 
-- Include 1 bullet point on stress triggers of the company (e.g., 40% revenue from top 1 customer; high fixed costs; collateral shortfall; aggressive capex; covenant breach; dropping profitability; mass lay-offs etc.)
-- Include 1 bullet point on any latest Credit Ratings from Moody’s, S&P and Fitch, if available (e.g. Fitch rated Company BBB+/Stable; Moody’s rated Company B-/Negative etc.)
- Each bullet must begin with the company name, "The company", or “It”. Make sure each bullet point is a proper sentence, which do not contain any sub-headings, colon or semi-colons

**Sources**
- Sources to be used for this section: 
-  After the previous block, add a single blank line, then a heading line: **Sources:**
-- The bullet points regarding what the company does, its products/services, operations, customers can be sourced through Web Search, using the company’s official website. The Web Search can be complemented by using Primary Activity, Business Review, Introduction or Strategic Report section of the annual report
-- The bullet point regarding company’s stress triggers can be sourced from the Business Review or Ongoing Concern or Bank Debt/Borrowings/Creditors section of the annual report
-- The bullet point regarding Credit Ratings can be sourced through Web Search, using press articles from Moody’s, S&P and Fitch
-- If any of the above source suggestions does not return results for any part, please scan and check other sections of the reports or do Web Search to see if relevant information can be found


- Notes for this section:
-- If information for any of the bullet point is not available in the report or through Web Search, do not include that specific bullet point as incorrect information is strictly prohibited

---------------
"""

biz_overview_mix_formatting = """
Follow the formatting and instructions for each section of the output.

**1. Business Overview**

- Add a single blank line, then a heading line: 1. Business Overview
- This section provides a high-level overview on what the company does, its operations, locations, products, customers and any ongoing debt/financial issues, in a bullet point format consisting of 5-6 bullet points with sentences, using all the context provided:
-- Include 1-2 bullet point sentences on what the company does
-- Include 1 bullet point on the products/services the company offers
-- Include 1 bullet point on where the company has its operations (e.g. manufacturing facilities, operating plants, offices, customers)
-- Include 1 bullet point on who are the customers of the company
-- Include 1 bullet point on stress triggers of the company (e.g., 40% revenue from top 1 customer; high fixed costs; collateral shortfall; aggressive capex; covenant breach; dropping profitability; mass lay-offs etc.)
-- Include 1 bullet point on any latest Credit Ratings from Moody's, S&P and Fitch, if available (e.g. Fitch rated Company BBB+/Stable; Moody's rated Company B-/Negative etc.)

- Each bullet must begin with the company name, "The company", or "It". Make sure each bullet point is a proper sentence, which do not contain any sub-headings, colon or semi-colons


- Sources to be used for this section:
-- The bullet points regarding what the company does, its products/services, operations, customers can be sourced through Web Search, using the company's official website. The Web Search can be complemented by using Primary Activity, Business Review, Introduction or Strategic Report section of the annual report
-- The bullet point regarding company's stress triggers can be sourced from the Business Review or Ongoing Concern or Bank Debt/Borrowings/Creditors section of the annual report
-- The bullet point regarding Credit Ratings can be sourced through Web Search, using press articles from Moody's, S&P and Fitch
-- If any of the above source suggestions does not return results for any part, please scan and check other sections of the reports or do Web Search to see if relevant information can be found


- Notes for this section:
-- If information for any of the bullet point is not available in the report or through Web Search, do not include that specific bullet point as incorrect information is strictly prohibited

SOURCES
- After the bullet points, add a "Sources:" section
- List all sources cited in the bullet points with their bracket numbers (e.g., [#1], [#2], [#5])
- For each source, include: document title, section/page (if available from context), and what information it substantiates, and URL to the website if information has been taken from web search
- If web search was used, include the URLs or source descriptions
- Keep one source per line
"""

# =================================
stakeholders_formatting = """ 
Follow the formatting and instructions for each section of the output.

**2. Key Stakeholders**

Return THREE sections in this exact order:

SECTION 1 — CSV TABLE
- Output a valid CSV with header: Metric,Shareholders
- One data row per metric.
- Use "n.a." / "n.m." exactly when unavailable.
- CSV rules:
  * Separate fields with commas only (no extra spaces around commas).
  * Wrap any field that contains commas, brackets, percent signs, currency symbols, or spaces in double quotes.
  * Escape any internal double quotes by doubling them.
- Do NOT wrap the CSV in code fences.
- Do NOT add any text before or after the CSV in this section.

SECTION 2 — SUMMARY / INTERPRETATION
- After the CSV, add a single blank line, then a heading line: Summary / Interpretation
- Provide 3–6 concise bullets explaining the key movements, relationships, and caveats.
- Base all points strictly on the CSV values; do not invent numbers.

SECTION 3 - SOURCES
- Point out all the sources used by the original input with the correct number index like [#6], and CITE THE COMPLETE SOURCE like which report it was used, etc.


Formatting example (shape only; values are illustrative):

Metric,Shareholders
"Shareholders", "Scott"
"Management","n.a."
"Lenders","Maria"
"Auditors","James"
"Advisors","n.a."

Summary / Interpretation
- Brief point 1…
- Brief point 2…
- Brief point 3…
"""


stakeholders_formatting_2 = """ 
Follow the formatting and instructions for each section of the output.

Return THREE sections in this exact order:

- Add a single blank line, then a heading line: **2. Key Stakeholders**

SECTION 1 — TABLE
- Table must be header: Metric,Shareholders
- One data row per metric.
- Use "n.a." / "n.m." exactly when unavailable.
- Do NOT add any text before or after the Table in this section.
- Do NOT include extra headers in the table
- USE MARKDOWN STYLE FOR THE TABLE


SECTION 2 — SUMMARY / INTERPRETATION
- After the Table, add a single blank line, then a heading line: **Summary / Interpretation**
- Provide 3–6 concise bullets explaining the key movements, relationships, and caveats.
- Base all points strictly on the Table values; do not invent numbers.

SECTION 3 - SOURCES
- Point out all the sources used by the original input with the correct number index like [#6], and CITE THE COMPLETE SOURCE like which report it was used, etc.


Formatting markdown example (shape only; values are illustrative):

| Metric | Shareholders |
| --- | --- |
| Shareholders | Scott |
| Management | n.a. |
| Lenders | Maria |
| Auditors | James |
| Advisors | n.a. |

Summary / Interpretation
- Brief point 1…
- Brief point 2…
- Brief point 3…
"""


stakeholders_web_mix = """
Follow the formatting and instructions for each section of the output.

RETURN TWO SECTIONS:

SECTION ONE - Key Stakeholders
- Add a single blank line, then a heading line: 2. Key Stakeholders
- This section provides key stakeholders of the company in a table format, including the following, using the available annual reports/financial statements of the company, as well as Web Search:
-- Shareholders (Provide the immediate parent company and ultimate parent company of the target company in the case of a private company. In the case of a public company, provide top 5 shareholders of the company with % owned)
-- Management (Include the name of the chairman, Chief Executive Officer and Chief Financial Officer. If these three are not available provide the name of the Directors listed in the annual report)
-- Lenders (Include the name of the lenders of the company for each of the debt facility, if reported)
-- Auditors (Provide the name of the auditor of the company mentioned in the report, e.g. PwC, EY etc.)
-- Advisors (Provide any financial or legal advisors, solicitors or bankers of the company)
-- Charges (Provide the list of Charges (Outstanding ONLY), their issue date and persons entitled using Companies House website)

SECTION TWO - SOURCES
- Sources to be used for this section: 
- After the Table add a blank line, then a heading line: Sources
-- Shareholders will be available under the Parent Company section of the annual report, or throughout text in different sections, for private companies. For public limited companies, the top shareholders will be listed in the Shareholders section of the annual report. However, for public limited companies if it is not available in the report, Use Web Search to obtain to this information, as a backup option
-- Management will be available on the company’s official website, using Web Search. If a website is not available, check Company Information or Strategic Report or Key Management or Board of Directors section of the annual report
-- Lenders might be available in the Notes section of the annual report, particularly in the Bank Debt or Debt or Borrowings or Payables or Creditors section of the report. If not available, use Web Search to search for press articles that has name of lenders for the debt facilities
-- Auditors will be available in the Company Information or Independent Auditors Report section of the annual report
-- Advisors need to be checked using Web Search, particularly for press articles related to debt issuance or M&A, that might provide name of the advisors, in addition to offering memorandum of debt if available. In addition, the annual report might have some advisors listed in Company Information section 
-- Charges need to be checked using Web Search, through Companies House website. The Companies House page of the company has all the Outstanding Charges listed
-- If any of the above source suggestions does not return results for any part, please scan and check other sections of the reports or do Web Search to see if relevant information can be found
- Notes for this section:
-- Put n/a for any part not available in the report or through Web Search, rather than reporting incorrect information

Formatting markdown example (shape only; values are illustrative):

| Metric | Shareholders |
| --- | --- |
| Shareholders | Scott |
| Management | n.a. |
| Lenders | Maria |
| Auditors | James |
| Advisors | n.a. |
"""


# =================================
revenue_split_formatting = """
Follow the formatting and instructions for each section of the output.
RETURN TWO SECTIONS

- Add a single blank line, then a heading line: 3. Revenue Split

1 - TABLE
- This section provides the revenue segmentation of the company’s latest available revenue/turnover in the form of a table, using the latest available annual report/financial statement of the company:
-- This can be revenue by geography, customer geography, products, type of business, business segments or/and any other type of split. If any of this type is not available, include what the company reports, as it is
-- If multiple types of revenue segmentations are available e.g. revenue split by geography and revenue split by business segments, provide both of them, as reported in the report
-- For the revenue split, using the actual values of each segment, calculate percentage shares
-- Report both actual values and the percentage shares for each
-- Make sure the total of the split must always be the same as the total revenue/turnover of the latest year

2 - SOURCES
- Sources to be used for this section: 
- After the Table, Add a single blank line, then a heading line: Sources
-- The revenue split is usually available in the Revenue/Turnover notes section of the report. Usually this is Note 2,3 or 4, but can vary
-- If any of the above source suggestions does not return results for any part, please scan and check other sections of the reports to see if relevant information can be found
- Notes for this section:
-- If the split is not available, please suggest that it is not available, as not all companies will have this information, rather than including incorrect information

Example of a table split:

Revenue by geography (country of destination)
| Segment | Revenue (£m) | Share (%)| 
| --- | --- | --- |
| UK | 9.2 | 12.0| 
| Europe | 15.9 | 20.8| 
| North America | 35.1 | 45.7| 
| Rest of world | 16.7 | 21.7| 
| Total | 76.8 | 100.0| 


The table must ALWAYS follow markdown format.
"""

# =================================

products_overview_formatting = """
Follow the formatting and instructions for each section of the output.


- Add a single blank line, then a heading line: 4a. Products/Services Overview

1 - SUMMARY
- This section details out all the products and service offering of the company, using the latest available annual reports/financial statements of the company as well as Web Search
-- Include each product/service with a high-level brief description, in a sentence format
- Sources to be used for this section: 
-- This information should be sourced through Web Search, using company’s official website. The Web Search can be complemented by using Primary Activity, Business Review, Introduction or Strategic Report section of the annual report
-- If any of the above source suggestions does not return results for any part, please scan and check other sections of the reports or do Web Search to see if relevant information can be found
- Notes for this section:
-- If this information is unavailable, please suggest so, rather than including incorrect information

2 - SOURCES
- After the Summary, Add a single blank line, then a heading line: Sources:
- Include all sources used in the previous section
"""

# =================================

geo_footprint_formatting = """
Follow the formatting and instructions for each section of the output.


- Add a single blank line, then a heading line: 4b. Geographical Footprint

- This section details out all the facilities of the company including its offices, manufacturing facilities, sales offices etc., using the latest available annual reports/financial statements of the company as well as Web Search
-- List down the countries the company operates in a table format, which indication of there is an office, manufacturing facility or sales office in that particular country
- Sources to be used for this section: 
-- This information should be sourced through Web Search, using company’s official website. The Web Search can be complemented by using Primary Activity, Business Review, Introduction or Strategic Report section of the annual report 
-- If any of the above source suggestions does not return results for any part, please scan and check other sections of the reports or do Web Search to see if relevant information can be found
- Notes for this section:
-- If this information is unavailable, please suggest so, rather than including incorrect information

Example for the table (ALWAYS MARKDOWN):

| Country | Office (HQ/other) | Manufacturing facility | Sales/commercial office | Notes (evidence) |
| --- | --- | --- | --- | --- |
| United Kingdom | Yes | Yes | Yes | Melbourn (Cambridge) is the global R&D and production centre for the core SPT Labtech range; Seaport Topco’s registered office is at Building F, Melbourn Science Park, Cambridge Road, Melbourn SG8 6HB. |

- Always use markdown format for the table
"""

# =================================

key_devs_formatting = """
Follow the formatting and instructions for each section of the output.

- Add a single blank line, then a heading line: 5. Key Developments


- This section includes the latest 8-10 available news of the company in reverse chronological order of release date, using Web Search, complemented by annual reports/financial statements:
-- These news must be formatted in bullet points, with each bullet starting with Mmm-yy (e.g. Jun-24: Ferrari acquired XYZ...), and must contain full proper sentences without the use of semi-colons
-- Each bullet point must start with the company name (e.g. Jun-24: Ferrari acquired XYZ) 
-- Include developments from the last three years maximum, not older than that
-- Everything reported cannot be considered as news. For e.g. “In 2023, Company recorded a profit of £xx” is not considered as a news as it is a trading update. However, “In 2023, the company refinanced its loan maturing in Dec-24” is a news.
-- Following news are priority, other news must not be included: (1) Debt issuance or debt refinancing (2) Restructuring, (3) Mergers/Acquisitions/Divestments, (5) Changes in management personnel, (6) Facility openings/closures, (7) Strategic partnerships, (8) Dividends payment/Share repurchase etc.
- Sources to be used for this section: 
-- Key news should be sourced using Web Search, particularly from the news sections on the company’s official website, as well as news articles posted by news outlet (e.g. Yahoo Finance, BBC etc.). Web Search can be complemented by any important news/developments reported in the annual reports/financial statements
- Notes for this section:
-- If key developments are limited, you can just provide a few of them, not 8-10, as long as they are relevant. However, if there is n
"""

# =================================

finance_formatting = """ 
Follow the formatting and instructions for each section of the output.

**6. Financial Highlights**
Return TWO sections in this exact order:

SECTION 1 — CSV TABLE
- Output a valid CSV with header: Metric,FY24,FY23,FY22
- One data row per metric.
- Use "n.a." / "n.m." exactly when unavailable.
- CSV rules:
  * Separate fields with commas only (no extra spaces around commas).
  * Wrap any field that contains commas, brackets, percent signs, currency symbols, or spaces in double quotes.
  * Escape any internal double quotes by doubling them.
- Do NOT wrap the CSV in code fences.
- Do NOT add any text before or after the CSV in this section.

SECTION 2 — SUMMARY / INTERPRETATION
- After the CSV, add a single blank line, then a heading line: Summary / Interpretation
- Provide 3–6 concise bullets explaining the key movements, relationships, and caveats.
- Base all points strictly on the CSV values; do not invent numbers.

SECTION 3 - SOURCES
- Point out all the sources used by the original input with the correct number index like [#6], and CITE THE COMPLETE SOURCE like which report it was used, etc.


Formatting example (shape only; values are illustrative):

Metric,FY24,FY23,FY22
"Revenue (Turnover)","£576.8m [#2]","£81.4m [#6]","£32.8m [#5]"
"Revenue growth % (yoy)","+608.6% [#2][#6]","+148.0% [#5]","n.a."
"Gross profit","n.a.","£48.4m [#3][#6]","£14.3m [#3]"

Summary / Interpretation
- Brief point 1…
- Brief point 2…
- Brief point 3…
"""


finance_formatting_2= """ 
Follow the formatting and instructions for each section of the output.

Return THREE sections in this exact order:

- Add a single blank line, then a heading line: 6. Financial Highlights

SECTION 1 — TABLE
- Output a valid Table with header: Metric,FY24,FY23,FY22
- One data row per metric.
- Use "n.a." / "n.m." exactly when unavailable.
- Do NOT add any text before or after the Table in this section.

SECTION 2 — SUMMARY / INTERPRETATION
- After the Table, add a single blank line, then a heading line: Summary / Interpretatio
- Include bullet point commentary from the annual reports (usually available in Business Review or Financial Review sections), a tight, detailed eight‑bullet narrative in the following order, complementing the table:
    1. Revenue change and key drivers.
    2. Gross profit movement and explanation.
    3. EBITDA direction and reasons.
    4. Net working capital change and major line items driving the movement.
    5. Capex development.
    6. CFADS changes
    7. Financing cash flow dynamics including dividends, debt repayments, and issuances.
    8. Total debt and leverage trend.
- Commentary bullets must be detailed, in proper full sentences. 
- AVOID sub-headings and semi-colons
- Write each bullet so a reader unfamiliar with the company can clearly understand the drivers and implications
- If any information regarding any bullet point is unavailable, please do not include it, rather than including wrong information
- Base all points strictly on the Table values; do not invent numbers.

SECTION 3 - SOURCES
- After the SUMMARY / INTERPRETATION, add a single blank line, then a heading line: Sources

- Point out all the sources used by the original input with the correct number index like [#6], and CITE THE COMPLETE SOURCE like which report it was used, etc.


Formatting example (shape only; values are illustrative):

| Metric | FY24 | FY23 | FY22 |
| --- | --- | --- | --- |
| Revenue (Turnover) | £576.8m [#2] | £81.4m [#6] | £32.8m [#5] |
| Revenue growth % (yoy) | +608.6% [#2][#6] | +148.0% [#5] | n.a. |
| Gross profit | n.a. | £48.4m [#3][#6] | £14.3m [#3] |

Summary / Interpretation
- Brief point 1…
- Brief point 2…
- Brief point 3…

Sources
- Source 1...

"""

# =================================

capital_structure_formatting = """
Follow the formatting and instructions for each section of the output.

**7. Capital Structure* 

Return THREE sections in this exact order:

SECTION 1 — CSV TABLE
- Output a valid CSV with header: Metric,FY24
- One data row per metric.
- Use the following canonical metric names (match exactly when present in the source):
  * Facility Name
  * Interest Rate
  * Maturity
  * Adjusted EBITDA
  * Cash (Closing Cash)
  * Net Debt
  * Liquidity
  * Leverage (Net Debt/EBITDA)
  * Facility B1 outstanding (GBP)
  * Facility B2 outstanding (GBP)
  * RCF drawn
  * RCF facility size
  * Delayed Drawdown Facility size
  * Bank loans due after >5 years
  * Bank loans due within 1 year
  * Bank loans + RCF outstanding (excl. leases)
- Use "n.a." / "n.m." exactly when unavailable or not meaningful.
- Always append source indices to numeric values like: £171.9m [#10] or 9.6x [#10].
- CSV rules:
  * Separate fields with commas only (no spaces around commas).
  * Wrap any field that contains spaces, commas, brackets, percent signs, currency symbols, or minus signs in double quotes.
  * Escape internal double quotes by doubling them.
- Do NOT wrap the CSV in code fences.
- Do NOT add any text before or after the CSV in this section.
- If a total is shown explicitly in the source (e.g., “Bank loans + RCF outstanding (excl. leases)”), include it. If it is not shown and all needed components are present (e.g., Facility B1 + Facility B2 + RCF drawn), you may compute it and include the computed total; otherwise use "n.a.".
- If EBITDA is ≤ 0, set Leverage (Net Debt/EBITDA) to "n.m.".

SECTION 2 — SUMMARY / INTERPRETATION
- After the CSV, add a single blank line, then a heading line: **Summary / Interpretation**
- Provide 3–6 concise bullets highlighting leverage, maturity profile, facility mix, liquidity lines, and visible gaps.
- Base all points strictly on the CSV values; do not invent numbers.

SECTION 3 — SOURCES
- After the SUMMARY / INTERPRETATION, add a single blank line, then a heading line: **Sources**
- List all sources cited in the CSV with their bracket numbers (e.g., [#10]).
- For each, include a brief description: document title, section/page (if available), and what it substantiates.
- Keep one source per line.

Formatting example (shape only; values are illustrative):

Metric,FY24
"Name of Facility","n.a"
"Interest Rate","30"
"Maturity","30-nov"
"Adjusted EBITDA","£17.9m [#10]"
"Cash (Closing Cash),"£30.0m [#4]"
"Net External Debt","£171.9m [#10]"
"Leverage (Net Debt/EBITDA)","9.6x [#10]"
"Facility B1 outstanding (GBP)","£36.0m [#1]"
"Facility B2 outstanding (GBP)","£135.0m [#1]"
"RCF drawn","£16.0m [#8]"
"RCF facility size","£30.0m [#8]"
"Delayed Drawdown Facility size","£75.0m [#8]"
"Bank loans due after >5 years","£168.7m [#1]"
"Bank loans due within 1 year","£14.7m [#1]"
"Bank loans + RCF outstanding (excl. leases)","£187.0m [#1][#4]"

Summary / Interpretation
- Brief point 1…
- Brief point 2…
- Brief point 3…

Sources
- [#1] Title / section / page — what it supports.
- [#4] Title / section / page — what it supports.
- [#10] Title / section / page — what it supports.
"""

capital_structure_formatting_2 = """
Return THREE sections in this exact order:

- Add a single blank line, then a heading line: 7. Capital Structure

SECTION 1 — TABLE
- header (only 2 columns): Metric, FY-latest year available example: FY-24
- CRITICAL: Display ONLY the latest fiscal year (e.g., FY24). Do NOT include FY23, FY22, or any prior years even if they appear in the source data.
- One data row per metric.
- Use the following canonical metric names (match exactly when present in the source):
  * Facility Name
  * Interest Rate
  * Maturity
  * Adjusted EBITDA
  * Cash (Closing Cash)
  * Net Debt
  * Liquidity
  * Leverage (Net Debt/EBITDA)
  * Facility B1 outstanding (GBP)
  * Facility B2 outstanding (GBP)
  * RCF drawn
  * RCF facility size
  * Delayed Drawdown Facility size
  * Bank loans due after >5 years
  * Bank loans due within 1 year
  * Bank loans + RCF outstanding (excl. leases)
- Use "n.a." / "n.m." exactly when unavailable or not meaningful.
- Always append source indices to numeric values like: £171.9m [#10] or 9.6x [#10].
- If a total is shown explicitly in the source (e.g., “Bank loans + RCF outstanding (excl. leases)”), include it. If it is not shown and all needed components are present (e.g., Facility B1 + Facility B2 + RCF drawn), you may compute it and include the computed total; otherwise use "n.a.".
- If EBITDA is ≤ 0, set Leverage (Net Debt/EBITDA) to "n.m.".

SECTION 2 — SUMMARY / INTERPRETATION
- After the Table, add a single blank line, then a heading line: Summary / Interpretation
- Include bullet point commentary using the context given, tight seven‑bullets complementing the table, covering:
    1. Net debt and leverage trend, with underlying factors.
    2. Recent refinancing actions
    3. Debt covenants including actual covenant terms and any recent covenant tests.
    4. Debt security including collateral and security package.
    5. Liquidity position including cash, committed undrawn facilities, overdraft, and accordion if available.
    6. Upcoming maturities.
    7. Any debt related issues (chances of default/bankruptcy) highlighted
- Commentary bullets must be detailed, in proper full sentences
- AVOID sub-headings and semi-colon
- Each commentary bullet must be written clearly enough for a reader unfamiliar with the company to understand the meaning, impact, and implications
- If any information regarding any bullet point is unavailable, please do not include it, rather than including wrong information
- Base all points strictly on the Table values; do not invent numbers.

SECTION 3 — SOURCES
- After the SUMMARY / INTERPRETATION, add a single blank line, then a heading line: Sources
- List all sources cited in the Table with their bracket numbers (e.g., [#10]).
- For each, include a brief description: document title, section/page (if available), and what it substantiates.
- Keep one source per line.

Formatting example (shape only; values are illustrative - NOTE: Only ONE year column):

| Metric | FY24 |
| --- | --- |
| Name of Facility | James |
| Interest Rate | 34 |
| Maturity | 30-nov |
| Adjusted EBITDA | n.a. |
| Cash (Closing Cash) | £30.0m [#4] |
| Net External Debt | n.a. |
| Leverage (Net Debt/EBITDA) | n.a. |
| Facility B1 outstanding (GBP) | £36.0m [#1] |
| Facility B2 outstanding (GBP) | £135.0m [#1] |
| RCF drawn | £30.0m [#4] |
| RCF facility size | £30.0m [#4] |
| Delayed Drawdown Facility size | n.a. |
| Bank loans due after >5 years | £168.7m [#1] |
| Bank loans due within 1 year | £14.7m [#1] |
| Bank loans + RCF outstanding (excl. leases) | £187.0m [#1][#4] |

Summary / Interpretation
- Brief point 1…
- Brief point 2…
- Brief point 3…

Sources
- [#1] Title / section / page — what it supports.
- [#4] Title / section / page — what it supports.
- [#10] Title / section / page — what it supports.
""" 