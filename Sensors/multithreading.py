from multiprocessing import Process
import os

def run(script):
    os.system(f"python3 {script}")

if __name__ == "__main__":
    processes = []
    for s in ["relay.py", "accl_and_temp.py","curr_location.py"]:
        p = Process(target=run, args=(s,))
        p.start()
        processes.append(p)
    for p in processes:
        p.join()

