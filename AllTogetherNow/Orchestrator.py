import multiprocessing as mp

from fake_demo import FakeDemo
from fake_audio import FakeAudio

if __name__ == '__main__':
    # Create a queue for inter-process communication
    queue = mp.Queue()

    # Create and start the fake demo process
    demo_process = mp.Process(target=FakeDemo("Demo").run)
    demo_process.start()

    # Create and start the fake audio process
    audio_process = mp.Process(target=FakeAudio(queue).play)
    audio_process.start()

    # Wait for both processes to finish
    demo_process.join()
    audio_process.join()