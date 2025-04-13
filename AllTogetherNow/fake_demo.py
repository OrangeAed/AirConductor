from time import sleep

class FakeDemo:
    def __init__(self, name):
        self.name = name
        self.results = {"speed": 0, "volume": 0, "playing": False}

    def run(self):
        while True:
            sleep(1)
            print(f"FakeDemo {self.name} is running...")
            self.results["speed"] = 1
            self.results["volume"] = 1
            self.results["playing"] = not self.results["playing"]
            print(self.results)
