from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex, 
    SimpleField, 
    SearchableField, 
    ComplexField,
    SearchFieldDataType
)
from azure.core.credentials import AzureKeyCredential
from flask import current_app, g

def get_search_admin_client():
    """Return a handle to the Azure Search admin client."""
    if 'search_admin_client' not in g:
        service_name = current_app.config['AZURE_SEARCH_SERVICE_NAME']
        admin_key = current_app.config['AZURE_SEARCH_ADMIN_KEY']
        endpoint = f"https://{service_name}.search.windows.net"
        credential = AzureKeyCredential(admin_key)
        g.search_admin_client = SearchIndexClient(endpoint=endpoint, credential=credential)
    return g.search_admin_client

def get_search_client():
    """Obtener el cliente de Azure Search."""
    search_service = current_app.config['AZURE_SEARCH_SERVICE_NAME']
    search_key = current_app.config['AZURE_SEARCH_ADMIN_KEY']
    index_name = current_app.config['AZURE_SEARCH_INDEX_NAME']
    
    endpoint = f"https://{search_service}.search.windows.net"
    credential = AzureKeyCredential(search_key)
    
    return SearchClient(endpoint=endpoint,
                       index_name=index_name,
                       credential=credential)

def close_search_clients(e=None):
    """Close the Azure Search clients."""
    g.pop('search_admin_client', None)
    g.pop('search_client', None)

def init_search_service(app):
    """Initialize the Azure Search service."""
    with app.app_context():
        admin_client = get_search_admin_client()
        index_name = app.config['AZURE_SEARCH_INDEX_NAME']
        
        # Check if index exists, create if not
        try:
            admin_client.get_index(index_name)
        except Exception as e:
            # Index doesn't exist, create it
            create_search_index(admin_client, index_name)
        
        app.teardown_appcontext(close_search_clients)

def create_search_index(admin_client, index_name):
    """Create the search index for menu and dish data."""
    
    # Define the index fields
    fields = [
        SimpleField(name="id", type=SearchFieldDataType.String, key=True),
        SimpleField(name="type", type=SearchFieldDataType.String, filterable=True),  # 'restaurant', 'dish', 'menu'
        SimpleField(name="restaurant_id", type=SearchFieldDataType.String, filterable=True),
        SimpleField(name="dish_id", type=SearchFieldDataType.String, filterable=True),
        SimpleField(name="menu_id", type=SearchFieldDataType.String, filterable=True),
        SearchableField(name="name", type=SearchFieldDataType.String, filterable=True, sortable=True),
        SearchableField(name="description", type=SearchFieldDataType.String),
        SearchableField(name="category", type=SearchFieldDataType.String, filterable=True),
        SimpleField(name="price", type=SearchFieldDataType.Double, filterable=True, sortable=True),
        SimpleField(name="date", type=SearchFieldDataType.DateTimeOffset, filterable=True, sortable=True),
        SimpleField(name="menu_type", type=SearchFieldDataType.String, filterable=True),
        SearchableField(name="cuisine_type", type=SearchFieldDataType.Collection(SearchFieldDataType.String), filterable=True),
        SearchableField(name="restrictions", type=SearchFieldDataType.Collection(SearchFieldDataType.String), filterable=True),
        SearchableField(name="ingredients", type=SearchFieldDataType.Collection(SearchFieldDataType.String), filterable=True),
        SimpleField(name="is_promoted", type=SearchFieldDataType.Boolean, filterable=True),
        SimpleField(name="promotion_level", type=SearchFieldDataType.Int32, filterable=True, sortable=True),
        SimpleField(name="avg_rating", type=SearchFieldDataType.Double, filterable=True, sortable=True),
        SimpleField(name="rating_count", type=SearchFieldDataType.Int32, filterable=True, sortable=True),
        ComplexField(name="location", fields=[
            SimpleField(name="latitude", type=SearchFieldDataType.Double),
            SimpleField(name="longitude", type=SearchFieldDataType.Double)
        ])
    ]
    
    # Create the index
    index = SearchIndex(name=index_name, fields=fields)
    admin_client.create_index(index)
    return index

def index_restaurant(restaurant_data):
    """
    Index a restaurant document in Azure Search.
    
    Args:
        restaurant_data: A dictionary containing restaurant data
    """
    search_client = get_search_client()
    
    # Prepare the document for indexing
    document = {
        "id": f"restaurant_{restaurant_data['_id']}",
        "type": "restaurant",
        "restaurant_id": str(restaurant_data['_id']),
        "name": restaurant_data['name'],
        "description": restaurant_data.get('description', ''),
        "cuisine_type": restaurant_data.get('cuisine_type', []),
        "avg_rating": restaurant_data.get('avg_rating', 0),
        "rating_count": restaurant_data.get('rating_count', 0),
        "price": float(restaurant_data.get('price_range', 0)),
        "location": {
            "latitude": restaurant_data.get('location', {}).get('coordinates', [0, 0])[1],
            "longitude": restaurant_data.get('location', {}).get('coordinates', [0, 0])[0]
        }
    }
    
    # Index the document
    search_client.upload_documents(documents=[document])
    return True

