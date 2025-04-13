import multiprocessing as mp

from AllTogetherNow.fake_demo import FakeDemo
# from hand_tracking import GestureRecognizer
from audio import AudioPlayer, make_and_run
from AllTogetherNow.demo import run

if __name__ == '__main__':
    # Create a queue for inter-process communication
    queue = mp.Queue()

    # Create and start the fake demo process
    # demo_process = mp.Process(target=FakeDemo(queue).run)
    # demo_process.start()
    # print("after")
    demo_process = mp.Process(target=run, args=(queue,))
    demo_process.start()


    # demo_process = mp.Process(target=GestureRecognizer("Demo").run)
    # demo_process.run()

    # Create and start the fake audio process
    audio_process = mp.Process(target=make_and_run, args=('songs\\Rick Astley - Never Gonna Give You Up', queue))
    audio_process.start()

    # Wait for both processes to finish
    demo_process.join()
    audio_process.join()