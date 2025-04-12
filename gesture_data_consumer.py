import datetime

import aio_pika
import asyncio
import json
from gesture_data_publisher import GestureDataPublisher
import threading

def on_message(message: aio_pika.IncomingMessage):
    gesture_data = json.loads(message.body.decode())
    print("Received", gesture_data["timestamp"])


async def main():
    connection = await aio_pika.connect_robust("amqp://guest:guest@localhost/")

    channel = await connection.channel()
    await channel.declare_queue("gesture_queue", durable=True)

    queue = await channel.declare_queue("gesture_queue", durable=True)
    await queue.consume(on_message)

    print("Awaiting messages, press 'CTRL+C' to exit")

    while True:
        await asyncio.sleep(0.5)

def run_loop(gdp):
    asyncio.run(gdp.send_gesture_data())

def set_message():
    while True:
        gdp.set_gesture_data({"timestamp": datetime.datetime.now()})

if __name__ == "__main__":
    gdp = GestureDataPublisher('gesture_queue')
    gdp.set_gesture_data({"timestamp": "whatever"})
    t1 = threading.Thread(target=run_loop(gdp))
    t2 = threading.Thread(target=set_message)
    t1.start()
    t2.start()
    t1.join()