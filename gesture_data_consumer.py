import aio_pika
import asyncio
import json


def on_message(message: aio_pika.IncomingMessage):
    gesture_data = json.loads(message.body.decode())
    print("Received", gesture_data["gesture"])


async def main():
    connection = await aio_pika.connect_robust("amqp://guest:guest@localhost/")

    channel = await connection.channel()
    await channel.declare_queue("gesture_queue", durable=True)

    queue = await channel.declare_queue("gesture_queue", durable=True)
    await queue.consume(on_message)

    print("Awaiting messages, press 'CTRL+C' to exit")

    while True:
        await asyncio.sleep(0.5)


if __name__ == "__main__":
    asyncio.run(main())