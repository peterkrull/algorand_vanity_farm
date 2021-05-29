# vanity_farmer.py - generate many vanity address for Algorand
#
# Depends on py-algorand-sdk which can be installed with:
#
# pip3 install py-algorand-sdk
#
# If you don't have pip3 you can install it with:
#
# apt install python3-pip
#
# This project expands on the work done by PureStage, which can be found with:
# https://github.com/PureStake/api-examples/blob/master/python-examples/algo_vanity.py

import time
import signal
import json
import multiprocessing
from multiprocessing import Process, Queue, Value
from algosdk import account

# Generate accounts and looks for a vanity match
def find_address(queue, counter, found):

    while True:
        with counter.get_lock():
            counter.value += 1

        # generate an account using algosdk
        private, public = account.generate_account()

        for i in range(len(vanities)):
            # If vanity was found in beginning [B]
            if public.startswith(vanities[i].upper()) and beginning:
                queue.put((public, private, vanities[i].upper(),"B"))
                with found.get_lock():
                    found.value += 1


            # If vanity was found in ending [E]
            if public.endswith(vanities[i].upper()) and ending:
                queue.put((public, private, vanities[i].upper(),"E"))
                with found.get_lock():
                    found.value += 1


            # If vanity was found anywhere [A]
            if public.find(vanities[i].upper()) != -1 and anywhere:
                queue.put((public, private, vanities[i].upper(),"A"))
                with found.get_lock():
                    found.value += 1

            if not (beginning, ending, anywhere):
                print("Please enable 'vanity_first', 'vanity_last' or 'vanity_anywhere' in the config")
                exit()


# Saver process
def save_address(queue):
    global saving
    while True:
        while queue.qsize() > 0:
            saving = True
            public_key, private_key, vanity, location = queue.get()
            save_to_json(public_key, private_key, vanity, location)
        if queue.qsize() == 0:
            saving = False
            time.sleep(0.01)
        

# Save private/public key pair to JSON file        
def save_to_json(public_key, private_key, vanity, location):

    count = 0
    #Try to open read from existing file
    try:
        file_data = json.load(open("vanity_addresses",'r'))
        try:
            # Update count if data for this vanity address exists
            count = len(file_data[str(vanity)][str(location)])
        except KeyError as e:
            # No data exists, count remains 0
            pass

        # Generate data
        new_data = generate_new_data(public_key, private_key, vanity, location, count)

        try:
            file_data[str(vanity)][str(location)].update(new_data[str(vanity)][str(location)])
        except KeyError:
            try:
                file_data[str(vanity)].update(new_data[str(vanity)])
            except KeyError as e:
                file_data.update(new_data)
        
        # Write to file
        with open("vanity_addresses",'w') as file:
            json.dump(file_data,file) 
            #print("File updated")

    # If no file was found
    except FileNotFoundError as e:
        with open("vanity_addresses",'x') as file:
            new_data = generate_new_data(public_key, private_key, vanity, location, count)
            json.dump(new_data,file)


# Generate new data to update existing file with
def generate_new_data(public_key, private_key, vanity, location, count):
    return {
        str(vanity) : {
            str(location) : {
                str(count) : {
                    "public key": public_key,
                    "private key" : private_key
                }
            }
        }
    }


