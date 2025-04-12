import asyncio
import aio_pika
import json
import time

class GestureDataPublisher:
    def __init__(self, queue_name="gesture_queue"):
        self.gesture_data = {}
        self.queue_name = queue_name
        self.send_data = True

    def set_gesture_data(self, gesture_data):
        self.send_data = True
        self.gesture_data = gesture_data

    async def send_gesture_data(self):
        connection = await aio_pika.connect_robust("amqp://guest:guest@localhost/")
        async with connection:
            channel = await connection.channel()

            await channel.declare_queue(self.queue_name, durable=True)

            while True:
                if self.send_data:
                    self.send_data = False
                    gesture_data = self.gesture_data
                    message = aio_pika.Message(
                        body=json.dumps(gesture_data).encode(),
                        delivery_mode=aio_pika.DeliveryMode.PERSISTENT
                    )
                    await channel.default_exchange.publish(message, routing_key=self.queue_name)
                    print("Sent:", gesture_data)
                await asyncio.sleep(1)

if __name__ == "__main__":
    gdp = GestureDataPublisher()
    gdp.gesture_data = {"timestamp": "whatever"}
    asyncio.run(gdp.send_gesture_data())
