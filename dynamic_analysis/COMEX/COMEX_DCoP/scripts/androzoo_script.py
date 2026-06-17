from multiprocessing import Process
import os
import time
import pandas as pd
import sys

sys.exit("ADD YOUR API KEY AND REMOVE EXIT()")
apikey = "<YOUR API KEY HERE>"

def download_from_hash(thread_num, hash_list, num_hashes):

        print("Process number " + str(thread_num) + " executing.")
        my_list = [hash_list[my_hash] for my_hash in range((num_hashes//40)*thread_num, (num_hashes//40)*(thread_num+1) if thread_num!=39 else num_hashes)]

        for my_hash in my_list:

                print("Downloading hash " + my_hash)
                os.system(f"curl -O --remote-header-name -G -d apikey={apikey} -d sha256={my_hash} https://androzoo.uni.lu/api/download")

                time.sleep(5)


if __name__ == "__main__":

        with open(f"{os.getenv('HOME')}/Desktop/missing_androzoo.txt", 'r') as fd1:
                benigns = [line.strip() for line in fd1]

        num_hashes = len(benigns)

        for i in range(40):
                myprocesses.append(Process(target=download_from_hash, args=(i, benigns, num_hashes)))
                myprocesses[i].daemon=True
                myprocesses[i].start()

        for i in range(40):
                myprocesses[i].join()

        print('\n\n----------------------------Execution over--------------------------\n')

