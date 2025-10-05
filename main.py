from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from azure.storage.blob import BlobServiceClient
import os

app = FastAPI()

@app.post("/upload-csv")
async def upload_csv(
    file: UploadFile = File(...),
    path: str = Form(...),  # e.g., path="dataset/user123/data.csv"
):
    if not path.endswith(".csv"):
        raise HTTPException(status_code=400, detail="The provided path must end with '.csv'.")

    try:
        contents = await file.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not read uploaded file: {e}")

    # Azure credentials from environment
    account_url = os.getenv("AZURE_ACCOUNT_URL")
    sas_token = os.getenv("AZURE_SAS_TOKEN")
    container_name = "artifacts"

    if not account_url or not sas_token:
        raise HTTPException(status_code=500, detail="Azure credentials are not configured properly.")

    try:
        blob_service_client = BlobServiceClient(account_url=account_url, credential=sas_token)
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=path)

        # Upload file contents as .csv
        blob_client.upload_blob(contents, overwrite=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading to Azure Blob Storage: {e}")

    return {"message": "Upload successful", "blob_path": path}
