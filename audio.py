import wave
import pyaudio
import numpy as np
import aio_pika
import asyncio
import json


class AudioPlayer:
    def __init__(self, path: str):
        self.file = wave.open(path, 'rb')
        self.pyaudio = pyaudio.PyAudio()
        self.audio_stream = self.pyaudio.open(format=pyaudio.paInt16, channels=1, rate=self.file.getframerate() * 2,
                                              output=True)

        self.playing = True
        self.volume = 1
        self.speed = (1, 1)

    async def chunk(self, data):
        data = self._transform_audio(data)
        self.audio_stream.write(data)
        return self.file.readframes(1024)

    def _transform_audio(self, data):
        arr = np.frombuffer(data, dtype=np.int16)
        arr = np.repeat(arr * self.volume, self.speed[1])[::self.speed[0]]
        return arr.astype(np.int16).tobytes()

    def play(self):
        self.playing = True

    def pause(self):
        self.playing = False

    def set_speed(self, numerator: int, denominator: int):
        self.speed = (numerator, denominator)

    def set_volume(self, value: float):
        self.volume = value

    def update(self, message: aio_pika.IncomingMessage):
        gesture_data = json.loads(message.body.decode())
        print("Received", gesture_data["gesture"])


async def main():
    connection = await aio_pika.connect_robust("amqp://guest:guest@localhost/")
    channel = await connection.channel()
    queue = await channel.declare_queue("gesture_queue", durable=True)

    player = AudioPlayer('Beethoven Symphony No. 9, Movement 2.wav')

    data = player.file.readframes(1024)
    while data:
        await queue.consume(player.update)
        data = await player.chunk(data)

    player.audio_stream.stop_stream()
    player.audio_stream.close()
    player.pyaudio.terminate()
    await connection.close()


if __name__ == '__main__':
    asyncio.run(main())
