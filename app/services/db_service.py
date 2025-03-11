from pymongo import MongoClient, GEOSPHERE
from flask import current_app, g
from bson.objectid import ObjectId
import datetime

def get_db():
    """Return a handle to the MongoDB database."""
    if 'db' not in g:
        # Ajustamos las opciones del cliente para Cosmos DB
        client_options = {
            "retryWrites": False,  # Cosmos DB no soporta retryWrites
            "serverSelectionTimeoutMS": 5000,
            "socketTimeoutMS": 10000,
            "connectTimeoutMS": 10000,
        }
        g.client = MongoClient(current_app.config['MONGO_URI'], **client_options)
        g.db = g.client[current_app.config['MONGO_DB_NAME']]
    return g.db

def close_db(e=None):
    """Close the MongoDB connection."""
    client = g.pop('client', None)
    if client is not None:
        client.close()

def init_db(app):
    """Initialize the database."""
    with app.app_context():
        db = get_db()
        
        try:
            # Creamos los índices sin la opción partitionKey
            db.restaurants.create_index([("location", GEOSPHERE)])
            db.restaurants.create_index([("name", 1)])
            db.dishes.create_index([("name", 1)])
            db.dishes.create_index([("restaurant_id", 1)])
            db.dishes.create_index([("is_promoted", 1)])
            db.menus.create_index([("restaurant_id", 1), ("date", -1)])
            db.ratings.create_index([("restaurant_id", 1), ("dish_id", 1)])
            db.promotions.create_index([("dish_id", 1), ("is_active", 1)])
            
            print("Índices creados exitosamente")
        except Exception as e:
            print(f"Error al crear índices: {str(e)}")
            
        app.teardown_appcontext(close_db)

# Restaurant operations
def get_restaurant(restaurant_id):
    db = get_db()
    return db.restaurants.find_one({"_id": ObjectId(restaurant_id)})

def get_restaurants(filters=None, sort=None, limit=20, skip=0):
    db = get_db()
    query = filters or {}
    cursor = db.restaurants.find(query)
    
    if sort:
        cursor = cursor.sort(sort)
    
    return list(cursor.skip(skip).limit(limit))

def create_restaurant(restaurant_data):
    db = get_db()
    restaurant_data["created_at"] = datetime.datetime.utcnow()
    restaurant_data["updated_at"] = datetime.datetime.utcnow()
    result = db.restaurants.insert_one(restaurant_data)
    return str(result.inserted_id)

def update_restaurant(restaurant_id, restaurant_data):
    db = get_db()
    restaurant_data["updated_at"] = datetime.datetime.utcnow()
    db.restaurants.update_one(
        {"_id": ObjectId(restaurant_id)},
        {"$set": restaurant_data}
    )
    return True

def delete_restaurant(restaurant_id):
    db = get_db()
    db.restaurants.update_one(
        {"_id": ObjectId(restaurant_id)},
        {"$set": {"active": False, "updated_at": datetime.datetime.utcnow()}}
    )
    return True

# Menu operations
def get_menu(menu_id):
    db = get_db()
    return db.menus.find_one({"_id": ObjectId(menu_id)})

def get_restaurant_menus(restaurant_id, menu_type=None, date=None):
    db = get_db()
    query = {"restaurant_id": restaurant_id, "active": True}
    
    if menu_type:
        query["menu_type"] = menu_type
    
    if date:
        query["date"] = date
    
    return list(db.menus.find(query).sort("date", -1))

def create_menu(menu_data):
    db = get_db()
    menu_data["created_at"] = datetime.datetime.utcnow()
    menu_data["updated_at"] = datetime.datetime.utcnow()
    result = db.menus.insert_one(menu_data)
    return str(result.inserted_id)

def update_menu(menu_id, menu_data):
    db = get_db()
    menu_data["updated_at"] = datetime.datetime.utcnow()
    db.menus.update_one(
        {"_id": ObjectId(menu_id)},
        {"$set": menu_data}
    )
    return True

def delete_menu(menu_id):
    db = get_db()
    db.menus.update_one(
        {"_id": ObjectId(menu_id)},
        {"$set": {"active": False, "updated_at": datetime.datetime.utcnow()}}
    )
    return True

# Dish operations
def get_dish(dish_id):
    db = get_db()
    return db.dishes.find_one({"_id": ObjectId(dish_id)})

