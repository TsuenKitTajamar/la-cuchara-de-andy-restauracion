import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    
    # MongoDB config (actualizado para Cosmos DB)
    MONGO_URI = os.environ.get('COSMOS_DB_CONNECTION_STRING')
    MONGO_DB_NAME = os.environ.get('COSMOS_DB_NAME')
    
    # Azure Blob Storage config
    AZURE_STORAGE_CONNECTION_STRING = os.environ.get('AZURE_STORAGE_CONNECTION_STRING')
    AZURE_STORAGE_CONTAINER_NAME = os.environ.get('AZURE_STORAGE_CONTAINER_NAME')
    
    # Azure Search config
    AZURE_SEARCH_SERVICE_NAME = os.environ.get('AZURE_SEARCH_SERVICE_NAME')
    AZURE_SEARCH_ADMIN_KEY = os.environ.get('AZURE_SEARCH_ADMIN_KEY')
    AZURE_SEARCH_INDEX_NAME = os.environ.get('AZURE_SEARCH_INDEX_NAME') or 'lacuchara-index'
    
    # Application config
    MENUS_PER_PAGE = 10
    DEFAULT_SEARCH_RADIUS_KM = 5