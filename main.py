import time
import threading
import random
import subprocess
import os

"""
This program will mutate an input file and for each iteration will choose n places to write bytes to, and for each place choose n consecutive random bytes to be written.
If the program crashes, it exits.
"""

source = ""
dest = ""
program = ""
program_args = []
num_tests = 10000
num_threads = 25
places_to_write_min = 1
consecutive_bytes_to_write_min = 1
places_to_write_max = 1000
consecutive_bytes_to_write_max = 50
wait = 10
hide_window = True


def range_end(start, end):
    return range(start, end + 1)


def fuzz(n):
    startupinfo = subprocess.STARTUPINFO()
    if hide_window:
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    process_args = [program] + program_args + [dest.format(n)]
    process = subprocess.Popen(
        process_args, startupinfo=startupinfo
    )

    time.sleep(wait)
    poll = process.poll()
    if not poll:
        process.terminate()
    else:
        print("Crashed on", dest.format(n))
        os._exit(0)


source_bytes = open(source, "rb").read()

for i in range(num_tests):
    print(f"Running number #{i + 1} with {num_threads} threads.")
    threads = list()
    for j in range(num_threads):
        copy = bytearray(source_bytes)
        places_to_write = random.randint(
            places_to_write_min, places_to_write_max)
        bytes_written = 0
        for l in range(places_to_write):
            index = random.randint(0, len(copy))
            bytes_to_write = random.randint(
                consecutive_bytes_to_write_min, consecutive_bytes_to_write_max)
            if index + bytes_to_write >= len(copy):
                bytes_to_write = len(copy) - index
                print(
                    f"Truncated consecutive bytes written to {bytes_to_write}, parameters may be too high.")
            for k in range(bytes_to_write):
                copy[index + k] = random.randint(0, 255)
            bytes_written += bytes_to_write
        f = open(dest.format(j), "wb")
        f.write(copy)
        f.close()
        #print(f"Wrote a total of {bytes_to_write} bytes in {places_to_write} places to {dest.format(j)} ")
        t = threading.Thread(target=fuzz, args=(j,))
        t.daemon = True
        threads.append(t)
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    print(f"Tried a total of {(i + 1) * num_threads} inputs.")
