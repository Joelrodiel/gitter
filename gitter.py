import os
import sys
import signal
import subprocess


# Colors class!!
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


# Handle the Ctrl+C exiting
def signal_handler(sig, frame):
    print(bcolors.WARNING  + "\nExited gracefully", bcolors.ENDC)
    sys.exit(0)


# Checks if currently in Git repo
def checkIfGit():
    if not os.path.exists("./.git"):
        print("Not a git repo dummy")
        sys.exit()


# Main function for executing shell commands and returning the output
def exec(cmd):
    r = subprocess.check_output(cmd, shell=True)
    return r.decode("utf-8")


# Parse status
def parseStatus(s):
    lines = s.splitlines()
    branx = lines[0]
    branx = branx[10:]
    temp_files = lines[7:lines.index("Untracked files:") - 1]
    # print(temp_files)
    files = []

    for x in temp_files:
        if x[0:1] == "\t":
            files.append(x)

    untra = lines[lines.index('  (use "git add <file>..." to include in what will be committed)')+2:len(lines)-2]
    # print(untra)

    for i in range(len(untra)):
        untra[i] = "created:" + untra[i]

    files.extend(untra)
    # print(files)

    return branx, files


# Append the type of change in file
def stylizeFile(str):
    str = str.split()
    if str[0] == "modified:":
        str[0] = bcolors.FAIL + str[0] + bcolors.ENDC
    if str[0] == "created:":
        str[0] = bcolors.OKGREEN + str[0] + bcolors.ENDC
    if str[0] == "new":
        str[0] = bcolors.OKGREEN + str[0] + " " + str[1] + bcolors.ENDC
        str[1] = str[2]
    return str[0] + '\t' + str[1]


# Print files in a nicely formatted way u_u
def printFiles(b, f):
    print("\nCurrent branch:",bcolors.OKGREEN + b.upper() + bcolors.ENDC,"\n")

    for i in range(len(f)):
        str = stylizeFile(f[i])
        print(" ",i,"\t",str)

    print("\n")
    print("Select which files you want to commit:")


# Checks if in Git, executes 'git status', parses it, and returns it to main process
def setup():
    checkIfGit()
    status = exec("git status")
    b, f = parseStatus(status)
    printFiles(b, f)
    return b, f


# Parse numbers with patterns such as (1-3, >2, -3)
def parseIntSet(nputstr, maxList):
    selection = set()
    invalid = set()
    tokens = [x.strip() for x in nputstr.split(',')]
    
    noAdd = False
    for i in tokens:
        if len(i) > 0:
            if i == ".":
                i = "0-%s"%(maxList)
            if i[:1] == "<":
                i = "0-%s"%(i[1:])
            if i[:1] == "-":
                selection.remove(int(i[1:]))
                noAdd = True
        try:
            if (not noAdd):
                selection.add(int(i))
            else:
                noAdd = False
        except:
            try:
                token = [int(k.strip()) for k in i.split('-')]
                if len(token) > 1:
                    token.sort()
                    first = token[0]
                    last = token[len(token)-1]
                    for x in range(first, last+1):
                        selection.add(x)
            except:
                invalid.add(i)
    if len(invalid) > 0:
        print(bcolors.FAIL + "Invalid set: " + str(', '.join(invalid)),bcolors.ENDC)
        return None
    return selection


# Parse commands
def parseCmd(cmd, files):
    if cmd.find("chng") > -1:
        return None
    elif cmd == 'q':
        print(bcolors.OKGREEN + 'Goodbye!\n', bcolors.ENDC)
        sys.exit()
    elif cmd == '':
        print(bcolors.FAIL + "Invalid entry: Empty", bcolors.ENDC);
        return None
    else:
        return parseIntSet(cmd, len(files) - 1)


# Appends commit files in one line to feed to 'git add ...'
def getCommits(f, fC):
    return (' '.join((f[i])[9:] for i in fC))


def main():

    signal.signal(signal.SIGINT, signal_handler) # Handle the Ctrl+C exit

    branch, commitFiles = setup() # Make sure in Git project, return branch and files

    filesC = None
    cmd_c = ''

    while filesC == None:
        cmd_add = input("$ ")
        filesC = parseCmd(cmd_add, commitFiles)

        for x in filesC:
            if (int(x) + 1 > len(commitFiles)):
                filesC = None;
                print(bcolors.FAIL + "Invalid entry: Out of range", bcolors.ENDC)

    print(bcolors.OKGREEN + "Adding files:", ', '.join(str(x) for x in filesC), bcolors.ENDC)

    commitList = getCommits(commitFiles, filesC)

    print("git add " + commitList)

    committing = input("Want to commit? (y/n): ")

    if committing == '':
        committing = 'n'

    if (committing == 'n' or committing == "N"):
        print(bcolors.WARNING + "Make sure to commit your changes later!\n", bcolors.ENDC)
        sys.exit()

    while cmd_c == '':
        cmd_c = input("Name of commit: ")

    print(bcolors.OKGREEN + "Created new commit", cmd_c, bcolors.ENDC)
    
    print("git commit -m", cmd_c)

main()
