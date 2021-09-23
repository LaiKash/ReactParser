# ReactParser
This script is meant to help Android Reverse Engineers to analyse React Native bundle.

## Requisites

- Python3 correctly installed.
- [JS Beautifier](https://github.com/beautify-web/js-beautify) installed to work with Python.

## Usage

parseReact.py [-h] [-b] [-f [FILE]] [-g [BRIDGE]]

optional arguments:

  -h, --help            show this help message and exit
  -b, --beauty          DO NOT beautify the bundle. This is used when you already have the output from js-beautify.
  -f [FILE], --file [FILE]
                      File name of the bundle file. Default name: bundle.js                     
  -g [BRIDGE], --bridge [BRIDGE]
                        Specify the full bridge name (eg. for NativeModules.Contacts, insert only Contacts). Default: Contacts
                        
                       
## Features

In summary this are the steps that the script perform:

1. Given a bundle file, it will parse it to get the bridge ID of the given bridge name (default to Contacts to search for Spyware).
2. Get all the bridges names of the bundle file and write them into the file `all_bridges.txt`
3. All the functions with the previous ID in the function's import array will be written into separate files.
4. Give the index number in the function's import array of each function so that the reverser do not have to count it.
5. Parse each function to search for common words such as `getAll`. Feel free to edit it in the `keywords` variable.

## Disclaimer

Always analyse the bundle file and the functiona manually. This script is only a helper to try to speed up the process.

---

### TODO

This is a first version with rude regex and a lot of spaguety code. What it concerns me the most is that it may have problems handleling REALLY big bundle files (specially loading them into memory). 

1. Clean up the code.
2. Find better regex.
3. Multithreading and better file management for really big files
4. Whatever...
