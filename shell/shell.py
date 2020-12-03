#! /usr/bin/env python3

import sys, os, re

def main():
  
    while True:

        if 'PS1' in os.environ:
            os.write(1, (os.environ['PS1']).encode())
        else:
            os.write(1, ("$").encode())

        args = os.read(0, 1024)
        if len(args) == 0:
            break
        args = args.decode().split("\n")
        if not args: 
            continue
        for arg in args:
            shellCommands(arg.split())


def shellCommands(args):

    if len(args) == 0:
        return

    elif args[0].lower == "exit":
        sys.exit(0)

    elif args[0] == "cd":
        
        try: 
            os.chdir(args[1])
        
        except IndexError:
            os.write(2, ("Include Target Directory \n").encode())

        except FileNotFoundError:
            os.write(1, ("cd: %s: No such file or directory \n" % args[1]).encode())
            pass

    elif "|" in args:  
        pipe(args)

    else:
        rc = os.fork()
        wait = True

        if "&" in args: 
            args.remove("&")
            wait = False

        if rc < 0: 
            os.write(2, ("Failed to Fork, returning... %d\n" % rc).encode())
            sys.exit(1)

        elif rc == 0:
            executeCommand(args)
            sys.exit(0)

        else:
            if wait:
                childpid = os.wait()


def pipe(args):
    left = args[0:args.index("|")]
    right = args[args.index("|") + 1:]

    pr, pw = os.pipe()
    rc = os.fork()

    if rc < 0:
        os.write(2, ("Failed to Fork, returning... %d\n" % rc).encode())
        sys.exit(1)
     
    elif rc == 0: 
        os.close(1)
        os.dup(pw)
        os.set_inheritable(1, True)
        for fd in (pr, pw):
            os.close(fd)
        executeCommand(left)
        os.write(2, ("Could not exec %s\n" % left[0]).encode())
        sys.exit(1)
        
    else:
        os.close(0)
        os.dup(pr)
        os.set_inheritable(0, True)
        for fd in (pw, pr):
            os.close(fd)
        
    
        if "|" in right:
            pipe(right)
        
        executeCommand(right)
        os.write(2, ("Could not exec %s\n" % right[0]).encode())
        sys.exit(1)


def redirectInputOutput(args):
    
    
    if '>' in args: 
        os.close(1)
        os.open(args[args.index('>')+1], os.O_CREAT | os.O_WRONLY)
        os.set_inheritable(1,True)
        args.remove(args[args.index('>') + 1])
        args.remove('>')
        
    else: 
        os.close(0)
        os.open(args[args.index('<')+1], os.O_RDONLY);
        os.set_inheritable(0, True)
        args.remove(args[args.index('<') + 1])
        args.remove('<')
    
    for dir in re.split(":", os.environ['PATH']): 
        prog = "%s/%s" % (dir,args[0])
        try:
            os.execve(prog, args, os.environ) 
        except FileNotFoundError:
            pass

    os.write(2, ("%s: command not found\n" % args[0]).encode())
    sys.exit(0)
        
def executeCommand(args):
    if "/" in args[0]:
        program = args[0]
        try:
            os.execve(program, args, os.environ)
        except FileNotFoundError:  
            pass 
    elif ">" in args or "<" in args:
        redirectInputOutput(args)
    else:
        for dir in re.split(":", os.environ['PATH']): 
            program = "%s/%s" % (dir, args[0])
            try:
                os.execve(program, args, os.environ)
            except FileNotFoundError:
                pass
                
    os.write(2, ("%s: command not found\n" % args[0]).encode()) 
    sys.exit(0)

if __name__ == "__main__":
    main()
