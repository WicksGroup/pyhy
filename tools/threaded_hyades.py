"""Attempt to speed up Hyadses using multithreading. First attempt did not appear to cause any increase

This might make sense I think multithreading is sending a single core more work, not asking additional cores to
distribute the load
"""

from time import perf_counter
from threading import Thread
import os


def run_hyades(inf_name):
    """Simple function to run Hyades command"""
    command = f'hyades {inf_name}'
    print('Starting', command)
    os.system(command)


start_time = perf_counter()

# create and start 10 threads
inf_files = [f for f in os.listdir('./') if f.endswith('.inf')]
threads = []
for inf in inf_files:
    t = Thread(target=run_hyades, args=(inf,))
    threads.append(t)
    t.start()

# wait for the threads to complete
for t in threads:
    t.join()

end_time = perf_counter()

print(f'It took {end_time- start_time: 0.2f} second(s) to complete.')