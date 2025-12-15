

TOOLS = [{
    "type": "function",
    "function": {
        "name": "create_company_profile",
        "description": "Call when the user says something similar to: 'Create a company profile (CompanyName)'. Extract the name inside parentheses.",
        "parameters": {
            "type": "object",
            "properties": {"companyName": {"type": "string"}},
            "required": ["companyName"],
            "additionalProperties": False,
        },
    },
    "function": {
    "name": "add_company",
    "description": "Call when the user says something similar to: 'Add this company (CompanyNumber)'. Extract the number sequence inside parentheses.",
    "parameters": {
        "type": "object",
        "properties": {"companyNumber": {"type": "string"}},
        "required": ["companyNumber"],
        "additionalProperties": False,
        },
    },
    "function": {
    "name": "web_search",
    "description": "Call when the user mentions web_search in the phrase. Return True if it is mentioned otherwise False. ",
    "parameters": {
        "type": "object",
        "properties": {"webSearch": {"type": "string"}},
        "required": ["webSearch"],
        "additionalProperties": False,
        },
    },
    "function": {
    "name": "web_search_duo",
    "description": "Call when the source used in user prompt mentions web_search AND annual report. Return True if it is mentioned otherwise False. ",
    "parameters": {
        "type": "object",
        "properties": {"webSearchDuo": {"type": "string"}},
        "required": ["webSearchDuo"],
        "additionalProperties": False,
        },
    },
}]

TOOLS2 = [
     {
        "type": "function",
        "name": "create_company_profile",
        "description": "Call when the user says: 'Create a company profile (CompanyName)'. Extract the name inside parentheses.",
        "parameters": {
            "type": "object",
            "properties": {"companyName": {"type": "string"}},
            "required": ["companyName"],
            "additionalProperties": False
        }
    },
    {
        "type": "function",
        "name": "add_company",
        "description": "Call when the user says: 'Add this company (CompanyNumber)'. Extract the number inside parentheses.",
        "parameters": {
            "type": "object",
            "properties": {"companyNumber": {"type": "string"}},
            "required": ["companyNumber"],
            "additionalProperties": False
        }
    },
    {
        "type": "function",
        "name": "web_search_duo",
        "description": "Call when SOURCE mentions both 'annual report' AND 'web_search'.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": { "type": "string", "description": "Optional query or note" }
            },
            "required": [],
            "additionalProperties": False
        }
    },
    {
        "type": "function",
        "name": "web_search",
        "description": "Call when SOURCE mentions 'web_search'.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": { "type": "string", "description": "Optional query or note" }
            },
            "required": [],
            "additionalProperties": False
        }
    }
]

TOOLS3 = [{'type': 'function',
  'function': {'name': 'create_company_profile',
   'description': "Call when the user says something similar to: 'Create a company profile (CompanyName)'. Extract the name inside parentheses.",
   'parameters': {'type': 'object',
    'properties': {'companyName': {'type': 'string'}},
    'required': ['companyName'],
    'additionalProperties': False}}},
 {'type': 'function',
  'function': {'name': 'add_company',
   'description': "Call when the user says something similar to: 'Add this company (CompanyNumber)'. Extract the number sequence inside parentheses.",
   'parameters': {'type': 'object',
    'properties': {'companyNumber': {'type': 'string'}},
    'required': ['companyNumber'],
    'additionalProperties': False}}},
 {'type': 'function',
  'function': {'name': 'web_search',
   'description': 'Call when the user mentions web_search in the phrase. Return True if it is mentioned otherwise False. ',
   'parameters': {'type': 'object',
    'properties': {'webSearch': {'type': 'string'}},
    'required': ['webSearch'],
    'additionalProperties': False}}},
 {'type': 'function',
  'function': {'name': 'web_search_duo',
   'description': 'Call when the source used in user prompt mentions web_search AND annual report. Return True if it is mentioned otherwise False. ',
   'parameters': {'type': 'object',
    'properties': {'webSearchDuo': {'type': 'string'}},
    'required': ['webSearchDuo'],
    'additionalProperties': False}}}]
