
import os
import logging
import json
import argparse


class ingestion_handler():


    def __init__():
        pass


    def company_house_get_http(company_number):
        """
        Accepts JSON like {"company_number":"01234567"} (or {"id":"01234567"})
        Optional overrides: container_name, blob_prefix, sleep_between
        """

        try:
            from apis.companies_house.companies_house import download_and_upload_company_accounts
        except ValueError:
            return logging.info('Failed at companies_house/companies_house import')


        # Accept either "company_number" or "id" from ADF
        if not company_number:
            return logging.info('{"error":"Missing company_number (or id)"}', status_code=400, mimetype="application/json")

        api_key = os.getenv("COMPANIES_HOUSE_API_KEY")
        if not api_key:
            return logging.HttpResponse('{"error":"COMPANIES_HOUSE_API_KEY not set"}', status_code=500, mimetype="application/json")

        try:
            found, uploaded = download_and_upload_company_accounts(
                api_key=api_key,
                company_number=company_number,
                # container_name=container_name,
                # prefix=blob_prefix or None,
                # sleep_between=sleep_between,
            )
            result = {"company_number": company_number, "found": found, "uploaded": uploaded, "status": "ok"}
            return logging.HttpResponse(json.dumps(result), mimetype="application/json", status_code=200)
        except Exception as e:
            logging.exception("Run failed for %s: %s", company_number, e)
            return logging.HttpResponse(json.dumps({"company_number": company_number, "error": str(e)}), mimetype="application/json", status_code=500)


# if __name__ == "__main__":
#     logging.basicConfig(
#         level=logging.INFO,
#         format='%(asctime)s - %(levelname)s - %(message)s'
#     )

#     parser = argparse.ArgumentParser(
#         description='Ingestion router for company data from various sources'
#     )
#     parser.add_argument(
#         'company_number',
#         type=str,
#         help='Company number to fetch data for'
#     )
#     parser.add_argument(
#         '--source',
#         type=str,
#         default='companies_house',
#         choices=['companies_house'],
#         help='Data source to use (default: companies_house)'
#     )

#     args = parser.parse_args()

#     logging.info(f"Starting ingestion for company: {args.company_number} from source: {args.source}")

#     if args.source == 'companies_house':
#         result = ingestion_handler.company_house_get_http(args.company_number)
#         if result:
#             logging.info("Ingestion completed successfully")
#         else:
#             logging.error("Ingestion failed")
#     else:
#         logging.error(f"Unknown source: {args.source}")