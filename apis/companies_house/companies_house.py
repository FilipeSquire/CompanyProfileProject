import logging
import os
import time
import base64
import json
from typing import Optional
import requests
from requests.auth import HTTPBasicAuth
# from azure.storage.blob import BlobServiceClient
# import azure.functions as func
from datetime import datetime
# from azure.storage.blob import ContentSettings

# from charges_extraction import charges_extraction
# from charges_check import charges_check
# from reports_check import reports_check
# from new_report_email import new_report_email
# from new_company_notification import company_notify

# app = func.FunctionApp()
# app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)
# app.register_functions(charges_extraction)
# app.register_functions(charges_check)  
# app.register_functions(reports_check)  
# app.register_functions(new_report_email)  
# app.register_functions(company_notify) 

# def get_blob_service_client():
#     conn = os.getenv("AZURE_STORAGE_CONNECTION_STRING") or os.getenv("AzureWebJobsStorage")
#     if not conn:
#         raise RuntimeError("No storage connection string found in AZURE_STORAGE_CONNECTION_STRING or AzureWebJobsStorage.")
#     return BlobServiceClient.from_connection_string(conn)


# def ensure_container(blob_service: BlobServiceClient, container_name: str):
#     try:
#         blob_service.create_container(container_name)
#     except Exception:
#         # likely already exists; ignore
#         pass

# ===== Helper: safe blob name =====
INVALID_CHARS = '<>:"/\\|?*'
def sanitize(s: str) -> str:
    s = s.replace(" ", "_")
    for ch in INVALID_CHARS:
        s = s.replace(ch, "_")
    return s

# ===== Main worker =====
def download_and_upload_company_accounts(
    api_key: str,
    company_number: str,
    # container_name: str,
    prefix: Optional[str] = None,
    sleep_between: float = 1.0,
):
    """
    Downloads Companies House 'accounts' filings for a company and uploads PDFs to Blob Storage.
    """
    # blob_service = get_blob_service_client()
    # ensure_container(blob_service, container_name)
    # container_client = blob_service.get_container_client(container_name)

    filing_history_url = f"https://api.company-information.service.gov.uk/company/{company_number}/filing-history"
    params = {"category": "accounts"}

    logging.info("Requesting filing history for %s ...", company_number)
    resp = requests.get(filing_history_url, auth=HTTPBasicAuth(api_key, ""), params=params, timeout=30)
    if resp.status_code != 200:
        raise RuntimeError(f"Filing history request failed: {resp.status_code} {resp.text}")

    try:
        data = resp.json()
    except requests.exceptions.JSONDecodeError:
        raise RuntimeError("Failed to parse filing history JSON")

    items = data.get("items", [])
    logging.info("Found %d 'accounts' filings.", len(items))

    uploaded = 0

    # Prepare auth headers for metadata + pdf
    key_pass = f"{api_key}:"
    encoded_auth = base64.b64encode(key_pass.encode("utf-8")).decode("utf-8")
    headers = {"Authorization": f"Basic {encoded_auth}"}
    pdf_headers = {"Authorization": f"Basic {encoded_auth}", "Accept": "application/pdf"}

    for index, item in enumerate(items):
        file_date = int(item.get('date')[:4]) > (datetime.today().year - 3)

        if file_date:
        
            description = item.get("description", "unknown_description")
            links = item.get("links", {})
            document_metadata_url = links.get("document_metadata")

            if not document_metadata_url:
                logging.info("Skipping item %d: no document_metadata link.", index)
                continue

            if not document_metadata_url.startswith("http"):
                document_metadata_url = "https://api.company-information.service.gov.uk" + document_metadata_url

            # Fetch metadata
            meta = requests.get(document_metadata_url, headers=headers, timeout=30)
            if meta.status_code != 200:
                logging.warning("Metadata request failed (%s): %s", meta.status_code, document_metadata_url)
                continue

            try:
                metadata = meta.json()
            except requests.exceptions.JSONDecodeError:
                logging.warning("Failed to parse metadata JSON for item %d", index)
                continue

            document_url = metadata.get("links", {}).get("document")
            if not document_url:
                logging.info("Skipping item %d: no document link in metadata.", index)
                continue

            if not document_url.startswith("http"):
                document_url = "https://api.company-information.service.gov.uk" + document_url

            # Get final (possibly redirected) URL
            redirect_response = requests.get(document_url, headers=pdf_headers, allow_redirects=False, timeout=30)
            if redirect_response.status_code in [301, 302, 303, 307, 308]:
                final_pdf_url = redirect_response.headers.get("Location")
                # fetch the actual PDF
                pdf_response = requests.get(final_pdf_url, timeout=60)
            elif redirect_response.status_code == 200:
                # some endpoints might directly return the PDF
                final_pdf_url = document_url
                pdf_response = redirect_response
            else:
                logging.warning("Document redirect failed (%s) for %s", redirect_response.status_code, document_url)
                continue

            if not pdf_response or pdf_response.status_code != 200:
                logging.warning("Failed to download PDF for item %d (status %s).", index, getattr(pdf_response, "status_code", "?"))
                continue

            # Build blob name
            date = item.get("date", "unknown_date")

            url = f"https://api.company-information.service.gov.uk/company/{company_number}"
            r = requests.get(url, auth=HTTPBasicAuth(api_key, ""))
            r.raise_for_status()
            name = r.json()["company_name"]
            name = sanitize(name)

            doc_type = sanitize(item.get("type", "unknown_type"))
            safe_desc = sanitize(description)
            blob_name = f"{name}_{doc_type}_annualReport_{date}_{index}.pdf"

            final_blob_path = f"{company_number.strip()}/{blob_name}"
        if prefix:
            blob_name = f"{prefix.strip('/')} /{blob_name}".replace(" ", "")  # keep blob paths neat

        # Upload to blob (overwrite)
        try:
            # blob_client = container_client.get_blob_client(final_blob_path)

            meta = {
                "company_number": company_number,
                "company_name": name,
                "annual_report_date": date,
                "doc_type": doc_type,
                "index_order": str(index),
                
            }


            # Create data_dump directory structure
            data_dump_dir = os.path.join(os.getcwd(), "data_dump", company_number.strip())
            os.makedirs(data_dump_dir, exist_ok=True)

            # Save PDF file
            pdf_path = os.path.join(data_dump_dir, blob_name)
            with open(pdf_path, "wb") as f:
                f.write(pdf_response.content)

            # Save metadata as JSON
            metadata_filename = blob_name.replace(".pdf", "_metadata.json")
            metadata_path = os.path.join(data_dump_dir, metadata_filename)
            with open(metadata_path, "w") as f:
                json.dump(meta, f, indent=2)

            # blob_client.upload_blob(
            #     pdf_response.content, 
            #     overwrite=True,
            #     metadata=meta,
            #     content_settings=ContentSettings(content_type="application/pdf")
            # )

            uploaded += 1
            logging.info("✓ Uploaded: %s", final_blob_path)
        except Exception as e:
            logging.exception("Failed to upload %s: %s", final_blob_path, e)

        # Throttle politely
        time.sleep(sleep_between)

    logging.info("Completed upload of %d items to container '%s'.", len(items), container_name)
    return len(items), uploaded


# # ================ HTTP REQUEST
# @app.function_name(name="companyhousetrigger")
# @app.route(methods=["POST"], auth_level=func.AuthLevel.FUNCTION)
# def company_house_get_http(req: func.HttpRequest) -> func.HttpResponse:
#     """
#     Accepts JSON like {"company_number":"01234567"} (or {"id":"01234567"})
#     Optional overrides: container_name, blob_prefix, sleep_between
#     """
#     try:
#         body = req.get_json()
#     except ValueError:
#         body = {}

#     # Accept either "company_number" or "id" from ADF
#     company_number = (
#         (body.get("company_number") if isinstance(body, dict) else None)
#         or (body.get("id") if isinstance(body, dict) else None)
#         or (body.get("IDS") if isinstance(body, dict) else None)
#         or req.params.get("company_number")
#         or req.params.get("id")
#         or req.params.get("IDS")
#     )
#     if not company_number:
#         return func.HttpResponse('{"error":"Missing company_number (or id)"}', status_code=400, mimetype="application/json")

#     api_key = os.getenv("COMPANIES_HOUSE_API_KEY")
#     if not api_key:
#         return func.HttpResponse('{"error":"COMPANIES_HOUSE_API_KEY not set"}', status_code=500, mimetype="application/json")

#     container_name = (body.get("container_name") if isinstance(body, dict) else None) or os.getenv("BLOB_CONTAINER_NAME", "companies-house-pdfs")
#     blob_prefix   = (body.get("blob_prefix") if isinstance(body, dict) else None) or os.getenv("BLOB_PREFIX", "")
#     try:
#         sleep_between = float((body.get("sleep_between") if isinstance(body, dict) else None) or os.getenv("DOWNLOAD_SLEEP_SECONDS", "1"))
#     except Exception:
#         sleep_between = 1.0

#     try:
#         found, uploaded = download_and_upload_company_accounts(
#             api_key=api_key,
#             company_number=company_number,
#             container_name=container_name,
#             prefix=blob_prefix or None,
#             sleep_between=sleep_between,
#         )
#         result = {"company_number": company_number, "found": found, "uploaded": uploaded, "status": "ok"}
#         return func.HttpResponse(json.dumps(result), mimetype="application/json", status_code=200)
#     except Exception as e:
#         logging.exception("Run failed for %s: %s", company_number, e)
#         return func.HttpResponse(json.dumps({"company_number": company_number, "error": str(e)}), mimetype="application/json", status_code=500)