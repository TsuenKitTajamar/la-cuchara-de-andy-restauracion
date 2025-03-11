from datetime import datetime

class Promotion:
    def __init__(self, restaurant_id, dish_id, start_date, end_date, level, 
                 daily_price, is_active=True, id=None):
        self.id = id
        self.restaurant_id = restaurant_id
        self.dish_id = dish_id
        self.start_date = start_date
        self.end_date = end_date
        self.level = level  # 1-5, promotional level
        self.daily_price = daily_price
        self.is_active = is_active
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def to_dict(self):
        return {
            "restaurant_id": self.restaurant_id,
            "dish_id": self.dish_id,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "level": self.level,
            "daily_price": self.daily_price,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data):
        promotion = cls(
            restaurant_id=data.get('restaurant_id'),
            dish_id=data.get('dish_id'),
            start_date=data.get('start_date'),
            end_date=data.get('end_date'),
            level=data.get('level'),
            daily_price=data.get('daily_price'),
            is_active=data.get('is_active', True),
            id=data.get('_id')
        )
        promotion.created_at = data.get('created_at', datetime.utcnow())
        promotion.updated_at = data.get('updated_at', datetime.utcnow())
        return promotion