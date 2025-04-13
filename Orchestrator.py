import asyncio
import multiprocessing as mp
from time import sleep

from audio import make_and_run
from hand_tracking import run
from GUI import create_and_run_gui

def main():
    # Create a queue to communicate the filepath of the audio directory
    filepath_queue = mp.Queue()
    # Create a queue to communicate gesture data
    hand_queue = mp.Queue()

    return_dict = {}
    gui_process = mp.Process(target=create_and_run_gui, args=(filepath_queue,))
    gui_process.start()

    # Wait for the GUI process to finish
    while gui_process.is_alive():
        sleep(0.25)
    gui_process.join()

    # Get the output file path from the GUI process
    output_filepath = filepath_queue.get()

    demo_process = mp.Process(target=run, args=(hand_queue, ))
    demo_process.start()

    # Create and start the fake audio process
    audio_process = mp.Process(target=make_and_run, args=(output_filepath, hand_queue))
    audio_process.start()

    processes = [demo_process, audio_process]
    while True:
        # waits for one process to terminate, then terminates the other one
        for process in processes:
            if not process.is_alive():
                for p in processes:
                    if p.is_alive():
                        p.terminate()
                break
        else:
            sleep(0.25)
            continue
        break

    # Cleanup processes
    demo_process.join()
    audio_process.join()


if __name__ == '__main__':
    main()

