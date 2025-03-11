from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv
import os

load_dotenv()

def test_storage_connection():
    try:
        # Obtener la cadena de conexión
        connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
        print("Cadena de conexión obtenida")
        
        # Crear el cliente
        blob_service_client = BlobServiceClient.from_connection_string(connect_str)
        print("Cliente creado exitosamente")
        
        # Listar los containers (esto prueba la conexión)
        containers = blob_service_client.list_containers()
        print("Containers disponibles:")
        for container in containers:
            print(f"- {container.name}")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_storage_connection()