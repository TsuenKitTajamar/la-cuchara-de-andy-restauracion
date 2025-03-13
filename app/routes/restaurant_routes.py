from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify
from app.services.db_service import (
    get_restaurant, get_restaurants, create_restaurant, update_restaurant,
    get_restaurant_menus, create_menu, get_restaurant_dishes, create_dish,
    get_active_promotions
)
from app.services.blob_service import upload_pdf, list_pdf_files
from app.services.pdf_service import extract_menu_from_pdf
from app.services.search_service import index_restaurant, index_menu, index_dish
from datetime import datetime
from bson.objectid import ObjectId
import os

restaurant_bp = Blueprint('restaurant', __name__, url_prefix='/restaurant')

@restaurant_bp.route('/')
def index():
    """Restaurant dashboard landing page."""
    # Obtener la lista de archivos PDF de los restaurantes
    restaurant_pdfs = list_pdf_files()
    
    # Paginación
    page = request.args.get('page', 1, type=int)
    per_page = 10
    total = len(restaurant_pdfs)
    start = (page - 1) * per_page
    end = start + per_page
    pdf_files_paginated = restaurant_pdfs[start:end]
    
    return render_template('restaurant/dashboard.html', restaurant_pdfs=pdf_files_paginated, total=total, page=page, per_page=per_page)

@restaurant_bp.route('/profile', methods=['GET', 'POST'])
def profile():
    """Restaurant profile management."""
    # Mock authentication - in a real app, you'd get the restaurant ID from the session
    restaurant_id = request.args.get('id')
    
    if request.method == 'POST':
        # Update restaurant profile
        data = {
            "name": request.form.get('name'),
            "description": request.form.get('description'),
            "address": request.form.get('address'),
            "location": {
                "type": "Point",
                "coordinates": [
                    float(request.form.get('longitude')),
                    float(request.form.get('latitude'))
                ]
            },
            "phone": request.form.get('phone'),
            "email": request.form.get('email'),
            "website": request.form.get('website'),
            "cuisine_type": request.form.getlist('cuisine_type'),
            "price_range": int(request.form.get('price_range')),
            "has_daily_menu": bool(request.form.get('has_daily_menu'))
        }
        
        # Handle opening hours
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        opening_hours = {}
        for day in days:
            opening_hours[day] = {
                "open": request.form.get(f'{day}_open'),
                "close": request.form.get(f'{day}_close'),
                "closed": bool(request.form.get(f'{day}_closed'))
            }
        data["opening_hours"] = opening_hours
        
        if restaurant_id:
            # Update existing restaurant
            success = update_restaurant(restaurant_id, data)
            
            # Re-index in search
            data['_id'] = ObjectId(restaurant_id)
            index_restaurant(data)
            
            flash('Perfil del restaurante actualizado con éxito', 'success')
        else:
            # Create new restaurant
            restaurant_id = create_restaurant(data)
            
            # Index in search
            data['_id'] = ObjectId(restaurant_id)
            index_restaurant(data)
            
            flash('Restaurante registrado con éxito', 'success')
        
        return redirect(url_for('restaurant.profile', id=restaurant_id))
    
    # GET request - show form
    restaurant = None
    if restaurant_id:
        restaurant = get_restaurant(restaurant_id)
    
    return render_template('restaurant/profile.html', restaurant=restaurant)

@restaurant_bp.route('/menu/upload', methods=['GET', 'POST'])
def upload_menu():
    """Upload a new menu PDF."""
    # Mock authentication - in a real app, you'd get the restaurant ID from the session
    restaurant_id = request.args.get('id')
    
    if not restaurant_id:
        flash('Se requiere ID del restaurante', 'error')
        return redirect(url_for('restaurant.index'))
    
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'menu_file' not in request.files:
            flash('No se seleccionó ningún archivo', 'error')
            return redirect(request.url)
        
        file = request.files['menu_file']
        
        # If user does not select file, browser also submits an empty part without filename
        if file.filename == '':
            flash('No se seleccionó ningún archivo', 'error')
            return redirect(request.url)
        
        if file:
            # Get form data
            menu_type = request.form.get('menu_type')
            menu_date = None
            
            if menu_type == 'daily':
                menu_date = request.form.get('menu_date')
                if not menu_date:
                    menu_date = datetime.now().strftime('%Y-%m-%d')
            
            # Process the PDF to extract menu items
            try:
                extracted_menu = extract_menu_from_pdf(file)
            except Exception as e:
                current_app.logger.error(f"Error extracting menu: {str(e)}")
                extracted_menu = {"dishes": [], "menu_restrictions": []}
            
            # Upload the file to Azure Blob Storage
            pdf_url = upload_pdf(file, restaurant_id, menu_date)
            
            # Create menu in database
            menu_data = {
                "restaurant_id": restaurant_id,
                "menu_type": menu_type,
                "date": menu_date,
                "pdf_url": pdf_url,
                "menu_restrictions": extracted_menu.get("menu_restrictions", []),
                "price": float(request.form.get('price')) if request.form.get('price') else None
            }
            
            menu_id = create_menu(menu_data)
            
            # Create dishes from extracted menu
            dish_ids = []
            restaurant_data = get_restaurant(restaurant_id)
            
            for dish_info in extracted_menu.get("dishes", []):
                dish_data = {
                    "restaurant_id": restaurant_id,
                    "name": dish_info.get("name"),
                    "description": "",
                    "price": dish_info.get("price"),
                    "category": dish_info.get("category"),
                    "restrictions": extracted_menu.get("menu_restrictions", []),
                    "is_promoted": False,
                    "promotion_level": 0
                }
                
                dish_id = create_dish(dish_data)
                dish_ids.append(dish_id)
                
                # Index dish in search
                dish_data['_id'] = ObjectId(dish_id)
                index_dish(dish_data, restaurant_data)
            
            # Update menu with dish IDs
            update_menu = {
                "dishes": dish_ids
            }
            update_restaurant_menu(menu_id, update_menu)
            
            # Index menu in search
            menu_data['_id'] = ObjectId(menu_id)
            index_menu(menu_data, restaurant_data)
            
            flash('Menú subido con éxito', 'success')
            return redirect(url_for('restaurant.menus', id=restaurant_id))
    
    restaurant = get_restaurant(restaurant_id)
    return render_template('restaurant/upload_menu.html', restaurant=restaurant)

