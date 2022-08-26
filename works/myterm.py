import os
from subprocess import Popen, PIPE, DEVNULL,io
import time
import curses
import random
import time
import sys

PIPE_PATH = '/home/frags/pipe'

#proc =  Popen([ 'gnome-terminal', '--', 'python3', '--', 'example.py', '--', 'tail -f %s' % PIPE_PATH])
proc =  Popen([ 'sh', '-c', 'tail -f %s | gnome-terminal -- python3 example.py' % PIPE_PATH ], stdout=PIPE,
    stdin=PIPE)


time.sleep(2)
while proc.returncode == None:
    with open(PIPE_PATH, 'w') as p:
        p.write('hello')
    p.close()
    print(proc.stdin, proc.stdout)
    stdin, stdout = proc.communicate()
    print(proc.args, proc.stdin, stdin)
    print(stdin)
    time.sleep(2)

