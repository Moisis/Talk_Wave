import concurrent.futures
import os
import time
import matplotlib.pyplot as plt
import subprocess


class Test():

    def __init__(self):
        self.times = []
        self.num_executions = 4

    def run_peer_permenant(self, thread_num):
        command = f'start cmd /k python "C:\\Users\\moisi\\Desktop\\Semester 7\\CSE351 - Computer Networks\\Project\\Phase 3\\Talk-Wave\\Talk_Wave\\Client\\Peer_Main.py" |  cmd /k echo 1'
        os.system(command)

        print(f"peer_t.py execution time for thread {thread_num}: 1 seconds")

    def run_peer(self, i):
        start_time = time.time()
        os.system(f"python Peer_Main.py --message 'Thread {i + 1} is running'")
        end_time = time.time()
        execution_time = end_time - start_time
        self.times.append(execution_time)
        print(f"peer.py execution time for thread {i + 1}: {execution_time} seconds")



    # # Print the average execution time

    def start_test(self):


        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.run_peer, i) for i in range(self.num_executions)]

            # Wait for all threads to complete
            concurrent.futures.wait(futures)

        avg_execution_time = sum(self.times) / self.num_executions
        print(f"Average peer.py execution time: {avg_execution_time} seconds")
        plt.plot(self.times)
        plt.ylabel('Execution time (seconds)')
        plt.xlabel('Execution number')
        plt.show()


if __name__ == '__main__':
    x = Test()
    x.start_test()

