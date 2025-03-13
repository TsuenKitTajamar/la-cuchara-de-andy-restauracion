from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv
import os

load_dotenv()

def list_pdf_files():
    """List all PDF files in the Azure Blob Storage container."""
    connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    container_name = os.getenv('AZURE_STORAGE_CONTAINER_NAME')  # Asegúrate de que esta variable esté en tu .env
    container_client = blob_service_client.get_container_client(container_name)
    
    pdf_files = []
    try:
        blobs = container_client.list_blobs()
        for blob in blobs:
            if blob.name.endswith('.pdf'):
                pdf_files.append(blob.name)
    except Exception as e:
        print(f"Error al listar archivos PDF: {str(e)}")
    
    return pdf_files

def test_list_pdf_files():
    """Test the list_pdf_files function."""
    pdf_files = list_pdf_files()
    if pdf_files:
        print("Archivos PDF encontrados:")
        for pdf in pdf_files:
            print(f"- {pdf}")
    else:
        print("No se encontraron archivos PDF.")

if __name__ == "__main__":
    test_list_pdf_files()