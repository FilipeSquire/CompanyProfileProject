import azure.functions as func
import logging

try:
    from engines.profile_pdf import profile_creator, markdown_table_to_docx
except Exception as e:
    logging.error(f'Failed to import engines.profile_df {e}')
    print(f'Failed to import engines.profile_df {e}')
    
try:
    from azure.blob_functions import get_company_name, upload_blob
except Exception as e:
    logging.error(f'Failed to import engines.profile_df {e}')
    print(f'Failed to import azure.blob_functions {e}')
#

app = func.FunctionApp(http_auth_level=func.AuthLevel.ADMIN)


@app.route(route="pdfprofile", methods=["POST"], auth_level=func.AuthLevel.ADMIN)
def pdfprofile(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        body = req.get_json()
    except ValueError:
        body = {}

    company_number = (
        (body.get("company_number") if isinstance(body, dict) else None)
        or (body.get("id") if isinstance(body, dict) else None)
        or (body.get("IDS") if isinstance(body, dict) else None)
        or req.params.get("company_number")
        or req.params.get("id")
        or req.params.get("IDS")
    )

    # company_name = "SEAPORT_TOPCO_LIMITED"

    if company_number:
        try:
            company_name = get_company_name(company_number)
        except Exception as e:
            print(f"Error getting company name: {e}")

        try:
            agent = profile_creator(company_name)
        except Exception as e:
            print(f"Error creating profile agent: {e}")

        try:
            agent._generate_section()
        except Exception as e:
            print(f"Error generating sections: {e}")

        try:
            agent._check_sections()
        except Exception as e:
            print(f"Error checking sections: {e}")

        try:
            all = agent._unite_sections()
        except Exception as e:
            print(f"Error uniting sections: {e}")

        try:
            # Generate document and get BytesIO buffer
            doc_buffer = markdown_table_to_docx(
                all,
                logo_path="logo_teneo.png"
            )
            print(f"✓ Generated {agent.company_name}.docx")
        except Exception as e:
            print(f"Error generating: {e}")
        
        try:
            # Upload to blob storage with metadata
            upload_blob(
                CONTAINER="companieshousesinglefile",
                BLOB_NAME=f"{agent.company_name}_PROFILE.docx",
                file=doc_buffer,
                company_name=agent.company_name,
                company_number=company_number,
                doc_type="profile"
            )
            print(f"✓ Uploaded {agent.company_name}.docx to blob storage")
        except Exception as e:
            print(f"Error uploading document: {e}")

        return func.HttpResponse(f"Hello, {company_name}. This HTTP triggered function executed successfully.")
        
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )