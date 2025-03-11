from datetime import datetime

class Menu:
    def __init__(self, restaurant_id, menu_type, date, pdf_url, dishes=None, 
                 price=None, menu_restrictions=None, id=None):
        self.id = id
        self.restaurant_id = restaurant_id
        self.menu_type = menu_type  # 'daily', 'regular'
        self.date = date  # Only relevant for daily menus
        self.pdf_url = pdf_url
        self.dishes = dishes or []  # List of dish ids
        self.price = price  # For fixed price menus
        self.menu_restrictions = menu_restrictions or []  # ['vegetarian', 'vegan', 'gluten-free', etc.]
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.active = True
    
    def to_dict(self):
        return {
            "restaurant_id": self.restaurant_id,
            "menu_type": self.menu_type,
            "date": self.date,
            "pdf_url": self.pdf_url,
            "dishes": self.dishes,
            "price": self.price,
            "menu_restrictions": self.menu_restrictions,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "active": self.active
        }
    
    @classmethod
    def from_dict(cls, data):
        menu = cls(
            restaurant_id=data.get('restaurant_id'),
            menu_type=data.get('menu_type'),
            date=data.get('date'),
            pdf_url=data.get('pdf_url'),
            dishes=data.get('dishes'),
            price=data.get('price'),
            menu_restrictions=data.get('menu_restrictions'),
            id=data.get('_id')
        )
        menu.created_at = data.get('created_at', datetime.utcnow())
        menu.updated_at = data.get('updated_at', datetime.utcnow())
        menu.active = data.get('active', True)
        return menu