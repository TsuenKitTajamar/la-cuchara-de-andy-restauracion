# This file intentionally left empty to mark directory as Python package

from flask import Blueprint
from .restaurant_routes import restaurant_bp
from .customer_routes import customer_bp
from .admin_routes import admin_bp

def register_routes(app):
    app.register_blueprint(restaurant_bp)
    app.register_blueprint(customer_bp)
    app.register_blueprint(admin_bp)

__all__ = ['restaurant_bp', 'customer_bp', 'admin_bp']