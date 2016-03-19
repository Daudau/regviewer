import sys
from Registry import Registry #python-registry
import curses

def explore(system_path, software_path, sam_path, users_paths):
    if system_path:
        system_hive = Registry.Registry(system_path)
    else:
        system_hive = None

    if software_path:
        software_hive = Registry.Registry(software_path)
    else:
        software_hive = None

    if sam_path:
        sam_hive = Registry.Registry(sam_path)
    else:
        sam_hive = None

    users_hives = []
    if users_paths:
        for (user, user_path) in users_path:
            users_hives.append((user, Registry.Registry(user_path)))

    stdscr = curses.initscr()
    curses.noecho()
    curses.curs_set(0) 
    stdscr.keypad(1)

    cursor_y = 6
    base_screen(stdscr, cursor_y)

    while 1:
        try:
            key = stdscr.getch()
            max_y, max_x = stdscr.getmaxyx()
            if key == curses.KEY_UP and cursor_y > 6:
                stdscr.clear()
                cursor_y -= 1
                base_screen(stdscr, cursor_y)
            elif key == curses.KEY_DOWN and cursor_y < max_y-3:
                stdscr.clear()
                cursor_y += 1
                base_screen(stdscr, cursor_y)
            elif key == curses.KEY_RIGHT:
                stdscr.clear()
                stdscr.addstr("Right")
            elif key == curses.KEY_LEFT:
                stdscr.clear()
                stdscr.addstr("Left")
            elif key == curses.KEY_RESIZE:
                stdscr.clear()
                if cursor_y < 6:
                    cursor_y = 6
                if cursor_y >  max_y - 3:
                    cursor_y = max_y - 3
                base_screen(stdscr, cursor_y)
        except:
            curses.endwin()
            sys.exit(0)


def base_screen(stdscr, cursor_y):
    try:
        stdscr.move(0, 0)
        max_y, max_x = stdscr.getmaxyx()
        stdscr.addstr(" " + "_"*(max_x-2))
        stdscr.move(1, 0)
        stdscr.addstr("/" + " "*(max_x-2) + "\\")
        stdscr.move(2, 0)
        stdscr.addstr("|" + " "*(int)((max_x-16)/2) + "RegViewer v0.1" +
            " "*(int)((max_x-15)/2) + "|")
        stdscr.move(3, 0)
        stdscr.addstr("\\" + " "*(max_x-2) + "/")
        stdscr.move(4, 0)
        stdscr.addstr(" " + "-"*(max_x - 2))
        stdscr.move(5, 0)
        stdscr.addstr("_"*max_x)
        for i in range(6, max_y-1):
            stdscr.move(i, (int)((max_x - 2)/2))
            stdscr.addstr("||")
        stdscr.move(max_y-2, 0)
        stdscr.addstr("-"*max_x)
        stdscr.move(cursor_y,0)
        stdscr.addstr("->")
    except:
        stdscr.clear()
        stdscr.move(0,0)
        stdscr.addstr("The window is too small to display content!")

