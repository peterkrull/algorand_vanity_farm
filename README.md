# Algorand Vanity address farming tool
This automated Algorand vanity address farming tool written in Python makes it easy to look for a single or multiple interesting vanity addresses to be used on the Algorand blockchain. The tools require that the Algorand SDK for Python is installed. Get the SDK with:

$ pip3 install py-algorand-sdk

To run the farming tool simply open a terminal window in the folder where the tools are located and type:

$ python vanity_farmer.py

When running the tool for the first time a configuration file called *vanity_config* will be created. Inside *vanity_config* you will need to input your wanted vanity addresses after the *"vanity"* section where it initially just says *["TEST","EXAMPLE"]*. Replace TEST and EXAMPLE with any number of vanity addresses you wish, but keep the quotation marks and remember the comma between each entry.

And when you wish to browse through the collected addresses you will want to run the *vanity_browse.py* file:

$ python vanity_browse.py

The browser will guide you through the process to make finding the right one easier.

# Speed of farming

The tools were tested on a Linux PC using an i5 3570k processor @ 4.2 GHz and could comb through *59.2 k (thousand) addresses/s using all 4 cores and 14.8 k addresses/s on each single core*. It is not advised to run multiple instances if the frequency of finding addresses is high, as all instances read and write to the same file, making room for error. This might be something i will look in to as well as native multi-threading support.
