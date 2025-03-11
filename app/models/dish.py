from datetime import datetime

class Dish:
    def __init__(self, restaurant_id, name, description, price, category, 
                 restrictions=None, ingredients=None, is_promoted=False, 
                 promotion_level=0, id=None):
        self.id = id
        self.restaurant_id = restaurant_id
        self.name = name
        self.description = description
        self.price = price
        self.category = category  # 'starter', 'main', 'dessert', etc.
        self.restrictions = restrictions or []  # ['vegetarian', 'vegan', 'gluten-free', etc.]
        self.ingredients = ingredients or []
        self.is_promoted = is_promoted
        self.promotion_level = promotion_level  # 0-5, 0 means no promotion
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.active = True
        self.avg_rating = 0
        self.rating_count = 0
    
    def to_dict(self):
        return {
            "restaurant_id": self.restaurant_id,
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "category": self.category,
            "restrictions": self.restrictions,
            "ingredients": self.ingredients,
            "is_promoted": self.is_promoted,
            "promotion_level": self.promotion_level,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "active": self.active,
            "avg_rating": self.avg_rating,
            "rating_count": self.rating_count
        }
    
    @classmethod
    def from_dict(cls, data):
        dish = cls(
            restaurant_id=data.get('restaurant_id'),
            name=data.get('name'),
            description=data.get('description'),
            price=data.get('price'),
            category=data.get('category'),
            restrictions=data.get('restrictions'),
            ingredients=data.get('ingredients'),
            is_promoted=data.get('is_promoted', False),
            promotion_level=data.get('promotion_level', 0),
            id=data.get('_id')
        )
        dish.created_at = data.get('created_at', datetime.utcnow())
        dish.updated_at = data.get('updated_at', datetime.utcnow())
        dish.active = data.get('active', True)
        dish.avg_rating = data.get('avg_rating', 0)
        dish.rating_count = data.get('rating_count', 0)
        return dish