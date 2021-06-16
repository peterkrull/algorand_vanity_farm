# vanity_browser.py - lets you browse through the addresses found with vanity_farmer.py
#
# Depends on py-algorand-sdk which can be installed with:
#
# pip3 install py-algorand-sdk
#
# If you don't have pip3 you can install it with:
#
# apt install python3-pip

import json
import algosdk

def program():
    open_file()
    present_names()
    user_input = present_publics()
    present_privates(user_input)

def open_file():
    global file_data
    file_data = ""
    try:
        file_data = json.load(open("vanity_addresses",'r'))
    except FileNotFoundError as e:
        print("No 'vanity_addresses' file found, exiting.")
        exit()

def present_names():
    print("The following vanity addresses were generated.")
    print("Type the name of a vanity to view the addresses.")
    print("")
    names = []
    for vanity in file_data:
        names.append(vanity)
    for i in range(len(names)):
        length = []
        try:
            length.append(len(file_data[names[i]]["A"]))
        except KeyError:
            pass
        try:
            length.append(len(file_data[names[i]]["E"]))
        except KeyError:
            pass
        try:
            length.append(len(file_data[names[i]]["B"]))
        except KeyError:
            pass

        sum_is = 0
        for g in range(len(length)):
            sum_is += length[g]
        print("Found :",names[i],sum_is,"times")

def present_publics():
    user_input = input().upper()
    names = []
    print("")
    if user_input not in file_data:
        print("The vanity '",user_input,"' was not an option. Exiting.",sep="")
        exit() 
    for vanity in file_data:
        names.append(vanity)
        if user_input == vanity:
            try:
                temp = file_data[vanity]["A"]
                print("\nVanity addresses with '"+vanity+"' anywhere.")
                for i in range(len(temp)):
                    print("A"+str(i)+":",temp[str(i)]["public key"])
            except KeyError:
                pass

            try:
                temp = file_data[vanity]["E"]
                print("\nVanity addresses with '"+vanity+"' at the end.")
                for i in range(len(temp)):
                    print("E"+str(i)+":",temp[str(i)]["public key"])
            except KeyError:
                pass

            try:
                temp = file_data[vanity]["B"]
                print("\nVanity addresses with '"+vanity+"' at the beginning.")
                for i in range(len(temp)):
                    print("B"+str(i)+":",temp[str(i)]["public key"])
            except KeyError:
                pass
            
    return user_input

def present_privates(vanity):
    print("\nPlease type the letter and number in front your wanted address.")
    user_input = input()
    try:
        key = file_data[vanity][str(user_input[0]).upper()][str(user_input[1:])]["private key"]
        print("\nThe private mnemonic will now be shown. Make sure noone is watching")
        print("Press any key to continue")
        user_input_2 = input()
        if user_input_2 != None:
            print("--------------------------------------------------------------")
            print(algosdk.mnemonic.from_private_key(key))
            print("\n",key,sep="")
            print("--------------------------------------------------------------")
            print("\nREMEMBER! Keep these safe and private. Anyone with your keys can spend your money.")
            print("It is advised to write the mnemonic on a piece of paper and hide it somewhere safe.")
            print("")
    except KeyError as e:
        print("The input {} was not an option. Exiting.".format(e))
    except IndexError as e:
         print("No valid input was given. Exiting.")

program()