import wave
import pyaudio
import numpy as np
import aio_pika
import asyncio
import json
from numpy.lib.function_base import vectorize

SPEED = [(1, 2), (3, 4), (1, 1), (3, 2), (2, 1)]
VOLUME = [0, 0.25, 0.5, 0.75, 1]
TRACK_NUMBERS = {
    'ul': 0,
    'ur': 1,
    'll': 2,
    'lr': 3
}


class AudioPlayer:
    def __init__(self, path: str):
        ul = wave.open(path + '\\ul.wav', 'rb')
        ur = wave.open(path + '\\ur.wav', 'rb')
        ll = wave.open(path + '\\ll.wav', 'rb')
        lr = wave.open(path + '\\lr.wav', 'rb')

        self.tracks = np.stack([np.frombuffer(ul.readframes(ul.getnframes()), dtype=np.int16),
                                np.frombuffer(ur.readframes(ur.getnframes()), dtype=np.int16),
                                np.frombuffer(ll.readframes(ll.getnframes()), dtype=np.int16),
                                np.frombuffer(lr.readframes(lr.getnframes()), dtype=np.int16)]).T
        self.volumes = np.array([2, 2, 2, 2])

        self.pyaudio = pyaudio.PyAudio()
        self.audio_stream = self.pyaudio.open(format=pyaudio.paInt16, channels=1,
                                              rate=ul.getframerate() * 2,
                                              output=True)

        self.playing = True
        self.speed = 2

    async def play(self, data):
        data = self._transform_audio(data)
        self.audio_stream.write(data.tobytes())

    def get_volume(self):
        arr = []
        for volume in self.volumes:
            arr.append(VOLUME[volume])
        return np.array(arr)

    def _transform_audio(self, data):
        arr = data * self.get_volume()
        arr = np.repeat(arr, SPEED[self.speed][1]).reshape((-1, 4))
        arr = arr[::SPEED[self.speed][0]]
        return np.clip(np.sum(arr, axis=1), -32768, 32767).astype(np.int16)

    def update(self, message: aio_pika.IncomingMessage):
        data = json.loads(message.body.decode())
        if data['track'] == 'c':
            self.volumes = np.where((0 <= self.volumes + data['volume']) & (self.volumes + data['volume'] <= 4),
                                    self.volumes + data['volume'],
                                    self.volumes)
        else:
            track = TRACK_NUMBERS[data['track']]
            if 0 <= (self.volumes[track] + data['volume']) <= 4:
                self.volumes[track] += data['volume']
        if 0 <= (self.speed + data['speed']) <= 4:
            self.speed += data['speed']
        self.playing = data['playing']
        print(
            f'Track: {data["track"]}\tVolume: {self.get_volume()}\tSpeed: {SPEED[self.speed]}\tPlaying: {self.playing}')


async def main(path):
    connection = await aio_pika.connect_robust('amqp://guest:guest@localhost/')
    channel = await connection.channel()
    await channel.queue_delete('gesture_queue')
    queue = await channel.declare_queue('gesture_queue', durable=True)

    player = AudioPlayer(path)

    data = player.tracks[:2048]
    counter = 0
    while data is not None:
        await queue.consume(player.update)
        if player.playing:
            await player.play(data)
            counter += 1
            data = player.tracks[counter * 2048:(counter + 1) * 2048]

    player.audio_stream.stop_stream()
    player.audio_stream.close()
    player.pyaudio.terminate()
    await connection.close()


if __name__ == '__main__':
    asyncio.run(main('songs\\Rick Astley - Never Gonna Give You Up'))
