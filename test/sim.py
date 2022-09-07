import sys
import os
import curses
import time

from subprocess import Popen, PIPE
from params import *


try:
    stdscr = curses.initscr()


    curses.noecho()
    curses.curs_set(False)
    stdscr.clear()
    stdscr.refresh()

    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)

    height, width = stdscr.getmaxyx()
    max_x = curses.COLS - 1
    max_y = curses.LINES - 1
    blank = ' '.join(' ' for x in range(max_x-1))
  
    columns_row = []
    columns_active = []
    for i in range(max_x+1):
        columns_row.append(-1)
        columns_active.append(0)
 
    auction_round = 0
    while(True):
        p = open(PIPE_PATH, 'r')
        start_y = int((height) - 3)

        title = "Auction Simulation"[:width-1]
        subtitle = "State " + str(auction_round)[:width-1]   
        start_x_title = int((width//2)-(len(title)//2)-len(title)%2)
        start_x_subtitle = int((width//2)-
            (len(subtitle)//2)-len(subtitle)%2)
        stdscr.attron(curses.color_pair(1))
        stdscr.attron(curses.A_BOLD)
        stdscr.addstr(start_y, start_x_title, title)
        stdscr.addstr(start_y + 1, start_x_subtitle, subtitle)
        
        stdscr.attron(curses.color_pair(2))
        # Get auction data from pipe
        '''
        sellers = p.readline()
        start_x_sellers = int((width//2)
                -(len(sellers)//2)
                -len(sellers)%2)
        stdscr.addstr(0, 0, sellers)
        '''
        start_y_state = 1
        for state in p.readlines():
            stdscr.addstr(start_y_state, 0, state)
            start_y_state += 1
        state = p.readline()
        stdscr.addstr(start_y_state, 0, state)
        #stdscr.addstr(start_y_state+1, 0, blank)
        #stdscr.addstr(start_y_state+2, 0, blank)
        #stdscr.addstr(start_y_state+2, 0, blank)
       
        time.sleep(ROW_DELAY)
        p.close()
        auction_round+=1
        stdscr.refresh()

except KeyboardInterrupt as err:
    curses.endwin()

# wrapper 
#curses.wrapper(draw_menu)
