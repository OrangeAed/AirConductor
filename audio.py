import wave
import pyaudio
import numpy as np


class AudioPlayer:
    def __init__(self):
        self.playing = True
        self.volume = 1
        self.speed = (1, 1)

    def stream(self, path: str):
        with wave.open(path, 'rb') as file:
            audio_stream = pyaudio.PyAudio().open(format=pyaudio.paInt16, channels=1, rate=file.getframerate() * 2, output=True)

            data = file.readframes(1024)
            while data:
                if self.playing:
                    data = self._update_audio(data)
                    audio_stream.write(data)
                    data = file.readframes(1024)

            audio_stream.stop_stream()
            audio_stream.close()

    def set_volume(self, value: float):
        self.volume = value

    def _update_audio(self, data):
        arr = np.frombuffer(data, dtype=np.int16)
        arr = np.repeat(arr * self.volume, self.speed[1])[::self.speed[0]]
        return arr.astype(np.int16).tobytes()

    def play(self):
        self.playing = True

    def pause(self):
        self.playing = False

    def change_speed(self, numerator : int, denominator : int):
        self.speed = (numerator, denominator)


if __name__ == '__main__':
    player = AudioPlayer()
    player.stream('Beethoven Symphony No. 9, Movement 2.wav')