import os, time
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexerClient
from dotenv import load_dotenv, find_dotenv
# Or: from azure.identity import DefaultAzureCredential  # if using Entra ID
load_dotenv(find_dotenv(), override=True)

SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")        # e.g. https://<svc>.search.windows.net
INDEXER_NAME    = os.getenv("AZURE_SEARCH_INDEXER")
ADMIN_KEY       = os.getenv("AZURE_SEARCH_API_KEY")        # or use DefaultAzureCredential()

def run_indexer():

    try:
        client = SearchIndexerClient(SEARCH_ENDPOINT, AzureKeyCredential(ADMIN_KEY))

        # 1) Try to run the indexer (if not already running)
        try:
            client.run_indexer(INDEXER_NAME)
            print(f"Started indexer: {INDEXER_NAME}")
            # Give the indexer time to start processing new files
            print("Waiting for indexer to pick up new files...")
            time.sleep(15)
        except Exception as e:
            # Check if it's already running
            if "concurrent invocations are not allowed" in str(e) or "in progress" in str(e):
                print(f"Indexer already running, monitoring existing run...")
            else:
                # Different error, re-raise
                raise

        # 2) Poll status until completion
        while True:
            status = client.get_indexer_status(INDEXER_NAME)
            current_state = status.last_result.status if status.last_result else None
            execution_state = status.status

            print(f"Indexer status - execution: {execution_state}, lastResult: {current_state}")

            # If still in progress, keep waiting
            if current_state == "inProgress":
                time.sleep(5)
                continue

            # If finished successfully
            if current_state == "success":
                print("Indexing complete! New data is ready.")
                return True

            # If failed
            if current_state in ["transientFailure", "persistentFailure", "error"]:
                error_msg = f"Indexer failed with status: {current_state}"
                if status.last_result and status.last_result.errors:
                    error_msg += f"\nErrors: {status.last_result.errors}"
                print(error_msg)
                return False

            # If no last result yet (indexer just started), keep waiting
            if not current_state:
                print("Waiting for indexer to start...")
                time.sleep(5)
                continue

            # Unknown state - log and wait a bit, but break after too long
            print(f"Unknown indexer state: execution={execution_state}, result={current_state}")
            time.sleep(2)

    except Exception as e:
        print(f"An error occurred communicating with Azure Search: {e}")
        return False

def get_companies():
    
    client = SearchIndexerClient(SEARCH_ENDPOINT, AzureKeyCredential(ADMIN_KEY))

    results = client.search(
    search_text="*",
    facets=["company_name,count:1000"],
    top=0  # return only facets
    )

    unique_companies = [f["value"] for f in results.get_facets().get("company_name", [])]