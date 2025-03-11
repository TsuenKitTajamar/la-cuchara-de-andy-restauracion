from flask import Blueprint, request, jsonify, render_template
from app.services.db_service import get_db
from app.services.search_service import search_restaurants_and_dishes

customer_bp = Blueprint('customer', __name__)

@customer_bp.route('/')
@customer_bp.route('/index')
def index():
    # Obtener algunos restaurantes destacados
    db = get_db()
    featured_restaurants = list(db.restaurants.find().limit(3))
    return render_template('index.html', restaurants=featured_restaurants)

@customer_bp.route('/search')
def search():
    query = request.args.get('q', '')
    results = search_restaurants_and_dishes(query) if query else []
    return render_template('search.html', query=query, results=results)

@customer_bp.route('/restaurant/<restaurant_id>')
def restaurant_profile(restaurant_id):
    db = get_db()
    restaurant = db.restaurants.find_one({'_id': restaurant_id})
    return render_template('restaurant_profile.html', restaurant=restaurant)

@customer_bp.route('/about')
def about():
    return render_template('about.html')

@customer_bp.route('/contact')
def contact():
    return render_template('contact.html')

@customer_bp.route('/customers', methods=['GET'])
def get_customers():
    try:
        customers = Customer.query.all()
        return jsonify([customer.to_dict() for customer in customers]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@customer_bp.route('/customers/<int:customer_id>', methods=['GET'])
def get_customer(customer_id):
    try:
        customer = Customer.query.get_or_404(customer_id)
        return jsonify(customer.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@customer_bp.route('/customers', methods=['POST'])
def create_customer():
    try:
        data = request.get_json()
        new_customer = Customer(**data)
        db.session.add(new_customer)
        db.session.commit()
        return jsonify(new_customer.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@customer_bp.route('/customers/<int:customer_id>', methods=['PUT'])
def update_customer(customer_id):
    try:
        customer = Customer.query.get_or_404(customer_id)
        data = request.get_json()
        for key, value in data.items():
            setattr(customer, key, value)
        db.session.commit()
        return jsonify(customer.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@customer_bp.route('/customers/<int:customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    try:
        customer = Customer.query.get_or_404(customer_id)
        db.session.delete(customer)
        db.session.commit()
        return jsonify({'message': 'Cliente eliminado exitosamente'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
