from io import BytesIO
import pandas as pd
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobClient, ContentSettings
from dotenv import load_dotenv, find_dotenv
import os
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime

load_dotenv(find_dotenv(), override=True)


# === CONFIG ===
ACCOUNT_URL   = os.getenv("BLOB_ACCOUNT_URL")
AZURE_STORAGE_CONNECTION_STRING=os.getenv("BLOB_AZURE_STORAGE_CONNECTION_STRING")
# BLOB_NAME     = "companieslist/CompaniesHouseList.xlsx"   # e.g., "reports/myfile.xlsx"
UK_API_KEY = os.getenv("UK_API_KEY")


def get_file_blob(CONTAINER, BLOB_NAME):
    # === AUTH + CLIENT ===
    # cred = DefaultAzureCredential()  # Works locally (Azure CLI login), in VM/MSI, GitHub OIDC, etc.
    # blob = BlobClient(account_url=ACCOUNT_URL, container_name=CONTAINER,
    #                 blob_name=BLOB_NAME, credential=cred)

    blob = BlobClient.from_connection_string(conn_str=AZURE_STORAGE_CONNECTION_STRING,
                                         container_name=CONTAINER,
                                         blob_name=BLOB_NAME)


    data = blob.download_blob().readall()

    return data

INVALID_CHARS = '<>:"/\\|?*'
def sanitize(s: str) -> str:
    s = s.replace(" ", "_")
    for ch in INVALID_CHARS:
        s = s.replace(ch, "_")
    return s



def companyHouseListAdd(
    CONTAINER='companieslist',
    BLOB_NAME='CompaniesHouseList.xlsx',
    CompanyNumber=None,
    sheet_name='IDs'   # change if your sheet is named differently
):
    if CompanyNumber is None:
        raise ValueError("CompanyNumber is required")

    # 1) Download the Excel
    excel_bytes = get_file_blob(CONTAINER, BLOB_NAME)

    # Try reading the sheet; if file/sheet doesn't exist, start a blank DF
    try:
        df = pd.read_excel(BytesIO(excel_bytes), sheet_name=sheet_name, dtype={'IDS': str, 'NAMES': str})
    except Exception:
        df = pd.DataFrame(columns=['IDS', 'NAMES'])

    # Ensure required columns exist
    for col in ('IDS', 'NAMES'):
        if col not in df.columns:
            df[col] = ""

    # 2) Get the company display name (human-friendly; don't sanitize for Excel)
    url = f"https://api.company-information.service.gov.uk/company/{CompanyNumber}"
    r = requests.get(url, auth=HTTPBasicAuth(UK_API_KEY, ""))
    r.raise_for_status()
    name = r.json().get("company_name", "")
    name = sanitize(name)

    # 3) Upsert: if ID exists, update its name; else append new row
    CompanyNumber = str(CompanyNumber)
    mask = (df['IDS'].astype(str) == CompanyNumber)
    if mask.any():
        df.loc[mask, 'NAMES'] = name
    else:
        df = pd.concat(
            [df, pd.DataFrame({'IDS': [CompanyNumber], 'NAMES': [name]})],
            ignore_index=True
        )

    # Optional: dedupe on IDs keeping the last occurrence
    df = df.drop_duplicates(subset=['IDS'], keep='last')

    # 4) Write back to Excel in-memory
    buf = BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as xw:
        df.to_excel(xw, index=False, sheet_name=sheet_name)
    buf.seek(0)

    # 5) Overwrite the blob
    blob = BlobClient.from_connection_string(
        conn_str=AZURE_STORAGE_CONNECTION_STRING,
        container_name=CONTAINER,
        blob_name=BLOB_NAME
    )
    
    blob.upload_blob(
        buf.getvalue(),
        overwrite=True,
        content_settings=ContentSettings(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ),
    )

def upload_blob(CONTAINER, BLOB_NAME, file, **kwargs):
    """
    Upload a file buffer to Azure Blob Storage.
    """
    blob = BlobClient.from_connection_string(
        conn_str=AZURE_STORAGE_CONNECTION_STRING,
        container_name=CONTAINER,
        blob_name=BLOB_NAME
    )

    # Handle both BytesIO and bytes
    data = file.getvalue() if hasattr(file, 'getvalue') else file

    # Build metadata from kwargs
    try:
        meta = {
            "company_name": kwargs.get("company_name", ""),
            "company_number": kwargs.get("company_number", ""),
            "annual_report_date": datetime.today().strftime("%Y-%m-%d"),
            "doc_type": kwargs.get("doc_type", "profile")
        }
    except:
        pass

    blob.upload_blob(
        data,
        overwrite=True,
        content_settings=ContentSettings(
            content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ),
        metadata=meta if meta else None
    )

def get_companies(CONTAINER = 'companieslist', BLOB_NAME = 'CompaniesHouseList.xlsx'):


    excel_bytes = get_file_blob(CONTAINER = 'companieslist', BLOB_NAME = 'CompaniesHouseList.xlsx')
    df = pd.read_excel(BytesIO(excel_bytes), sheet_name="IDs")
    names = df['NAMES'].copy()
    clean = (names.astype(str)
                .str.replace(r'_+', ' ', regex=True)  # "_" -> " "
                .str.replace(r'\s+', ' ', regex=True) # collapse double spaces
                .str.strip())

    name_map = dict(zip(names.tolist(), clean.tolist()))
    clean_in_order = [name_map[orig] for orig in names] 

    return name_map, clean_in_order

def get_company_name(company_number, CONTAINER = 'companieslist', BLOB_NAME = 'CompaniesHouseList.xlsx'):
    """
    This function is returns the company_name registered in the excel file CompaniesHouseList based on company_number
    and returns the company_name
    """

    excel_bytes = get_file_blob(CONTAINER = 'companieslist', BLOB_NAME = 'CompaniesHouseList.xlsx')
    df = pd.read_excel(BytesIO(excel_bytes), sheet_name="IDs")
    company_name = df[df.IDS == company_number].NAMES.values[0]
    return company_name





