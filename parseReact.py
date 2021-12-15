import jsbeautifier, re, os, sys
from argparse import ArgumentParser


parser = ArgumentParser()

parser.add_argument("-b", "--beauty", action="store_true",
                    help="DO NOT beautify the bundle. This is used when you already have the output from js-beautify. It requires the --file option.")
parser.add_argument("-f", "--file", default="bundle.js", nargs='?', action="store",
                     help="File name of the bundle file. Default name (if no --beauty option is used): bundle.js")
parser.add_argument("-g", "--bridge", default="NativeModules.Contacts", nargs='?', action='store',
                     help="Specify the full bridge name (eg. for NativeModules.Contacts, insert  NativeModules.Contacts). Default: NativeModules.Contacts")

args = parser.parse_args()
HEADER = '\033[95m'
OKCYAN = '\033[96m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'

# Keywords to search in the functions
keywords = ['http.get', 'http.post','upload', 'sendrequest', 'xmlhttprequest', '$.ajax', '$.post', 'fetch', '$http',
            '"post"', 'firebasestorage', 'firebaseio', 'send', 'contact', 'invite', 'getAll']
global signals
signals = False




# Get the bridge function
bridge_func_regex = re.compile(r'(?s)'+args.bridge+'((.*?)|(\n)+)},.\d+,')
# Get the bridge ID
bridge_id_regex = re.compile(r',.\d+,')
# Separate all functions into Match Objects
functions_sep_regex = re.compile(r'(?s)__d\(function\((\w+,\s)+\w+\)\s\{(.*?)\},\s\d+(.*?)\d\]\)\;')
# To parse the bridge names
bridge_names_regex = re.compile(r'NativeModules\.\w+')
# To count the bridge number used in the function
bridge_line_regex = re.compile(r'(?:\d+,.)+\d+')
# To parse bad parsed functions


def beautify(bundleName):
    try:
        print('[+] Beautifier on the move, please be patient...')
        file_exists=os.path.exists(bundleName)
        if not file_exists:
            sys.exit(1)
        res = jsbeautifier.beautify_file(bundleName)
        with open("bundle_beauty.js", "w") as f:
            f.write(res)
        print('[+] Beautiful bundle in "bundle_beauty.js"')
        bridge_func = bridge_func_regex.search(res)
        all_bridges_func(res)
    except SystemExit:
        print (FAIL+"ERROR! FILE NOT FOUND."+ENDC)
        sys.exit(1)
    except:
        pass #jsbeautifier gives some random errors sometimes due to imports
    else:
        return res

    

def openBundleBeauty(bundleName):
    print("[+] Opening file " + bundleName)
    flag = False
    try:
        with open(bundleName, 'r') as file:
            res = file.read()
        all_bridges_func(res)
        flag = True
    except:
        print (FAIL+"ERROR! FILE NOT FOUND."+ENDC)
        sys.exit(1) 
    else:
        return res


def all_bridges_func (res):
    print("[+] Writing all bridges names in: all_bridges.txt")
    filename = "all_bridges.txt"
    file_exists=os.path.exists(filename)
    if file_exists:
        os.remove(filename)
    all_bridges = bridge_names_regex.finditer(res)
    for bridges in all_bridges:
        with open(filename, "a") as file:
            file.write(bridges[0] + "\n")
    uniqlines = set(open(filename).readlines())
    open(filename, 'w').writelines(set(uniqlines))


def parse(res):
    print('[+] Searching for the bridge ID...')
    bridge_func = bridge_func_regex.search(res)
    try:
        bridge_id = bridge_id_regex.search(bridge_func[0])
    except:
        print (FAIL+"ERROR! BRIDGE NAME INCORRECT OR NOT FOUND."+ENDC)
        sys.exit(1)
    print('[+] Bridge ID found: '+OKGREEN+bridge_id[0].replace(',','')+ ENDC)
    print('[+] Finding functions with that bridge ID...')
    functions_sep = functions_sep_regex.finditer(res)
    
    count = 0
    numberOfFuncFound=len(re.findall(bridge_id[0], res))
    for functions in functions_sep:
        if bridge_id[0] in functions.group(0):
            func_name = 'function_'+str(count)+'.js'
            count = count + 1
            print('[+] Function found! Writing it in: '+ OKCYAN + func_name + ENDC)
            file_exists=os.path.exists(func_name)
            if file_exists:
                os.remove(func_name)
            with open(func_name, "w") as file:
                function_beauty = jsbeautifier.beautify(functions.group(0))
                file.write(function_beauty)
            id_count_helper (func_name, bridge_id)
            # Maybe call here the analyse_files
            if not signals:
                print('\t[-] No suspicious patterns found in this function.')

    if count!=numberOfFuncFound or count <= 1: # The bridge function is usually captured, and at least two functions should be captured (except if the bridge is not used)

        print(WARNING+'[!!] ATENTION: THE FUNCTIONS WERE  PROBABLY NOT PARSED PROPERLY, CHECK THE BUNDLE MANUALLY!! (known bug, catastrophic backtracking)'+ENDC)
    else:
        print('[+] DONE! ANALYSE ALL THE FUNCTIONS AND THE BUNDLE MANUALLY TOO!')

def id_count_helper(func_name, bridge_id):
    with open(func_name, "r") as file:
        for line in file:
            pass
    bridge_line = bridge_line_regex.search(line)
    try:
        list = bridge_line[0].split (",")
        print('\t[-] The index in the import array is: '+HEADER + str(list.index(bridge_id[0].replace(',','')))+ ENDC)
        analyse_files(func_name)
    except:
        print('\t[-] This is the bridge function. ')
        pass # The bridge function will fail
    

def analyse_files(file_name):
    global signals
    verdict = WARNING+'\t[!] ATENTION'+ENDC+': File ' + file_name + ' needs MORE analysis. Found: '+ENDC
    with open(file_name, "r") as file:
        for line in file:
                for keyword in keywords:
                    if keyword.lower() in line.lower() and keyword.lower() not in verdict:
                        verdict += WARNING+keyword + ' '+ENDC
                        signals = True
    if signals and not verdict.endswith(': '):
            print(verdict)


if args.beauty and (args.file is None or args.file == "bundle.js"):

    parser.error(FAIL+"ERROR: --beauty requires --file to specify the file."+ENDC)

if args.beauty:
    if (args.file is None or args.file == "bundle.js"):
        parser.error("--beauty requires --file to specify the file.")
    res=openBundleBeauty(args.file)
    parse(res)
else:
    res=beautify(args.file)
    parse(res)
