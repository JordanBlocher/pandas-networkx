import os
from subprocess import Popen, PIPE
import time
import curses
import time
from params import * 


if not os.path.exists(PIPE_PATH):
    os.mkfifo(PIPE_PATH)

#Popen(['gnome-terminal', '--', 'python3', '--', 'market_sim.py', 'tail -f %s' % PIPE_PATH])
Popen(['gnome-terminal', '-e', 'tail -f %s' %
    PIPE_PATH, 'python3', '--', 'market_sim.py'])
while(True):
    p = open(PIPE_PATH, "w")
    #print(p.readline())
    time.sleep(3)
    
 
