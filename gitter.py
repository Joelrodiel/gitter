import os
import sys
import subprocess

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def checkIfGit():
    if not os.path.exists("./.git"):
        print("Not a git repo dummy")
        sys.exit()

def exec(cmd):
    r = subprocess.check_output(cmd, shell=True)
    return r.decode("utf-8")

def parseStatus(s):
    lines = s.splitlines()
    branx = lines[0]
    branx = branx[10:]
    temp_files = lines[7:lines.index("Untracked files:") - 1]
    print(temp_files)
    files = []

    for x in temp_files:
        if x[0:1] == "\t":
            files.append(x)

    untra = lines[lines.index('  (use "git add <file>..." to include in what will be committed)')+2:len(lines)-1]
    print(untra)

    for i in range(len(untra)):
        untra[i] = "created:" + untra[i]

    files.extend(untra)
    print(files)

    return branx, files

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

def printFiles(b, f):
    print("\nCurrent branch:",bcolors.OKGREEN + b.upper() + bcolors.ENDC,"\n")

    for i in range(len(f)):
        str = stylizeFile(f[i])
        print(" ",i,"\t",str)

    print("\n")
    print("Select which files you want to commit:")

def setup():
    checkIfGit()
    status = exec("git status")
    b, f = parseStatus(status)
    printFiles(b, f)
    return b, f

def parseIntSet(nputstr=""):
    selection = set()
    invalid = set()
    tokens = [x.strip() for x in nputstr.split(',')]
    for i in tokens:
        if len(i) > 0:
            if i[:1] == "<":
                i = "0-%s"%(i[1:])
        try:
            selection.add(int(i))
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

def parseCmd(cmd):
    if cmd.find("?") > -1:
        return None
    elif cmd == 'q':
        print('Goodbye!\n')
        sys.exit()
    elif cmd == '':
        print(bcolors.FAIL + "Invalid entry: Empty", bcolors.ENDC);
        return None
    else:
        return parseIntSet(cmd)

def getCommits(f, fC):
    return (' '.join((f[i])[9:] for i in range(len(fC))))

def main():
    branch, commitFiles = setup()

    filesC = None
    cmd_c = ''

    while filesC == None:
        cmd_add = input("$ ")
        filesC = parseCmd(cmd_add)

    print(bcolors.OKGREEN + "Adding files:", ', '.join(str(x) for x in filesC), bcolors.ENDC)

    while cmd_c == '':
        cmd_c = input("Name of commit: ")

    cmd_b = input("Branch name (" + branch + "): ")
    if cmd_b != "":
        branch = cmd_b

    print(bcolors.OKGREEN + "Pushing to", branch, "branch", bcolors.ENDC);

    cmd_w = input("Push where? (origin): ")
    if cmd_w == "":
        cmd_w = "origin"

    commitList = getCommits(commitFiles, filesC)

    os.system("git add " + commitList)

main()
