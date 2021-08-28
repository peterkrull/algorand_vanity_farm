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
import ctypes
from multiprocessing import Process, Queue, Value
from algosdk import account

# Generate accounts and looks for a vanity match
def find_address(queue,in_count,in_found,vanities,in_place):

    while True: # Thread loop
 
        # Wait for counter semaphore to clear
        # TODO Instead of waiting for the value to be available, each thread should have its own value.
        # This value, for each thread, would then be added afterwards by another thread.
        # It is not yet known how much of an effect this has on throughput.
        with in_count.get_lock():
            in_count.value += 1

        # generate an account using algosdk
        private, public = account.generate_account()
        for i in range(len(vanities)):

            # If vanity was found in beginning [B]
            if public.startswith(vanities[i].upper()) and in_place[0]:
                queue.put((public, private, vanities[i].upper(),"B"))
                with in_found.get_lock():
                    in_found.value += 1

            # If vanity was found in ending [E]
            if public.endswith(vanities[i].upper()) and in_place[1]:
                queue.put((public, private, vanities[i].upper(),"E"))
                with in_found.get_lock():
                    in_found.value += 1

            # If vanity was found anywhere [A]
            if public.find(vanities[i].upper()) != -1 and in_place[2]:
                queue.put((public, private, vanities[i].upper(),"A"))
                with in_found.get_lock():
                    in_found.value += 1

            # If configuration is invalid, exit.
            if not (in_place):
                print("Please enable 'vanity_first', 'vanity_last' or 'vanity_anywhere' in the config")
                exit()


# Saver process
def save_address(queue,saving):
    while True:
        while queue.qsize() > 0:
            saving.value = True
            public_key, private_key, vanity, location = queue.get()
            save_to_json(public_key, private_key, vanity, location)
        if queue.qsize() == 0:
            saving.value = False
            time.sleep(0.01)


# Save private/public key pair to JSON file        
def save_to_json(public_key, private_key, vanity, location):

    acc_count = 0
    #Try to open read from existing file
    try:
        file_data = json.load(open("vanity_addresses",'r'))
        try:
            # Update count if data for this vanity address exists
            acc_count = len(file_data[str(vanity)][str(location)])
        except KeyError as e:
            # No data exists, count remains 0
            pass

        # Generate data
        new_data = generate_new_data(public_key, private_key, vanity, location, acc_count)

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

    # If no file was found
    except FileNotFoundError as e:
        with open("vanity_addresses",'x') as file:
            new_data = generate_new_data(public_key, private_key, vanity, location, acc_count)
            json.dump(new_data,file)


# Generate new data to update existing file with
def generate_new_data(public_key, private_key, vanity, location, acc_count):
    return {
        str(vanity) : {
            str(location) : {
                str(acc_count) : {
                    "public key": public_key,
                    "private key" : private_key
                }
            }
        }
    }


def load_single_config(file_data,label,value):
    try:
        temp = file_data[label]
        return temp
    except KeyError:
        file_data.update({label : value})
        with open("vanity_config",'w') as file:
            json.dump(file_data,file)

# Load user configuration
def load_config():

    #Default config
    max_threads = 4
    vanities = ["TEST","EXAMPLE"]
    beginning = True
    ending = False
    anywhere = False

    print("Loading configuration file..")

    try:
        # Load configuration from file
        file_data = json.load(open("vanity_config",'r'))
        
        # Fetch vanity list
        vanities = load_single_config(file_data,"vanity",vanities)
        # Fetch threads configuration
        max_threads = load_single_config(file_data,"max_threads",max_threads)
        # Fetch first only configuration
        beginning = load_single_config(file_data,"vanity_first",beginning)
        # Fetch first only configuration
        ending = load_single_config(file_data,"vanity_last",ending)
        # Fetch first only configuration
        anywhere = load_single_config(file_data,"vanity_anywhere",anywhere)

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
            print("\nIt looks like this is your first time running Algorand Vanity Farmer.")
            print("Please place your wanted vanities in the 'vanity_config' file.")
            print("A recommended length is between 4 to 6 characters.\n")
            print("When you are done, execute this program again.\n")
            input()
            exit()


