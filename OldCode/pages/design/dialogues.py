greeting_1 = f"""
Hello! Welcome to Oraculum! This system is being prepared to completely assist you in your corporate journey. \n

I am currently capable of downloading new companies from CompaniesHouse, create Company Profile and navigate internet! \n

Please, if you don't want to insert a new company, select one from the following list to talk about: \n

In order to select a new company you just have to type in: 'Select company [company_name]'  \n
"""

greeting_2 = """
Welcome to Web Search Bot! \n In this mode you are able to talk freely with web and youre not restricted by our ingested pdfs.
"""

greeting_3 = """
Welcome to the Web Search and Companies House! \n
This bot was designed to allow you to have a conversation that mixes the usage of two different data sources: PDF and Web. \n

The first step is to select the company that you want to talk about. \n

Every question in this mode must be followed by the source required for that question \n
Example: \n
'I want to know the key developments of Radley Company. Use the annual reports' \n
'I want to know the key developments of Radley Company, use web search'\n
'I want to know the key developments of Radley Company, use web search and annual reports'\n

Through this method you can easily combine data sources for your question or just pick a single one. \n

OBS: This method is still under development and improvements will be made.
"""
profile_tutorial_1 = """
This function makes it possible to create a Company Profile of a company of your choosing!\n

In order to use this function you can type in 'Create company profile of [COMPANY_NAME]' \n

OBs: Currently only some sections such as Financial Highlights and Corporate Structure are available right now\n

"""

add_company_tutorial_1 = """
This function allows you to insert a new company from CompaniesHouse in the database where it will be properly OCRed.\n

In order to use this function you need the company number that you want. \n

To use this function type in: 'Add company [COMPANY_NUMBER]' \n

OBs: Currently it only supports private companies and downloads last 3 years of annual report files.\n
"""

companies_available = """
In order to select a company you must type: \n'Use company [company's name]'\n
This is the following list of availables companies for you to chat: \n

"""

section_tutorial_1 = """
Hey! This action allows you to build a certain company profile section. \n
These sections are made up using either a PDF (company house) or web search, but it only focus in a single company per time \n

The sections are available the in left sidebar menu. Open it and the Profile Section will be available at the bottom \n

REQUIREMENTS: Select a company first\n
"""
error_1 = """
This action requires the previous selection of a company. \n

Try again \n

"""

