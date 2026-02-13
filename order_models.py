from pydantic import BaseModel, Field
from decimal import Decimal
from uuid import UUID
from datetime import datetime
from typing import Optional


class UserName(BaseModel):
    username: str = Field(..., min_length=1, max_length=100)

class Price(BaseModel):
    price: Decimal = Field(..., max_digits = 15, decimal_places= 2)

class OrderID(BaseModel):
    id: UUID

class OrderIDStr(BaseModel):
    order_id: str

class Event(BaseModel):
    event: str


class OrderCreate(UserName, Price):
    pass

class OrderUpdateEvent(OrderID, Event):
    payment_id: Optional[UUID] = None

class OrderReturn(OrderID, UserName, Price):
    status: str = Field()
    placed_at: datetime = Field()
    updated_at: datetime = Field() 

class OrderUpdateMessage(OrderIDStr, UserName, Event):
    updated_at: datetime = Field() 