# Load user configuration
def load_config():
    #print("Loading configuration")

    global vanities
    global max_threads
    global beginning
    global ending
    global anywhere

    try:

        # Load configuration from file
        file_data = json.load(open("vanity_config",'r'))
        
        # Fetch vanity list
        try:
            vanities = file_data["vanity"]
        except KeyError:
            file_data.update({"vanity" : vanities})
            with open("vanity_config",'w') as file:
                json.dump(file_data,file)
        
        # Fetch threads configuration
        try:
            max_threads = file_data["max_threads"]
        except KeyError:
            file_data.update({"max_threads":max_threads})
            with open("vanity_config",'w') as file:
                json.dump(file_data,file) 
        
        # Fetch first only configuration
        try:
            beginning = file_data["vanity_first"]   
        except KeyError:
            file_data.update({"vanity_first":beginning})
            with open("vanity_config",'w') as file:
                json.dump(file_data,file) 

        # Fetch first only configuration
        try:
            ending = file_data["vanity_last"]   
        except KeyError:
            file_data.update({"vanity_last":ending})
            with open("vanity_config",'w') as file:
                json.dump(file_data,file) 

        # Fetch first only configuration
        try:
            anywhere = file_data["vanity_anywhere"]   
        except KeyError:
            file_data.update({"vanity_anywhere":anywhere})
            with open("vanity_config",'w') as file:
                json.dump(file_data,file) 

        return vanities,max_threads,beginning,ending,anywhere
    # Handle missing file
    except FileNotFoundError as e:
        with open("vanity_config",'x') as file:
            new_data = {
                "vanity" : vanities,
                "max_threads" : max_threads,
                "vanity_first" : beginning,
                "vanity_last" : ending,
                "vanity_anywhere" : anywhere
                }
            json.dump(new_data,file)
            print("\nIt looks like this is your first running Algorand Vanity Farmer.")
            print("Please place your wanted vanities in the 'vanity_config' file.")
            print("A recommended length is between 4 to 6 characters.\n")
            print("When you are done, execute this program again.\n")
            exit()


# Handler for user ctrl-c action
def signal_handler(sig, frame):
    print("")
    terminate_processes()
    if found.value == 0:
        print("No match in " + str(count.value) + " attempts and " + get_running_time())
    else:
        print("Found " + str(found.value) + " matches in " + str(count.value) + " attempts and " + get_running_time())
        print("Average address generation : "+str(int(count.value/running_time))+" addr/s")
    exit()


# Calculate and format running time
def get_running_time():
    global running_time
    running_time = time.time() - start_time
    # float formatted to string with 2 decimal places
    if running_time < 60:
        running_time_str = time.strftime("%S",time.gmtime(running_time)) + " seconds"
    elif running_time < 3600:
        running_time_str = time.strftime("%M:%S",time.gmtime(running_time)) + " minutes"
    else:
        running_time_str = time.strftime("%H:%M:%S",time.gmtime(running_time)) + " hours"
    return running_time_str


# Print information
def info_print():
    while True:
        print("\n\nTimer : "+ get_running_time())
        print("Speed : "+str(int(count.value/running_time))+" a/s")
        if count.value < 1000000:
            print("Tried : "+str(count.value))
        else:
            print("Tried : "+str(int(count.value/100000)/10)+" M")
        print("Found : "+str(found.value))
        load_config()
        time.sleep(1)
        

# Cleanup spawned processes
def terminate_processes():
    global saving
    for j in jobs:
        j.terminate()
        i.terminate()

    # Wait for saving process to finish
    if not saving:
        s.terminate()


# Get correct number threads
def get_num_threads(max_threads):
    if max_threads == 0 or multiprocessing.cpu_count() <= max_threads:
        return multiprocessing.cpu_count()
    elif max_threads < multiprocessing.cpu_count():
        return max_threads


if __name__ == '__main__':

    #Default config
    max_threads = 4
    vanities = ["TEST","EXAMPLE"]
    beginning = True
    ending = False
    anywhere = False

    vanities,max_threads,beginning,ending,anywhere = load_config()

    num_threads = get_num_threads(max_threads)
    print("Running on " + str(num_threads) + " thread(s)")

    start_time = time.time()
    count = Value('i', 0)
    found = Value('i', 0)
    queue = Queue()
    jobs = []
    saving = False

    # spawn number of address search processes equal to the number of processors on the system
    for i in range(num_threads):
        p = Process(target=find_address, args=(queue, count, found))
        jobs.append(p)
        p.start()
    
    # Spawn saver process
    s = Process(target=save_address, args=(queue,))
    s.start()

    # Spawns process to print info
    i = Process(target=info_print)
    i.start()

    # capture ctrl-c so we can report attempts and running time
    signal.signal(signal.SIGINT, signal_handler)