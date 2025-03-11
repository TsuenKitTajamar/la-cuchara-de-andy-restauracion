from azure.storage.blob import BlobServiceClient, ContentSettings
from flask import current_app, g
import uuid
import os

def get_blob_service():
    """Return a handle to the Azure Blob Storage service."""
    if 'blob_service' not in g:
        conn_str = current_app.config['AZURE_STORAGE_CONNECTION_STRING']
        g.blob_service = BlobServiceClient.from_connection_string(conn_str)
    return g.blob_service

def close_blob_service(e=None):
    """Close the Azure Blob Storage connection."""
    blob_service = g.pop('blob_service', None)
    # No need to explicitly close the BlobServiceClient

def init_blob_service(app):
    """Initialize Azure Blob Storage."""
    with app.app_context():
        blob_service = get_blob_service()
        container_name = app.config['AZURE_STORAGE_CONTAINER_NAME']
        
        # Check if container exists, create if not
        try:
            container_client = blob_service.get_container_client(container_name)
            container_client.get_container_properties()
        except Exception as e:
            # Container doesn't exist, create it
            container_client = blob_service.create_container(container_name)
        
        app.teardown_appcontext(close_blob_service)

def upload_pdf(file_data, restaurant_id, menu_date=None):
    """
    Upload a PDF file to Azure Blob Storage.
    
    Args:
        file_data: The file data to upload
        restaurant_id: The ID of the restaurant
        menu_date: Optional date string for daily menus
    
    Returns:
        The URL of the uploaded file
    """
    blob_service = get_blob_service()
    container_name = current_app.config['AZURE_STORAGE_CONTAINER_NAME']
    container_client = blob_service.get_container_client(container_name)
    
    # Generate a unique blob name
    date_part = f"_{menu_date}" if menu_date else ""
    blob_name = f"{restaurant_id}{date_part}_{uuid.uuid4()}.pdf"
    
    # Upload the file
    blob_client = container_client.get_blob_client(blob_name)
    content_settings = ContentSettings(content_type='application/pdf')
    
    blob_client.upload_blob(
        file_data,
        content_settings=content_settings,
        overwrite=True
    )
    
    # Return the URL
    return blob_client.url

def delete_pdf(blob_url):
    """
    Delete a PDF file from Azure Blob Storage.
    
    Args:
        blob_url: The URL of the blob to delete
    
    Returns:
        Boolean indicating success
    """
    blob_service = get_blob_service()
    container_name = current_app.config['AZURE_STORAGE_CONTAINER_NAME']
    container_client = blob_service.get_container_client(container_name)
    
    # Extract blob name from URL
    blob_name = blob_url.split('/')[-1]
    
    # Delete the blob
    blob_client = container_client.get_blob_client(blob_name)
    blob_client.delete_blob()
    
    return True