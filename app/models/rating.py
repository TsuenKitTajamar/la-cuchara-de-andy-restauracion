from datetime import datetime

class Rating:
    def __init__(self, customer_id, restaurant_id, rating_value, comment=None, 
                 dish_id=None, id=None):
        self.id = id
        self.customer_id = customer_id
        self.restaurant_id = restaurant_id
        self.dish_id = dish_id  # Optional, if rating a specific dish
        self.rating_value = rating_value  # 1-5 scale
        self.comment = comment
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.active = True
    
    def to_dict(self):
        return {
            "customer_id": self.customer_id,
            "restaurant_id": self.restaurant_id,
            "dish_id": self.dish_id,
            "rating_value": self.rating_value,
            "comment": self.comment,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "active": self.active
        }
    
    @classmethod
    def from_dict(cls, data):
        rating = cls(
            customer_id=data.get('customer_id'),
            restaurant_id=data.get('restaurant_id'),
            rating_value=data.get('rating_value'),
            comment=data.get('comment'),
            dish_id=data.get('dish_id'),
            id=data.get('_id')
        )
        rating.created_at = data.get('created_at', datetime.utcnow())
        rating.updated_at = data.get('updated_at', datetime.utcnow())
        rating.active = data.get('active', True)
        return rating