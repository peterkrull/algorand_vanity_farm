
# Updated version
For an updated and improved, ultra-fast version implemented in Rust see [algo-vanity-rs](https://github.com/peterkrull/algo-vanity-rs)

---

# Algorand Vanity address farming tool

This automated Algorand vanity address farming tool written in Python makes it easy to look for a single or multiple interesting vanity addresses to be used on the Algorand blockchain. The tools require that the Algorand SDK for Python is installed to generate the public/private key pair.

## Prerequisites
* `python3.x`
* `pip3`
* `py-algorand-sdk`

To run the farming tool simply open a terminal window in the folder where the tools are located and type:
```bash
python vanity_farmer.py
```
When running the tool for the first time a configuration file called *vanity_config* will be created. Inside *vanity_config* you will need to input your wanted vanity addresses after the *"vanity"* section where it initially just says *["TEST","EXAMPLE"]*. Replace TEST and EXAMPLE with any number of vanity addresses you wish, but keep the quotation marks and remember the comma between each entry. When the config is updated, running the file again will should give the folloing output:

![vanity_farm_terminal](images/vanity_farm_terminal.png?raw=true)

And when you wish to browse through the collected addresses you will want to run the *vanity_browse.py* file:
```bash
python vanity_browse.py
```
The browser will guide you through the process to make finding the right address easier.

## Speed of farming

The tools were tested on a Linux PC using an i5 3570k processor @ 4.2 GHz and could comb through *58 k (thousand) addresses/s using all 4 cores* when searching for a single vanity pattern. Searching for multiple patterns will slow down the process slightly. Because of this speed, it is not advised to look for addresses with a vanity pattern that is too short, since this can cause too frequent file saves, and thus corrupt can the file. Try to at least look for 4 character vanities.
