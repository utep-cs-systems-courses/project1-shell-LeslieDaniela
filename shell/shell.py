#!/usr/bin/env python3

import os, sys, re

def setPrompt():
    while True:
        defaultPrompt = os.getcwd() + "$"
        
        # PS1 variable
        if 'PS1' in os.environ:
            defaultPrompt = os.environ['PS1']

            try:
                # Writes bytestring 1 to file descriptor bytes 
                os.write(1, defaultPrompt.encode())
                # Reads n bytes from associated file descriptor
                data = os.read(0, 10000)

                if len(data) == 0:
                    break
                data  = data.decode().split("\n")

                for information in data:
                    executeCommand(information.split())
            # Error handling
            except EOFError:
                sys.exit(1)

# Shell Commands Method
def shellCommands(data):
    # Checks if Empty
    if len(data) == 0:
        return
    # Exit Command 
    if data[0].lower() == 'exit':
        sys.exit(0)
        
    # Directory Command
    if data[0].lower() == 'cd':

        # chdir for Navigating Directories
        try:
            os.chdir(data[1])
        except IndexError:
            os.write(2, ("Include Target Directory \n").encode())
        except FileNotFoundError:
            os.write(2, ("No such file or directory \n").encode())
        
    elif '|' in data:
        # Initialize fork
        forking = os.fork()
        
        # Child Process
        if forking == 0:
            simplePipes(data)
        elif forking < 0:
            os.write(2, ("Failed to Fork \n").encode())
            sys.exit(1)

        # Parent Process
        else:
            if data[-1] != "&":
                value = os.wait()
                if state[1] != 0 and state[1] != 256:
                    os.write(2, ("Program Terminated with exit code: %d\n" % state[1].encode()))

    else:
        # Initialize fork
        forking = os.fork()

        # Boolean for wait
        waitingProcess = True

        if "&" in data:
            waitingProcess = False
            data.remove("&")

        if forking == 0:
            redirectInputOutput(data)
        elif forking < 0 :
            os.write(2, ("Failed to Fork \n").encode())
            sys.exit(1)

        else:
            if waitingProcess:
                state = os.wait()
                if state[1] !=0 and state[1] !=256:
                     os.write(2, ("Program Terminated with exit code: %d\n" % state[1].encode()))

def simplePipes(data):
    # pipline for converters from one file to another
    readPipe, writePipe = os.pipe()
    read = data[data.index("|")+1]
    write = data[0:data.index("|")]

    # Parent Process
    if forking > 0:
        # Closes DATA file descriptor
        os.close(0)
        # Duplicates pipe reader to file descriptor 0
        os.dup2(readPipe, 0)

        for fileDescriptor in (readPipe, writePipe): 
           os.close(fileDescriptor)
        if "|" in read:
            pipe(read)

        # Calls method to run process
        redirectInputOutput(read)
        os.write(2, ("Not executable\n").encode())
        sys.exit(1)

    # Child Process
    elif forking == 0:
        # Closes OUTPUT file descriptor
        os.close(1)
        # Duplicates pipe writer to file descriptor 1
        os.dup2(writePipe, 1)

        for fileDescriptor in (readPipe, writePipe): 
            # Closes pipe read and write
            os.close(fileDescriptor)

        # Calls method to run process
        redirectInputOutput(write)
        os.write(2,("Not executable\n").encode())
        sys.exit(1)

    # Fork Fails
    else: 
        os.write(2,("Failed to Fork \n").encode())
        sys.exit(1)
 
def redirectInputOutput(data):
    try:
        # INPUT 
        if '<' in data: 
            os.close(0)
            # Open file to read
            os.open(data[data.index('<') +1], os.O_RDONLY)
            # Set inheritable flag of standard output file descriptor to 0 
            os.set_inheritable(0, True)
            # Removes file directory name
            data.remove(data[data.index('<')+1])
            # Removes <
            data.remove('<')

        # OUTPUT
        if '>' in data: 
            os.close(1)
            # Creates file to write
            os.open(data[data.index('>') +1], os.O_CREAT | os.O_WRONLY)
            # Set inheritable flag of standard output file descriptor to 1
            os.set_inheritable(1,True)
            # Removes file directory name
            data.remove(data[data.index('>')+1])
            # Removes >
            data.remove('>') 

    except IndexError:
        os.write(2, "Not able to redirect\n".encode())

    try:
        if data[0][0] == '/':
            # Child process uses execve to run command
            os.execve(data[0], data, os.environ) 
    except FileNotFoundError:
        pass
    except Exception:
        sys.exit(1)

    # Absolute path not specified uses environ $PATH
    for dir in re.split(":", os.environ['$PATH']): 
        targetDirectory  = "%s/%s" % (dir, data[0])
        try:
            # Attempts execution
            os.execve(targetDirectory, data, os.environ)
        except FileNotFoundError:
            pass
        except Exception:
            sys.exit(1)
            
    os.write(2, ("Command not found\n").encode())
    sys.exit(1)
    
setPrompt()
