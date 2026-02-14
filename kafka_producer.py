import os
from confluent_kafka import Producer
import json
import asyncio
from order_models import OrderUpdateMessage

class KafkaProd:
    def __init__(self):
        self.__bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
        self.__topic = os.getenv("KAFKA_ORDERS_TOPIC", "orders")
        self.__password = os.getenv("KAFKA_PASSWORD")
        self.__user = os.getenv("KAFKA_USER")

    
    async def init_connection(
        self
    ):
        try:
            print(f'Initializing connection to kafka: {self.__bootstrap_servers}')

            self.__producer = Producer({
                'bootstrap.servers': self.__bootstrap_servers,
                'security.protocol': 'SASL_PLAINTEXT',
                'sasl.mechanism': 'PLAIN',
                'sasl.username': self.__user,
                'sasl.password': self.__password,
                'message.timeout.ms': 10000,
                'api.version.request': True,
                'broker.version.fallback': '0.11.0'   
            })
            
            print('Sending test topic')
            
            # Флаг для отслеживания результата доставки
            delivery_result = {'success': False, 'error': None}
            
            # Callback для отчёта о доставке
            def delivery_report(err, msg):
                if err is not None:
                    delivery_result['error'] = err
                else:
                    delivery_result['success'] = True
            
            # Отправка сообщения
            self.__producer.produce(
                topic='test-connection-topic',
                value=json.dumps({'test': 'connection'}).encode('utf-8'),
                callback=delivery_report
            )
            
            # Ожидание доставки (опрос колбэков в цикле)
            print('waiting for delivery (up to 25 sec)')
            for _ in range(25):
                self.__producer.poll(0)  # обрабатываем колбэки
                if delivery_result['success'] or delivery_result['error']:
                    break
                await asyncio.sleep(1)
            
            # Проверка результата
            if delivery_result['error']:
                raise Exception(f"Delivery failed: {delivery_result['error']}")
            
            if not delivery_result['success']:
                raise Exception("Timeout waiting for message delivery")
            
            self.__producer.flush(timeout=5.0)
            print(f'✅ Connected to kafka: {self.__bootstrap_servers}')
            
        except Exception as e:
            print(f'Unexpected error: {type(e).__name__}: {e}')
            raise


    async def send_order_event(
        self,
        order_message: OrderUpdateMessage
    ):
        # Флаг для отслеживания результата
        result = {'success': False, 'error': None}
        
        def delivery_report(err, msg):
            if err:
                result['error'] = err
                print(f"Failed to deliver message to topic {msg.topic()}: {err}")
            else:
                result['success'] = True
                print(f"✅ Delivered order {order_message.order_id} to partition {msg.partition()}, offset {msg.offset()}")
        
        # Отправка сообщения
        try:
            self.__producer.produce(
                topic=self.__topic,
                value=order_message.model_dump_json().encode('utf-8'),
                key=order_message.order_id.encode('utf-8'),  # ключ для партиционирования по id
                callback=delivery_report
            )
            
            # Опрос колбэка (без блокировки основного потока)
            for _ in range(5):  # максимум 5 секунд ожидания
                self.__producer.poll(0)
                if result['success'] or result['error']:
                    break
                await asyncio.sleep(1)
            
            if result['error']:
                print(f"Kafka sending failed: {result['error']}")
            
            print(f'Successfulle sent {order_message.event} for order {order_message.order_id}')

            return result['success']
        
        except Exception as e:
            print(f"Error publishing order {order_message.order_id}: {e}")

    
    def close(self):
        self.__producer.close()