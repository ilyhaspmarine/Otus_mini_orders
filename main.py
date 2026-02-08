from fastapi import Depends, FastAPI, HTTPException, status
from order_models import OrderCreate, OrderReturn, OrderUpdateEvent
from order_db import _get_db
import order_utils as utils
import uuid
from typing import List


app = FastAPI(title="Order Service", version="1.0.0")


@app.get('/health', summary='HealthCheck EndPoint', tags=['Health Check'])
def healthcheck():
    return {'status': 'OK'}


@app.post('/orders', summary = 'Create new order', tags = ['Orders'], response_model = OrderReturn, status_code = status.HTTP_201_CREATED)
async def order_create_new(
    new_order: OrderCreate,
    db = Depends(_get_db)
):
    result = await utils.process_new_order(new_order, db)
    return result


@app.put('/orders', summary = 'Update order status', tags = ['Orders'], response_model = OrderReturn, status_code = status.HTTP_200_OK)
async def order_update_status(
    event: OrderUpdateEvent,
    db = Depends(_get_db)
):
    result = await utils.process_order_update_event(event, db)
    return result


@app.get('/orders/id/{order_id}', summary = 'Get order by ID', tags = ['Orders'], response_model = OrderReturn, status_code = status.HTTP_200_OK)
async def order_get_by_id(
    order_id: uuid.UUID,
    db = Depends(_get_db)
):
    result = await utils.get_order_by_id(order_id, db)
    return utils.build_return_from_order(result)


@app.get('/orders/user/{uname}', summary = 'Get orders for User', tags = ['Orders'], response_model = List[OrderReturn], status_code = status.HTTP_200_OK)
async def orders_get_for_uname(
    uname: str,
    db = Depends(_get_db)
):
    # TO-DO: Нужная функция, но не нужна в рамках ДЗ
    pass