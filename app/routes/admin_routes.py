from flask import Blueprint, request, jsonify
from app.services.db_service import (
    get_restaurants, 
    update_restaurant,
    delete_restaurant,
    get_restaurant_dishes,
    update_dish,
    delete_dish,
    deactivate_expired_promotions
)
from app.services.search_service import (
    index_restaurant,
    index_dish,
    delete_document
)
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/restaurants', methods=['GET'])
def list_restaurants():
    filters = request.args.get('filters', {})
    sort = request.args.get('sort')
    limit = int(request.args.get('limit', 20))
    skip = int(request.args.get('skip', 0))
    
    restaurants = get_restaurants(filters, sort, limit, skip)
    return jsonify(restaurants)

@admin_bp.route('/admin/restaurants/<restaurant_id>', methods=['PUT'])
def update_restaurant_status(restaurant_id):
    data = request.get_json()
    
    # Actualizar en la base de datos
    success = update_restaurant(restaurant_id, data)
    
    if success:
        # Reindexar en Azure Search
        restaurant_data = get_restaurants({"_id": restaurant_id})[0]
        index_restaurant(restaurant_data)
        
        return jsonify({"message": "Restaurante actualizado exitosamente"})
    return jsonify({"error": "Error al actualizar el restaurante"}), 400

@admin_bp.route('/admin/restaurants/<restaurant_id>', methods=['DELETE'])
def remove_restaurant(restaurant_id):
    success = delete_restaurant(restaurant_id)
    
    if success:
        # Eliminar del índice de búsqueda
        delete_document(f"restaurant_{restaurant_id}")
        return jsonify({"message": "Restaurante eliminado exitosamente"})
    return jsonify({"error": "Error al eliminar el restaurante"}), 400

@admin_bp.route('/admin/restaurants/<restaurant_id>/dishes', methods=['GET'])
def list_restaurant_dishes(restaurant_id):
    filters = request.args.get('filters', {})
    dishes = get_restaurant_dishes(restaurant_id, filters)
    return jsonify(dishes)

@admin_bp.route('/admin/dishes/<dish_id>', methods=['PUT'])
def update_dish_status(dish_id):
    data = request.get_json()
    
    # Actualizar en la base de datos
    success = update_dish(dish_id, data)
    
    if success:
        # Reindexar en Azure Search
        dish_data = get_restaurant_dishes({"_id": dish_id})[0]
        index_dish(dish_data)
        
        return jsonify({"message": "Plato actualizado exitosamente"})
    return jsonify({"error": "Error al actualizar el plato"}), 400

@admin_bp.route('/admin/dishes/<dish_id>', methods=['DELETE'])
def remove_dish(dish_id):
    success = delete_dish(dish_id)
    
    if success:
        # Eliminar del índice de búsqueda
        delete_document(f"dish_{dish_id}")
        return jsonify({"message": "Plato eliminado exitosamente"})
    return jsonify({"error": "Error al eliminar el plato"}), 400

@admin_bp.route('/admin/promotions/cleanup', methods=['POST'])
def cleanup_expired_promotions():
    count = deactivate_expired_promotions()
    return jsonify({
        "message": f"Se desactivaron {count} promociones expiradas",
        "deactivated_count": count
    })
