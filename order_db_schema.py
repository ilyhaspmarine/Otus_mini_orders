from sqlalchemy import Column, String, Numeric, DateTime, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
import uuid
from enum import Enum
from datetime import datetime


Base = declarative_base()


# Определяем перечисление для статуса заказа
class OrderStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    CANCELLED = "cancelled"
    DELIVERED = "delivered"


class Order(Base):
    __tablename__ = 'orders'

    # ID заказа
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)

    # Статус заказа
    status = Column(SQLEnum(OrderStatus), nullable=False, default=OrderStatus.PENDING)

    # Цена заказа
    price = Column(Numeric(precision=15, scale=2), nullable=False)

    # Дата-время заказа
    placed_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Дата-время заказа
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Имя пользователя, разместившего заказ
    username = Column(String(100), nullable=False)

    # ID оплаты (для связи с сервисом биллинга)
    payment_id = Column(UUID(as_uuid=True))