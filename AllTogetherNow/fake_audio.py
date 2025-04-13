
class FakeAudio:
    def __init__(self, queue):
        self.queue = queue
        print("FakeAudio initialized")

    def play(self):
        old_empty = True
        while True:
            empty = self.queue.empty()
            if empty != old_empty:
                print(f"Queue empty: {empty}")
            old_empty = empty
            if not self.queue.empty():
                message = self.queue.get()
                with open('audio_log.txt', 'a') as log_file:
                    log_file.write(f"Received message: {message}\n")
