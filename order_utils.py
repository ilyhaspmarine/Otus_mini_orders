from order_db_schema import Order as OrderSchema, OrderStatus
from order_models import OrderReturn, OrderCreate, OrderUpdateEvent, OrderUpdateMessage
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from order_config import settings
from kafka_producer import KafkaProd


producer = None


async def handle_startup():
    global producer 
    producer = KafkaProd()
    await producer.init_producer()


def handle_shutdown():
    global producer
    producer.close()


async def process_new_order(
    new_order: OrderCreate,
    db: AsyncSession
):
    now = datetime.utcnow()
    db_order = OrderSchema(
        id = uuid.uuid4(),
        username = new_order.username,
        price = new_order.price,
        status = OrderStatus.PENDING,
        placed_at = now,
        updated_at = now,
        payment_id = None
    )

    db.add(db_order)

    try:
        await db.commit()
    except IntegrityError:
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = 'Failed to create order')
    
    return build_return_from_order(db_order)


def build_return_from_order(
    db_order: OrderSchema
):
    return OrderReturn (
        id = db_order.id,
        username = db_order.username,
        status = db_order.status,
        price = db_order.price,
        placed_at = db_order.placed_at,
        updated_at = db_order.updated_at
    )


async def process_order_update_event(
    event: OrderUpdateEvent,
    db: AsyncSession
):
    if event.event == 'payment_confirmed':
        result = await process_payment_confirmed(event, db)
    elif event.event == 'payment_failed':
        result = await process_payment_failed(event, db)
    return result


async def process_payment_confirmed(
    event: OrderUpdateEvent,
    db: AsyncSession
):
    # Если заказ  найти не удастся - схлопочем исключение изнутри функции
    order = await get_order_by_id(event.id, db)

    # Заказ отменили - не надо обновлять его в оплаченный статус, надо откатывать оплату
    if order.status == OrderStatus.CANCELLED:
        raise HTTPException(
            status_code = status.HTTP_409_CONFLICT,
            detail = 'Order already cancelled'
        )
    # Не надо обновлять - уже все обновили ранее
    elif order.status != OrderStatus.PENDING:
        return order
    
    # А вот тут начинаем обновлять
    order.status = OrderStatus.PAID
    order.updated_at = datetime.utcnow()
    order.payment_id = event.payment_id

    try:
        await db.commit()
        await db.refresh(order)
    except IntegrityError:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = 'Failed to update order status'
        )
    
    await send_order_updated_message(order, event.event)

    return build_return_from_order(order)


async def send_order_updated_message(
    order: OrderSchema,
    event: str
):
    message = OrderUpdateMessage(
        order_id = str(order.id),
        username = order.username,
        event = event,
        updated_at = order.updated_at
    )

    global producer

    await producer.send_order_event(message)


async def get_order_by_id(
    id: uuid.UUID,
    db: AsyncSession
):
    result = await db.execute(select(OrderSchema).filter(OrderSchema.id == id))
    if result is None:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = 'Order not found'
        )
    return result.scalar_one_or_none()


async def process_payment_failed(
    event: OrderUpdateEvent,
    db: AsyncSession
):
    # Если заказ  найти не удастся - схлопочем исключение изнутри функции
    order = await get_order_by_id(event.id, db)

    # Заказ доставили - уже не надо ничего отменять
    if order.status == OrderStatus.DELIVERED:
        raise HTTPException(
            status_code = status.HTTP_409_CONFLICT,
            detail = 'Order already delivered'
        )
    elif order.status == OrderStatus.PAID:
        raise HTTPException(
            status_code = status.HTTP_409_CONFLICT,
            detail = 'Order paid before'
        )
    # Не надо обновлять - уже все обновили ранее
    elif order.status == OrderStatus.CANCELLED:
        return order
    
    # А вот тут начинаем обновлять
    order.status = OrderStatus.CANCELLED
    order.updated_at = datetime.utcnow()

    try:
        await db.commit()
        await db.refresh(order)
    except IntegrityError:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = 'Failed to update order status'
        )
    
    return build_return_from_order(order)


async def get_orders_by_uname(
    req_uname: str,
    db: AsyncSession
):
    result = await db.execute(select(OrderSchema).filter(OrderSchema.username == req_uname))
    orders = result.scalars().all()
    return orders