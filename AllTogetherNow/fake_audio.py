
class FakeAudio:
    def __init__(self, queue):
        self.queue = queue

    def play(self):
        while True:
            if not self.queue.empty():
                message = self.queue.get()
                print(f"Playing audio with settings: {message}")