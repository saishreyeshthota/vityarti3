"""
models.py
Defines the schema definitions, data models, and conversion helpers for the CampusBite
Canteen Management System.
"""

from datetime import datetime
import json


class User:
    """Represents an application user (Student, Faculty, Staff, or Admin)."""

    def __init__(self, id, username, email, full_name, role, wallet_balance=0.0, roll_no=None, created_at=None):
        self.id = id
        self.username = username
        self.email = email
        self.full_name = full_name
        self.role = role  # 'student', 'faculty', 'staff', 'admin'
        self.wallet_balance = float(wallet_balance or 0.0)
        self.roll_no = roll_no
        self.created_at = created_at or datetime.now().isoformat()

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "role": self.role,
            "wallet_balance": round(self.wallet_balance, 2),
            "roll_no": self.roll_no,
            "created_at": self.created_at,
        }


class MenuItem:
    """Represents a food or beverage item offered in the canteen."""

    def __init__(
        self,
        id,
        name,
        category,
        description,
        price,
        is_available=1,
        stock_quantity=50,
        dietary_type="veg",
        image_url="/static/images/burger.jpg",
        prep_time_minutes=10,
        calories=350,
        rating=4.8,
        created_at=None,
    ):
        self.id = id
        self.name = name
        self.category = category  # 'Breakfast', 'Lunch', 'Snacks', 'Beverages', 'Healthy'
        self.description = description
        self.price = float(price)
        self.is_available = bool(is_available)
        self.stock_quantity = int(stock_quantity)
        self.dietary_type = dietary_type  # 'veg', 'non-veg', 'vegan'
        self.image_url = image_url
        self.prep_time_minutes = int(prep_time_minutes)
        self.calories = int(calories)
        self.rating = float(rating)
        self.created_at = created_at or datetime.now().isoformat()

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "description": self.description,
            "price": round(self.price, 2),
            "is_available": self.is_available,
            "stock_quantity": self.stock_quantity,
            "dietary_type": self.dietary_type,
            "image_url": self.image_url,
            "prep_time_minutes": self.prep_time_minutes,
            "calories": self.calories,
            "rating": self.rating,
            "created_at": self.created_at,
        }


class Order:
    """Represents an order placed by a user."""

    STATUS_PENDING = "pending"
    STATUS_PREPARING = "preparing"
    STATUS_READY = "ready"
    STATUS_COMPLETED = "completed"
    STATUS_CANCELLED = "cancelled"

    def __init__(
        self,
        id,
        order_number,
        token_number,
        user_id,
        total_amount,
        discount_amount=0.0,
        final_amount=0.0,
        payment_method="wallet",
        payment_status="paid",
        order_status=STATUS_PENDING,
        special_instructions="",
        created_at=None,
        updated_at=None,
        items=None,
        user_name=None,
    ):
        self.id = id
        self.order_number = order_number
        self.token_number = token_number
        self.user_id = user_id
        self.total_amount = float(total_amount)
        self.discount_amount = float(discount_amount or 0.0)
        self.final_amount = float(final_amount or total_amount)
        self.payment_method = payment_method
        self.payment_status = payment_status
        self.order_status = order_status
        self.special_instructions = special_instructions or ""
        self.created_at = created_at or datetime.now().isoformat()
        self.updated_at = updated_at or datetime.now().isoformat()
        self.items = items or []
        self.user_name = user_name

    def to_dict(self):
        return {
            "id": self.id,
            "order_number": self.order_number,
            "token_number": self.token_number,
            "user_id": self.user_id,
            "user_name": self.user_name,
            "total_amount": round(self.total_amount, 2),
            "discount_amount": round(self.discount_amount, 2),
            "final_amount": round(self.final_amount, 2),
            "payment_method": self.payment_method,
            "payment_status": self.payment_status,
            "order_status": self.order_status,
            "special_instructions": self.special_instructions,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "items": self.items,
        }


class OrderItem:
    """Represents an individual line-item within an Order."""

    def __init__(self, id, order_id, item_id, item_name, quantity, unit_price, subtotal):
        self.id = id
        self.order_id = order_id
        self.item_id = item_id
        self.item_name = item_name
        self.quantity = int(quantity)
        self.unit_price = float(unit_price)
        self.subtotal = float(subtotal)

    def to_dict(self):
        return {
            "id": self.id,
            "order_id": self.order_id,
            "item_id": self.item_id,
            "item_name": self.item_name,
            "quantity": self.quantity,
            "unit_price": round(self.unit_price, 2),
            "subtotal": round(self.subtotal, 2),
        }
