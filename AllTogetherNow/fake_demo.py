from time import sleep

class FakeDemo:
    def __init__(self, queue):
        self.queue = queue
        self.results = {"speed": 0, "volume": 0, "playing": False, 'track': 'c'}

    def run(self):
        while True:
            sleep(1)
            # print(f"FakeDemo {self.name} is running...")
            self.results["speed"] = 1 - self.results["speed"]
            self.results["volume"] = 1 - self.results["volume"]
            self.results["playing"] = not self.results["playing"]
            self.queue.put(self.results)
            # print(self.results)
