import multiprocessing as mp

from AllTogetherNow.hand_tracking import make_and_run
# import multiprocessing

from fake_demo import FakeDemo
from hand_tracking import GestureRecognizer
from AllTogetherNow.demo import run
from fake_audio import FakeAudio

if __name__ == '__main__':
    # Create a queue for inter-process communication
    queue = mp.Queue()

    # Create and start the fake demo process
    # demo_process = mp.Process(target=FakeDemo(queue).run)
    # demo_process.start()
    # print("after")

    demo_process = mp.Process(target=run(queue))
    demo_process.start()

    # Create and start the fake audio process
    audio_process = mp.Process(target=FakeAudio(queue).play)
    audio_process.start()

    # Wait for both processes to finish
    demo_process.join()
    audio_process.join()