@restaurant_bp.route('/menus')
def menus():
    """List all menus for a restaurant."""
    # Mock authentication - in a real app, you'd get the restaurant ID from the session
    restaurant_id = request.args.get('id')
    
    if not restaurant_id:
        flash('Se requiere ID del restaurante', 'error')
        return redirect(url_for('restaurant.index'))
    
    restaurant = get_restaurant(restaurant_id)
    menus = get_restaurant_menus(restaurant_id)
    
    return render_template('restaurant/menus.html', restaurant=restaurant, menus=menus)

@restaurant_bp.route('/dishes', methods=['GET', 'POST'])
def dishes():
    """Manage dishes for a restaurant."""
    # Mock authentication - in a real app, you'd get the restaurant ID from the session
    restaurant_id = request.args.get('id')
    
    if not restaurant_id:
        flash('Se requiere ID del restaurante', 'error')
        return redirect(url_for('restaurant.index'))
    
    if request.method == 'POST':
        # Create new dish
        dish_data = {
            "restaurant_id": restaurant_id,
            "name": request.form.get('name'),
            "description": request.form.get('description'),
            "price": float(request.form.get('price')),
            "category": request.form.get('category'),
            "restrictions": request.form.getlist('restrictions'),
            "ingredients": request.form.get('ingredients').split(','),
            "is_promoted": False,
            "promotion_level": 0
        }
        
        dish_id = create_dish(dish_data)
        
        # Index in search
        dish_data['_id'] = ObjectId(dish_id)
        restaurant_data = get_restaurant(restaurant_id)
        index_dish(dish_data, restaurant_data)
        
        flash('Plato creado con éxito', 'success')
        return redirect(url_for('restaurant.dishes', id=restaurant_id))
    
    restaurant = get_restaurant(restaurant_id)
    dishes = get_restaurant_dishes(restaurant_id)
    
    return render_template('restaurant/dishes.html', restaurant=restaurant, dishes=dishes)

@restaurant_bp.route('/promotions')
def promotions():
    """Manage promotions for a restaurant."""
    # Mock authentication - in a real app, you'd get the restaurant ID from the session
    restaurant_id = request.args.get('id')
    
    if not restaurant_id:
        flash('Se requiere ID del restaurante', 'error')
        return redirect(url_for('restaurant.index'))
    
    restaurant = get_restaurant(restaurant_id)
    dishes = get_restaurant_dishes(restaurant_id)
    active_promotions = get_active_promotions(restaurant_id)
    
    return render_template('restaurant/promotions.html', 
                          restaurant=restaurant, 
                          dishes=dishes,
                          promotions=active_promotions)

@restaurant_bp.route('/analytics')
def analytics():
    """View analytics for a restaurant."""
    # Mock authentication - in a real app, you'd get the restaurant ID from the session
    restaurant_id = request.args.get('id')
    
    if not restaurant_id:
        flash('Se requiere ID del restaurante', 'error')
        return redirect(url_for('restaurant.index'))
    
    restaurant = get_restaurant(restaurant_id)
    
    return render_template('restaurant/analytics.html', restaurant=restaurant)

@restaurant_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Página de inicio de sesión del restaurante."""
    if request.method == 'POST':
        # Lógica de autenticación aquí
        pass  # Reemplaza esto con tu lógica de autenticación

    return render_template('restaurant/login.html')  # Asegúrate de tener esta plantilla

# API endpoints for AJAX calls
@restaurant_bp.route('/api/dishes', methods=['GET'])
def api_dishes():
    """API endpoint to get restaurant dishes."""
    restaurant_id = request.args.get('id')
    
    if not restaurant_id:
        return jsonify({'error': 'Se requiere ID del restaurante'}), 400
    
    dishes = get_restaurant_dishes(restaurant_id)
    return jsonify({'dishes': dishes})

@restaurant_bp.route('/<restaurant_name>/menu')
def view_menu(restaurant_name):
    """Mostrar el menú de un restaurante específico."""
    # Aquí puedes implementar la lógica para obtener el menú del restaurante
    # usando el nombre del restaurante (restaurant_name).
    return render_template('restaurant/menu.html', restaurant_name=restaurant_name)