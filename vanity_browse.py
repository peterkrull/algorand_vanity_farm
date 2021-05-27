import json
import algosdk
from nacl.exceptions import InvalidkeyError

file_data = ""

def program():
    open_file()
    present_names()
    user_input = present_publics()
    present_privates(user_input)

def open_file():
    global file_data
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
        print("Found :",names[i],len(file_data[names[i]]),"times")

def present_publics():
    user_input = input().upper()
    names = []
    print("\nType the number in front of your wanted vanity go get mnemonic.")
    print("")
    if user_input not in file_data:
        print("The vanity '",user_input,"' was not an option. Exiting.",sep="")
        exit() 
    for vanity in file_data:
        names.append(vanity)
        if user_input == vanity:
            for i in range(len(file_data[vanity])):
                print(i,":",file_data[vanity][str(i)]["public key"])
    return user_input

def present_privates(vanity):
    user_input = input()
    try:
        print("\nThe private mnemonic will now be shown. Make sure noone is watching")
        print("Press any key to continue")
        user_input_2 = input()
        if user_input_2 != None:
            print(algosdk.mnemonic.from_private_key(file_data[vanity][str(user_input)]["private key"]),sep="")
            print("\nPress any key again to show private key")
            user_input_2 = input()
            if user_input_2 != None:
                print(file_data[vanity][str(user_input)]["private key"],"\n",sep="")
                print("REMEMBER! Keep these safe and private. Anyone with your key can spend your money.")
                print("It is advised to write the mnemonic on a piece of paper and hide it somewhere safe.")
                print("")
    except KeyError as e:
        print("That input {} was not an option. Exiting.".format(e))

program()