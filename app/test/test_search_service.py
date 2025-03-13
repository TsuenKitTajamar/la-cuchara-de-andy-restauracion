import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Azure AI Search Configuration
SERVICE_NAME = os.getenv("AZURE_SEARCH_SERVICE_NAME").strip("/")  # Ensure no trailing slash
INDEX_NAME = "la-cuchara-index"  # Change if necessary
API_VERSION = "2023-11-01"  # Use a supported version
API_KEY = os.getenv("AZURE_SEARCH_ADMIN_KEY")  # Ensure this is set in .env

# Construct the search URL correctly
SEARCH_URL = f"{SERVICE_NAME}/indexes/{INDEX_NAME}/docs/search?api-version={API_VERSION}"

def pretty_print_json(data):
    """
    Print the JSON response in a nice and formatted way with indentation
    """
    print(json.dumps(data, indent=4, ensure_ascii=False))

def test_search_restaurants_and_dishes(query="jamón"):
    try:
        headers = {
            "Content-Type": "application/json",
            "api-key": API_KEY
        }
        
        search_payload = {
            "search": query,   # Palabra clave de búsqueda
            "top": 5,          # Número de resultados a devolver
            "select": "metadata_storage_name, metadata_storage_path", # Campos a devolver
            "count": True      # Incluir número total de resultados
        }

        response = requests.post(SEARCH_URL, headers=headers, json=search_payload)
        response.raise_for_status()  # Raise error if request fails
        
        # Show the raw response nicely formatted
        print("\n🔍 Respuesta completa de búsqueda en formato JSON (formateada):")
        pretty_print_json(response.json())  # Formatted JSON output
        
        results = response.json()
        
        # Extract and display results
        print(f"\n🔍 Resultados para la búsqueda: '{query}'")
        total_results = results.get('count', 0)
        print(f"Total de resultados encontrados: {total_results}\n")
        
        # Show individual results in a more visual format
        if results.get("value"):
            for i, result in enumerate(results["value"], start=1):
                metadata_storage_name = result.get("metadata_storage_name", "Desconocido")

                # Mostrar el nombre del archivo PDF y su ruta
                print(f"\033[1;32m{i}. {metadata_storage_name}\033[0m")  # Verde para el nombre
        else:
            print("No se encontraron resultados para tu búsqueda.")
        
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Error en la búsqueda: {e}")

if __name__ == "__main__":
    test_search_restaurants_and_dishes()
