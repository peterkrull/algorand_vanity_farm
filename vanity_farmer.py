import algosdk
import time
import json
import threading

# Preloaded config
threads = 1 # Not implemented!
vanities = ["TEST","EXAMPLE"]
first_only = True

def make_vanity_wallet( printing = True):

    # Key variables
    private_key = ""
    public_key = ""

    # Counters and timers
    counter = 0
    previous = 0
    timer = 0

    # Address search
    current = time.time()
    begin = current

    global anyplace
    global beginning
    anyplace = False
    beginning = False
    delta_counter = 0
    delta_sum = 0
    
    while(1):

        found_first = [False]*len(vanities)
        found_any = [False]*len(vanities)
        while not ((anyplace and not first_only) or (beginning)):

            previous = current
            current = time.time()
            delta = current - previous
            delta_sum = delta_sum + delta
            delta_counter = delta_counter + 1
            counter = counter + 1

            if time.time() >= 1 + timer:
                timer = current
                seconds = (current-begin)
                hours = int(seconds/3600)
                minutes = int(seconds/60)
                hourmin = int(minutes-hours*60)
                minsec = int(seconds-minutes*60)

                if seconds < 60:
                    print("\n\nTime  : %.2f s"%seconds)
                elif seconds <= 3600:
                    print()
                    print("\n\nTime  : %d:%s m"%(minutes,str(minsec).zfill(2)))
                else:
                    print("\n\nTime  : %d:%s h"%(hours,str(hourmin).zfill(2)))
                try:
                    print("Speed : {} addr/s".format(int(1/(delta_sum/delta_counter))))
                    delta_counter = 0
                    delta_sum = 0
                    
                except ZeroDivisionError:
                    print("Speed : calculating..")

                if counter < 1000000:
                    print("Tried : {} k addr".format(int(counter/1000)))
                else:
                    print("Tried : %.2f M addr"%(float(int(counter/1000))/1000))
                load_config()
                update_finding()
                found_first = [False]*len(vanities)
                found_any = [False]*len(vanities)

            # Generate key
            private_key, public_key = algosdk.account.generate_account()
            
            # Find vanities
            for i in range(len(vanities)):
                # Look for vanity anywhere in public key
                if public_key.find(vanities[i].upper()) != -1 and not first_only:
                    anyplace = True
                    found_any[i] = True
                else:
                    found_any[i] = False

                # Look for vanity in beginning public key
                if public_key.find(vanities[i].upper()) == 0:
                    beginning = True
                    found_first[i] = True
                else:
                    found_first[i] = False

        beginning = False
        anyplace = False

        for i in range(len(vanities)):
            if found_first[i] or found_any[i]:
                save_to_json(private_key, public_key,vanities[i])

def update_finding():
    print("")
    try:
        file_data = json.load(open("vanity_addresses",'r'))
        for i in range(len(vanities)):
            try:
                print("Found",len(file_data[vanities[i]]),"of",vanities[i])
            except KeyError:
                print("Found 0 of",vanities[i])
    except FileNotFoundError as e:
        print("Nothing found so far")
        
def load_config():
    try:
        global vanities
        global threads
        global first_only

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
            threads = file_data["threads"]
        except KeyError:
            file_data.update({"threads":threads})
            with open("vanity_config",'w') as file:
                json.dump(file_data,file) 
        
        # Fetch first only configuration
        try:
            first_only = file_data["first only"]   
        except KeyError:
            file_data.update({"first only":first_only})
            with open("vanity_config",'w') as file:
                json.dump(file_data,file) 

    # Handle missing file
    except FileNotFoundError as e:
        with open("vanity_config",'x') as file:
            new_data = {
                "vanity" : vanities,
                "threads" : threads,
                "first only": first_only
                }
            json.dump(new_data,file)
            print("Please place your own vanities in the 'vanity_config' file.")
            exit()

def save_to_json(private_key, public_key, vanity):
    count = 0
    new_data = generate_new_data(vanity, count, public_key, private_key)
    try:
        file_data = json.load(open("vanity_addresses",'r'))
        try:
            count = len(file_data[str(vanity)])
        except KeyError as e:
            count = 0

        new_data = generate_new_data(vanity, count, public_key, private_key)

        try:
            file_data[str(vanity)].update(new_data[str(vanity)])
        except KeyError as e:
            file_data.update(new_data)
        
        with open("vanity_addresses",'w') as file:
            json.dump(file_data,file) 
            #print("File updated")
    except FileNotFoundError as e:
        with open("vanity_addresses",'x') as file:
            new_data = generate_new_data(vanity, count, public_key, private_key)
            json.dump(new_data,file)
            #print("File created")

def generate_new_data(vanity, count, public_key, private_key):
    return {
        str(vanity) : {
            str(count) : {
                "public key": public_key,
                "private key" : private_key
            }
        }
    }

def show_all(vanity):
    try:
        file_data = json.load(open("vanity_addresses",'r'))
        for i in range(len(file_data[vanity])):
            file_data[vanity][str(i)]["private key"]
    except FileNotFoundError as e:
        print("No address file exists")

# Program order
load_config()
make_vanity_wallet()
