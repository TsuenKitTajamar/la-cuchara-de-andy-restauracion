from flask import Flask
from .services.db_service import init_db
from .services.blob_service import init_blob_service
from .routes import register_routes

def create_app():
    app = Flask(__name__)
    
    # Cargar configuración
    app.config.from_object('app.config.Config')
    print("Configuración cargada")
    
    # Inicializar servicios
    try:
        init_db(app)
        print("Base de datos inicializada")
        # init_blob_service(app)  # Comentado temporalmente
    except Exception as e:
        print(f"Error al inicializar servicios: {str(e)}")
    
    # Registrar rutas
    register_routes(app)
    print("Rutas registradas")
    
    return app