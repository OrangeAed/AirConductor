import asyncio
import aio_pika
import json
import time
from threading import Thread

class DataPublisher:
    def __init__(self, queue_name="data_queue"):
        self.gesture_data = {}
        self.file_location = ""
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

    async def send_string_data(self):
        connection = await aio_pika.connect_robust("amqp://guest:guest@localhost/")
        async with connection:
            channel = await connection.channel()

            await channel.declare_queue(self.queue_name, durable=True)

            while True:
                if self.send_data:
                    self.send_data = False
                    file_location = self.file_location
                    message = aio_pika.Message(
                        body=file_location.encode(),
                        delivery_mode=aio_pika.DeliveryMode.PERSISTENT
                    )
                    await channel.default_exchange.publish(message, routing_key=self.queue_name)
                    print("Sent:", file_location)
                await asyncio.sleep(1)

async def main():
    gdp = DataPublisher()
    gdp.gesture_data = {"timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "gesture": "swipe_right"}
    ldp  = DataPublisher()
    ldp.file_location = "C:\\Users\\sadit\PycharmProjects"

    await asyncio.gather(gdp.send_gesture_data(), ldp.send_string_data())

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    finally:
        loop.close()