# Handler for user ctrl-c action
def signal_handler(sig, frame):
    global acount,found,running_time
    
    print("")
    terminate_processes()
    if found.value == 0:
        print("No match in " + str(count.value) + " attempts and " + get_running_time(running_time, start_time))
    else:
        print("Found " + str(found.value) + " matches in " + str(count.value) + " attempts and " + get_running_time(running_time, start_time))
        
        genrate = ""
        try:
            genrate = str(int(count.value/running_time.value))
        except ZeroDivisionError:
            generate = "Calculaing"

        print("Average address generation : "+genrate+" addr/s")
    exit()

# Calculate and format running time
def get_running_time(running_time, start_time):

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
def info_print(count,found,running_time,start_time):

    prev_count = 0
    array_count = []
    array_circ = 0
    array_sum = 0
    avg_over = 60 # seconds
    while True:

        # Average speed over avg_over seconds
        if len(array_count) < avg_over:
            if len(array_count) == 0:
                time.sleep(1)
            array_count.append(count.value-prev_count)
            array_sum = 0
            for i in range(len(array_count)):
                array_sum += array_count[i]
        else:
            if array_circ < avg_over:
                array_count[array_circ] = count.value-prev_count
                array_circ += 1

            elif array_circ == avg_over:
                array_circ = 0
                array_count[array_circ] = count.value-prev_count
            array_sum = 0
            for i in range(avg_over):
                array_sum += array_count[i]
        avg_speed = int(array_sum/len(array_count))
        
        print("\n\n\nStats for current session.")
        print("Timer : "+ get_running_time(running_time, start_time))
        print("Speed : "+str(avg_speed)+" a/s")

        if count.value < 1000000:
            print("Tried : "+str(count.value))
        else:
            print("Tried : "+str(int(count.value/100000)/10)+" M")

        if found.value > 1:
            print("Found : "+str(found.value)+" matches")
        elif found.value == 1:
            print("Found : "+str(found.value)+" match")
        else:
            print("Found : no matches")
            
        print("\nAverage time between match.")
        try:
            print("4 chars : %.1f"%((pow(32,4)/avg_speed))+" seconds")
            print("5 chars : %.1f"%((pow(32,5)/avg_speed)/60)+" minutes")
            print("6 chars : %.1f"%((pow(32,6)/avg_speed)/3600)+" hours")
            print("7 chars : %.1f"%((pow(32,7)/avg_speed)/86400)+" days")
            print("8 chars : %.1f"%((pow(32,8)/avg_speed)/604800)+" weeks")
        except ZeroDivisionError:
            print("Calculating speed..")

        prev_count = count.value
        time.sleep(1)
        

# Cleanup spawned processes
def terminate_processes():
    global saving
    for j in jobs:
        j.terminate()

    i.terminate()  

    # Wait for saving process to finish
    while saving.value:
        pass
    s.terminate()


# Get correct number threads
def get_num_threads(max_threads):
    if max_threads == 0 or multiprocessing.cpu_count() <= max_threads:
        return multiprocessing.cpu_count()
    elif max_threads < multiprocessing.cpu_count():
        return max_threads


if __name__ == '__main__':
    
    start_time = time.time()
    running_time = Value('i',0)

    count = Value('i',0)
    found = Value('i',0)

    saving = Value(ctypes.c_bool,False)
    saving.value = False

    vanities,max_threads,beginning,ending,anywhere = load_config()
    place = [beginning,ending,anywhere]

    num_threads = get_num_threads(max_threads)
    print("Running on " + str(num_threads) + " thread(s)")

    queue = Queue()
    jobs = []

    # spawn number of address search processes equal to the number of processors on the system
    for i in range(num_threads):
        p = Process(target=find_address, args=(queue,count,found,vanities,place))
        jobs.append(p)
        p.start()
    
    # Spawn saver process
    s = Process(target=save_address, args=(queue,saving))
    s.start()

    # Spawns process to print info
    i = Process(target=info_print,args=(count,found,running_time, start_time))
    i.start()

    # capture ctrl-c so we can report attempts and running time
    signal.signal(signal.SIGINT, signal_handler)