def get_restaurant_dishes(restaurant_id, filters=None):
    db = get_db()
    query = {"restaurant_id": restaurant_id, "active": True}
    
    if filters:
        query.update(filters)
    
    return list(db.dishes.find(query))

def create_dish(dish_data):
    db = get_db()
    dish_data["created_at"] = datetime.datetime.utcnow()
    dish_data["updated_at"] = datetime.datetime.utcnow()
    result = db.dishes.insert_one(dish_data)
    return str(result.inserted_id)

def update_dish(dish_id, dish_data):
    db = get_db()
    dish_data["updated_at"] = datetime.datetime.utcnow()
    db.dishes.update_one(
        {"_id": ObjectId(dish_id)},
        {"$set": dish_data}
    )
    return True

def delete_dish(dish_id):
    db = get_db()
    db.dishes.update_one(
        {"_id": ObjectId(dish_id)},
        {"$set": {"active": False, "updated_at": datetime.datetime.utcnow()}}
    )
    return True

# Rating operations
def create_rating(rating_data):
    db = get_db()
    rating_data["created_at"] = datetime.datetime.utcnow()
    rating_data["updated_at"] = datetime.datetime.utcnow()
    result = db.ratings.insert_one(rating_data)
    
    # Update restaurant average rating
    if "dish_id" not in rating_data or not rating_data["dish_id"]:
        # Restaurant rating
        update_restaurant_avg_rating(rating_data["restaurant_id"])
    else:
        # Dish rating
        update_dish_avg_rating(rating_data["dish_id"])
    
    return str(result.inserted_id)

def update_restaurant_avg_rating(restaurant_id):
    db = get_db()
    pipeline = [
        {"$match": {"restaurant_id": restaurant_id, "dish_id": None, "active": True}},
        {"$group": {"_id": "$restaurant_id", "avg_rating": {"$avg": "$rating_value"}, "count": {"$sum": 1}}}
    ]
    result = list(db.ratings.aggregate(pipeline))
    
    if result:
        db.restaurants.update_one(
            {"_id": ObjectId(restaurant_id)},
            {"$set": {
                "avg_rating": result[0]["avg_rating"],
                "rating_count": result[0]["count"],
                "updated_at": datetime.datetime.utcnow()
            }}
        )

def update_dish_avg_rating(dish_id):
    db = get_db()
    pipeline = [
        {"$match": {"dish_id": dish_id, "active": True}},
        {"$group": {"_id": "$dish_id", "avg_rating": {"$avg": "$rating_value"}, "count": {"$sum": 1}}}
    ]
    result = list(db.ratings.aggregate(pipeline))
    
    if result:
        db.dishes.update_one(
            {"_id": ObjectId(dish_id)},
            {"$set": {
                "avg_rating": result[0]["avg_rating"],
                "rating_count": result[0]["count"],
                "updated_at": datetime.datetime.utcnow()
            }}
        )

# Promotion operations
def create_promotion(promotion_data):
    db = get_db()
    promotion_data["created_at"] = datetime.datetime.utcnow()
    promotion_data["updated_at"] = datetime.datetime.utcnow()
    
    # Update dish promotion status
    db.dishes.update_one(
        {"_id": ObjectId(promotion_data["dish_id"])},
        {"$set": {
            "is_promoted": True,
            "promotion_level": promotion_data["level"],
            "updated_at": datetime.datetime.utcnow()
        }}
    )
    
    result = db.promotions.insert_one(promotion_data)
    return str(result.inserted_id)

def get_active_promotions(restaurant_id=None):
    db = get_db()
    now = datetime.datetime.utcnow()
    query = {
        "is_active": True,
        "start_date": {"$lte": now},
        "end_date": {"$gte": now}
    }
    
    if restaurant_id:
        query["restaurant_id"] = restaurant_id
    
    return list(db.promotions.find(query))

def deactivate_expired_promotions():
    db = get_db()
    now = datetime.datetime.utcnow()
    
    # Find expired promotions
    expired = list(db.promotions.find({
        "is_active": True,
        "end_date": {"$lt": now}
    }))
    
    # Update promotion status
    db.promotions.update_many(
        {"_id": {"$in": [p["_id"] for p in expired]}},
        {"$set": {"is_active": False, "updated_at": now}}
    )
    
    # Update dish promotion status
    for promotion in expired:
        db.dishes.update_one(
            {"_id": ObjectId(promotion["dish_id"])},
            {"$set": {
                "is_promoted": False,
                "promotion_level": 0,
                "updated_at": now
            }}
        )
    
    return len(expired)