def index_dish(dish_data, restaurant_data=None):
    """
    Index a dish document in Azure Search.
    
    Args:
        dish_data: A dictionary containing dish data
        restaurant_data: Optional restaurant data for enriching the document
    """
    search_client = get_search_client()
    
    # Prepare the document for indexing
    document = {
        "id": f"dish_{dish_data['_id']}",
        "type": "dish",
        "dish_id": str(dish_data['_id']),
        "restaurant_id": dish_data['restaurant_id'],
        "name": dish_data['name'],
        "description": dish_data.get('description', ''),
        "category": dish_data.get('category', ''),
        "price": float(dish_data.get('price', 0)),
        "restrictions": dish_data.get('restrictions', []),
        "ingredients": dish_data.get('ingredients', []),
        "is_promoted": dish_data.get('is_promoted', False),
        "promotion_level": dish_data.get('promotion_level', 0),
        "avg_rating": dish_data.get('avg_rating', 0),
        "rating_count": dish_data.get('rating_count', 0)
    }
    
    # Add restaurant data if available
    if restaurant_data:
        document["cuisine_type"] = restaurant_data.get('cuisine_type', [])
        document["location"] = {
            "latitude": restaurant_data.get('location', {}).get('coordinates', [0, 0])[1],
            "longitude": restaurant_data.get('location', {}).get('coordinates', [0, 0])[0]
        }
    
    # Index the document
    search_client.upload_documents(documents=[document])
    return True

def index_menu(menu_data, restaurant_data=None, dishes_data=None):
    """
    Index a menu document in Azure Search.
    
    Args:
        menu_data: A dictionary containing menu data
        restaurant_data: Optional restaurant data for enriching the document
        dishes_data: Optional list of dishes in the menu
    """
    search_client = get_search_client()
    
    # Prepare the document for indexing
    document = {
        "id": f"menu_{menu_data['_id']}",
        "type": "menu",
        "menu_id": str(menu_data['_id']),
        "restaurant_id": menu_data['restaurant_id'],
        "menu_type": menu_data.get('menu_type', ''),
        "date": menu_data.get('date', None),
        "price": float(menu_data.get('price', 0)) if menu_data.get('price') else None,
        "restrictions": menu_data.get('menu_restrictions', [])
    }
    
    # Add restaurant data if available
    if restaurant_data:
        document["name"] = restaurant_data.get('name', '')
        document["cuisine_type"] = restaurant_data.get('cuisine_type', [])
        document["location"] = {
            "latitude": restaurant_data.get('location', {}).get('coordinates', [0, 0])[1],
            "longitude": restaurant_data.get('location', {}).get('coordinates', [0, 0])[0]
        }
    
    # Add dishes data if available
    if dishes_data:
        document["description"] = ", ".join([d.get('name', '') for d in dishes_data])
    
    # Index the document
    search_client.upload_documents(documents=[document])
    return True

def search_restaurants(query_text="*", filters=None, sort=None, top=10, skip=0):
    """
    Search for restaurants based on a text query and filters.
    
    Args:
        query_text: The text to search for
        filters: Optional filter expressions
        sort: Optional sort expressions
        top: Number of results to return
        skip: Number of results to skip
    
    Returns:
        A list of search results
    """
    search_client = get_search_client()
    
    # Add type filter
    if filters:
        filters = f"type eq 'restaurant' and {filters}"
    else:
        filters = "type eq 'restaurant'"
    
    # Execute the search
    results = search_client.search(
        search_text=query_text,
        filter=filters,
        order_by=sort,
        top=top,
        skip=skip,
        include_total_count=True
    )
    
    # Process the results
    search_results = []
    for result in results:
        search_results.append(result)
    
    return {
        "total": results.get_count(),
        "results": search_results
    }

def search_dishes(query_text="*", filters=None, sort=None, top=10, skip=0):
    """
    Search for dishes based on a text query and filters.
    
    Args:
        query_text: The text to search for
        filters: Optional filter expressions
        sort: Optional sort expressions
        top: Number of results to return
        skip: Number of results to skip
    
    Returns:
        A list of search results
    """
    search_client = get_search_client()
    
    # Add type filter
    if filters:
        filters = f"type eq 'dish' and {filters}"
    else:
        filters = "type eq 'dish'"
    
    # Execute the search
    results = search_client.search(
        search_text=query_text,
        filter=filters,
        order_by=sort,
        top=top,
        skip=skip,
        include_total_count=True
    )
    
    # Process the results
    search_results = []
    for result in results:
        search_results.append(result)
    
    return {
        "total": results.get_count(),
        "results": search_results
    }

def search_menus(query_text="*", filters=None, sort=None, top=10, skip=0):
    """
    Search for menus based on a text query and filters.
    
    Args:
        query_text: The text to search for
        filters: Optional filter expressions
        sort: Optional sort expressions
        top: Number of results to return
        skip: Number of results to skip
    
    Returns:
        A list of search results
    """
    search_client = get_search_client()
    
    # Add type filter
    if filters:
        filters = f"type eq 'menu' and {filters}"
    else:
        filters = "type eq 'menu'"
    
    # Execute the search
    results = search_client.search(
        search_text=query_text,
        filter=filters,
        order_by=sort,
        top=top,
        skip=skip,
        include_total_count=True
    )
    
    # Process the results
    search_results = []
    for result in results:
        search_results.append(result)
    
    return {
        "total": results.get_count(),
        "results": search_results
    }

def delete_document(doc_id):
    """
    Delete a document from the search index.
    
    Args:
        doc_id: The ID of the document to delete
    """
    search_client = get_search_client()
    search_client.delete_documents(documents=[{"id": doc_id}])
    return True

def search_restaurants_and_dishes(query, limit=50):
    """
    Buscar restaurantes y platos que coincidan con la consulta.
    
    Args:
        query (str): Texto a buscar
        limit (int): Número máximo de resultados
    
    Returns:
        list: Lista de resultados (restaurantes y platos)
    """
    try:
        client = get_search_client()
        
        # Realizar la búsqueda
        results = client.search(
            search_text=query,
            select=["id", "type", "name", "description", "cuisine", "price", "restaurant_id"],
            top=limit
        )
        
        # Convertir resultados a lista
        return list(results)
        
    except Exception as e:
        print(f"Error en la búsqueda: {str(e)}")
        return []