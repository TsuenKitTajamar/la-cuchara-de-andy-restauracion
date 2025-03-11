# La Cuchara - Plataforma de Gestión de Restaurantes

## Descripción
La Cuchara es una plataforma web que permite a los restaurantes gestionar su presencia digital y a los clientes descubrir y explorar opciones gastronómicas.

## Estructura del proyecto:

```bash
lacuchara/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── restaurant.py
│   │   ├── menu.py
│   │   ├── dish.py
│   │   ├── rating.py
│   │   └── promotion.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── db_service.py
│   │   ├── blob_service.py
│   │   ├── search_service.py
│   │   └── pdf_service.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── restaurant_routes.py
│   │   ├── customer_routes.py
│   │   └── admin_routes.py
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   │   └── img/
│   └── templates/
│       ├── base.html
│       ├── index.html
│       ├── search.html
│       ├── restaurant_profile.html
│       └── admin/
│           ├── dashboard.html
│           └── promotion.html
├── requirements.txt
└── run.py
```

### Componentes Principales

#### 1. Modelos (`app/models/`)
- `restaurant.py`: Define la estructura de datos para los restaurantes
- `menu.py`: Gestiona la información de los menús
- `dish.py`: Maneja los platos individuales
- `rating.py`: Sistema de calificaciones y reseñas
- `promotion.py`: Gestión de promociones y ofertas especiales

#### 2. Servicios (`app/services/`)
- `db_service.py`: Gestión de conexiones y operaciones con la base de datos
- `blob_service.py`: Manejo de almacenamiento de archivos (imágenes, documentos)
- `search_service.py`: Motor de búsqueda para restaurantes y platos
- `pdf_service.py`: Generación de PDFs (menús, reportes)

#### 3. Rutas (`app/routes/`)
- `restaurant_routes.py`: Endpoints para gestión de restaurantes
- `customer_routes.py`: Rutas para la experiencia del cliente
- `admin_routes.py`: Funcionalidades de administración

#### 4. Interfaz de Usuario
- **Templates** (`app/templates/`): Plantillas HTML para las diferentes vistas
- **Static** (`app/static/`): Archivos estáticos (CSS, JavaScript, imágenes)


### Requisitos del Sistema
Primero, crea un entorno virtual y actívalo:
```bash
# Crear el entorno virtual
python -m venv venv

# Activar el entorno virtual
# En Windows:
venv\Scripts\activate
# En macOS/Linux:
source venv/bin/activate
```

Los requisitos se encuentran en `requirements.txt`. Para instalarlos:
```bash
pip install -r requirements.txt
```

### Configuración
El archivo `config.py` contiene las configuraciones del proyecto:
- Configuración de la base de datos
- Claves API
- Variables de entorno
- Configuraciones de seguridad

### Ejecución
Para iniciar la aplicación:
```bash
python run.py
```

### Características Principales
1. **Para Restaurantes:**
   - Gestión de perfil y menú
   - Publicación de promociones
   - Análisis de estadísticas
   - Generación de menús PDF

2. **Para Clientes:**
   - Búsqueda de restaurantes
   - Visualización de menús
   - Sistema de calificaciones
   - Acceso a promociones

3. **Para Administradores:**
   - Panel de control
   - Gestión de usuarios
   - Moderación de contenido
   - Reportes y análisis

### Contribución
Para contribuir al proyecto:
1. Fork del repositorio
2. Crear una rama para tu función (`git checkout -b feature/NuevaFuncion`)
3. Commit de cambios (`git commit -m 'Añadir nueva función'`)
4. Push a la rama (`git push origin feature/NuevaFuncion`)
5. Crear Pull Request

### Licencia
[Especificar tipo de licencia]

### Contacto
[Información de contacto del equipo]