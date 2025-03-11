from datetime import datetime

class Restaurant:
    def __init__(self, name, description, address, longitude, latitude, phone, 
                 email, website=None, cuisine_type=None, price_range=None, 
                 opening_hours=None, has_daily_menu=False, id=None):
        self.id = id
        self.name = name
        self.description = description
        self.address = address
        self.location = {
            "type": "Point",
            "coordinates": [longitude, latitude]
        }
        self.phone = phone
        self.email = email
        self.website = website
        self.cuisine_type = cuisine_type or []
        self.price_range = price_range  # 1-5 scale
        self.opening_hours = opening_hours or {}
        self.has_daily_menu = has_daily_menu
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.active = True
        self.verified = False
        self.avg_rating = 0
        self.rating_count = 0
    
    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "address": self.address,
            "location": self.location,
            "phone": self.phone,
            "email": self.email,
            "website": self.website,
            "cuisine_type": self.cuisine_type,
            "price_range": self.price_range,
            "opening_hours": self.opening_hours,
            "has_daily_menu": self.has_daily_menu,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "active": self.active,
            "verified": self.verified,
            "avg_rating": self.avg_rating,
            "rating_count": self.rating_count
        }
    
    @classmethod
    def from_dict(cls, data):
        restaurant = cls(
            name=data.get('name'),
            description=data.get('description'),
            address=data.get('address'),
            longitude=data.get('location', {}).get('coordinates', [0, 0])[0],
            latitude=data.get('location', {}).get('coordinates', [0, 0])[1],
            phone=data.get('phone'),
            email=data.get('email'),
            website=data.get('website'),
            cuisine_type=data.get('cuisine_type'),
            price_range=data.get('price_range'),
            opening_hours=data.get('opening_hours'),
            has_daily_menu=data.get('has_daily_menu', False),
            id=data.get('_id')
        )
        restaurant.created_at = data.get('created_at', datetime.utcnow())
        restaurant.updated_at = data.get('updated_at', datetime.utcnow())
        restaurant.active = data.get('active', True)
        restaurant.verified = data.get('verified', False)
        restaurant.avg_rating = data.get('avg_rating', 0)
        restaurant.rating_count = data.get('rating_count', 0)
        return restaurant