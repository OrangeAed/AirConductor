import asyncio
import aio_pika
import json
import time

class GestureDataPublisher:
    def __init__(self):
        self.gesture_data = {}


    async def send_gesture_data(self):
        connection = await aio_pika.connect_robust("amqp://guest:guest@localhost/")
        async with connection:
            channel = await connection.channel()

            await channel.declare_queue("gesture_queue", durable=True)

            while True:
                gesture_data = self.gesture_data
                message = aio_pika.Message(
                    body=json.dumps(gesture_data).encode(),
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT
                )
                await channel.default_exchange.publish(message, routing_key="gesture_queue")
                print("Sent:", gesture_data)
                await asyncio.sleep(1)

if __name__ == "__main__":
    gdp = GestureDataPublisher()
    gdp.gesture_data = {"timestamp": "whatever"}
    asyncio.run(gdp.send_gesture_data())
