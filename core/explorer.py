import sys
from Registry import Registry #python-registry
import curses

def explore(system_path, software_path, sam_path, users_paths):
    current_key = ""
    first_displayed_key = 0
    first_displayed_value = 0
    keys = []
    key_values = []
    screen = 0

    if system_path:
        system_hive = Registry.Registry(system_path)
        system_name = system_hive.open("").name()
        keys.append("SYSTEM")
    else:
        system_hive = None
        system_name = ""

    if software_path:
        software_hive = Registry.Registry(software_path)
        software_name = software_hive.open("").name()
        keys.append("SOFTWARE")
    else:
        software_hive = None
        software_name = ""

    if sam_path:
        sam_hive = Registry.Registry(sam_path)
        sam_name = sam_hive.open("").name()
        keys.append("SAM")
    else:
        sam_hive = None
        sam_name = ""

    users_hives = []
    users_names = []
    if users_paths:
        for (user, user_path) in users_paths:
            user_hive =  Registry.Registry(user_path)
            users_names.append((user, user_hive.open("").name()))
            keys.append(user)
            users_hives.append((user, user_hive))

    if keys == []:
        print("you need to specify at least one registry hive")
        sys.exit(-1)

    stdscr = curses.initscr()
    curses.noecho()
    curses.curs_set(0) 
    stdscr.keypad(1)

    cursor_y = 6
    cursor_y_2 = 12
    base_screen(stdscr, cursor_y, cursor_y_2, screen)
    display_keys(stdscr, cursor_y, keys, current_key, first_displayed_key)
    display_infos(stdscr, cursor_y, first_displayed_key, first_displayed_value,
        keys, current_key, system_hive, software_hive, users_hives, system_name,
        software_name, sam_name, users_names)

    while 1:
        try:
            stdscr.clear()
            base_screen(stdscr, cursor_y, cursor_y_2, screen)
            display_keys(stdscr, cursor_y, keys, current_key, 
                first_displayed_key)
            key_values = display_infos(stdscr, cursor_y, first_displayed_key,
                first_displayed_value, keys, current_key, system_hive, 
                software_hive, users_hives, system_name, software_name,
                sam_name, users_names)
            key = stdscr.getch()
            max_y, max_x = stdscr.getmaxyx()

            if key == curses.KEY_UP and not screen:
                if cursor_y > 6:
                    cursor_y -= 1
                else:
                    first_displayed_key = max(first_displayed_key - 1, 0)

            elif key == curses.KEY_UP and screen:
                if first_displayed_value > 0 and cursor_y_2 == 13:
                    first_displayed_value -= 1
                    if first_displayed_value == 0:
                        cursor_y_2 -= 1
                elif cursor_y_2 > 12:
                    cursor_y_2 -= 1

            elif key == curses.KEY_DOWN and not screen:
                if cursor_y < max_y-3 and first_displayed_key + cursor_y - 5 < len(keys):
                    cursor_y += 1
                elif key == curses.KEY_DOWN and first_displayed_key + cursor_y - 5 < len(keys):
                    first_displayed_key += 1

            elif key == curses.KEY_DOWN and screen:
                if first_displayed_value + cursor_y_2 - 12 < len(key_values) and cursor_y_2 < max_y - 4:
                    cursor_y_2 += 1
                elif first_displayed_value + cursor_y_2 - 12 < len(key_values):
                    if first_displayed_value == 0:
                        first_displayed_value = 2
                    else:
                        first_displayed_value += 1

            elif key == curses.KEY_RIGHT and not screen:
                index = keys.index(keys[first_displayed_key + cursor_y - 6])
                if index == 0:
                    new_keys = [keys[0]]
                else:
                    new_keys = keys[0:index+1] 
                for subkey in get_key_from_name(system_hive, software_hive,
                    sam_hive, users_hives, keys[first_displayed_key + cursor_y - 6]).subkeys():
                    if keys[first_displayed_key + cursor_y - 6] + "\\" + subkey.name() not in keys:
                        new_keys += [keys[first_displayed_key + cursor_y - 6] + "\\" + subkey.name()]
                new_keys += keys[index+1:]
                if len(new_keys) != len(keys):
                    cursor_y += 1
                keys = new_keys

            elif key == curses.KEY_LEFT and not screen:
                index = keys.index(keys[first_displayed_key + cursor_y - 6])
                key_length = len(keys[index].split("\\"))
                new_keys = []
                cursor_y = 0
                for key in keys:
                    if len(key.split("\\")) >= key_length and key.split("\\")[0:key_length - 1] == keys[index].split("\\")[0:key_length - 1]:
                        if cursor_y == 0:
                            if keys.index(key) > first_displayed_key:
                                cursor_y = keys.index(key) + 5 - first_displayed_key
                            else:
                                cursor_y = 6
                                first_displayed_key = keys.index(key) - 1
                    else:
                        new_keys.append(key)
                keys = new_keys
                if len(keys) < max_y - 7:
                    cursor_y += first_displayed_key
                    first_displayed_key = 0

            elif key == ord(' '):
                screen = (screen + 1) % 2
                cursor_y_2 = 12
                first_displayed_value = 0

            elif key == curses.KEY_RESIZE:
                if cursor_y < 6:
                    cursor_y = 6
                if cursor_y >  max_y - 3:
                    first_displayed_key += cursor_y - max_y + 3
                    cursor_y = max_y - 3
                if len(keys) < max_y - 6:
                    cursor_y += first_displayed_key
                    first_displayed_key = 0
                elif len(keys) - first_displayed_key < max_y - 8:
                    cursor_y += max_y - 8 - len(keys) + first_displayed_key
                    first_displayed_key -= max_y - 8 - len(keys) + first_displayed_key

        except:
            curses.endwin()
            sys.exit(-1)


def display_keys(stdscr, cursor_y, keys, current_key, first_displayed_key):
    try:
        max_y, max_x = stdscr.getmaxyx()
        for i in range(6, max_y-2):
            if first_displayed_key + i - 6 < len(keys):
                level = len(keys[first_displayed_key + i - 6].split("\\"))
                stdscr.move(i, 3)
                stdscr.addnstr("  "*(level-1) + "| " +
                    keys[first_displayed_key + i - 6].split("\\")[-1], max_x/2 - 4)
        current_key = keys[first_displayed_key + cursor_y - 6]
    except:
        stdscr.clear()
        stdscr.move(0,0)
        stdscr.addstr("The window is too small to display content!")


def display_infos(stdscr, cursor_y, first_displayed_key, first_displayed_value,
    keys, current_key, system_hive, software_hive, users_hives, system_name,
    software_name, sam_name, users_names):
    try:
        max_y, max_x = stdscr.getmaxyx()
        
        current_key = "\\".join(keys[first_displayed_key +
            cursor_y - 6].split("\\")[1::])

        if keys[first_displayed_key + 
            cursor_y - 6].split("\\")[0] == "SYSTEM":
            key = system_hive.open(current_key)
        elif keys[first_displayed_key + 
            cursor_y - 6].split("\\")[0] == "SOFTWARE":
            key = software_hive.open(current_key)
        else:
            for (user_name, user_hive_name) in users_names:
                if keys[first_displayed_key + cursor_y - 6].split("\\")[0] == user_name:
                    index = users_names.index((user_name, user_hive_name))
                    key = users_hives[index][1].open(current_key)
                    break

        i = 7
        if max_y > 9:
            stdscr.move(i, max_x/2 + 3)
            #TODO: split at \
            name = replace_hive_name(system_name, software_name, sam_name,
                users_names, keys[first_displayed_key + cursor_y - 6])
            stdscr.addstr("Key name: " + name[0:max_x/2 - 13])
            name = name[max_x/2 - 13:]
            while len(name) > 0:
                i += 1
                stdscr.move(i, max_x/2 + 3)
                stdscr.addstr(name[0:max_x/2 - 3])
                name = name[max_x/2 - 3:]
        if max_y > 11:
            stdscr.move(i + 2, max_x/2 + 3)
            stdscr.addnstr("Key timestamp: " + format(key.timestamp(), 
                '%a, %d %B %Y %H:%M:%S %Z'), max_x/2 - 3)

        if max_y > 13:
            key_values = key.values()
            stdscr.move(i+4, max_x/2 + 3)
            stdscr.addstr("Key values:")
            if first_displayed_value > 0:
                stdscr.move(i+5, max_x/2 +3)
                stdscr.addstr("    [...]")
                begin_of_values = i+6
            else:
                begin_of_values = i+5
            if len(key_values) + begin_of_values - first_displayed_value < max_y - 2:
                end_of_values = begin_of_values + len(key_values) - first_displayed_value 
            else:
                stdscr.move(max_y - 3, max_x/2 + 3)
                stdscr.addstr("    [...]")
                end_of_values = max_y - 3
            for j in range(begin_of_values, end_of_values):
                stdscr.move(j, max_x/2 + 3)
                try:
                    stdscr.addstr("    " + 
                        str(key_values[j - begin_of_values +
                        first_displayed_value].name()) + ": " + 
                        str(key_values[j - begin_of_values +
                        first_displayed_value].value()))
                except:
                    stdscr.addstr("    Can't display value for " + 
                        str(key_values[j - begin_of_values +
                        first_displayed_value].name()))
        
        return key_values

    except:
        stdscr.clear()
        stdscr.move(0,0)
        stdscr.addstr("The window is too small to display content!")


def base_screen(stdscr, cursor_y, cursor_y_2, screen):
    try:
        stdscr.move(0, 0)
        max_y, max_x = stdscr.getmaxyx()
        stdscr.addstr(" " + "_"*(max_x-2))
        stdscr.move(1, 0)
        stdscr.addstr("/" + " "*(max_x-2) + "\\")
        stdscr.move(2, 0)
        stdscr.addnstr("|" + " "*(int)((max_x-16)/2) + 
            "RegViewer v0.1"[0:max_x-2] + " "*(int)((max_x-15)/2) + "|", max_x)
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

        if not screen:
            if cursor_y > 5:
                stdscr.move(cursor_y,0)
                stdscr.addstr("->")
                stdscr.refresh()
        else:
            if cursor_y_2 > 5:
                stdscr.move(cursor_y_2, max_x/2 + 1)
                stdscr.addstr("->")
                stdscr.refresh()

    except:
        stdscr.clear()
        stdscr.move(0,0)
        stdscr.addstr("The window is too small to display content!")


def replace_hive_name(system_name, software_name, sam_name, users_names, 
    key_name):
    if key_name.split("\\")[0] == system_name:
        key_name = key_name.replace(system_name, "SYSTEM")
    elif key_name.split("\\")[0] == software_name:
        key_name = key_name.replace(software_name, "SOFTWARE")
    elif key_name.split("\\")[0] == sam_name:
        key_name = key_name.replace(sam_name, "SAM")
    else:
        for user, user_name in users_names:
            if key_name.split("\\")[0] == user_name:
                key_name = key_name.replace(user_name, user)

    return key_name


def get_key_from_name(system_hive, software_hive, sam_hive, users_hives, name):
    if name == "SYSTEM":
        return system_hive.open("")
    elif name.split("\\")[0] == "SYSTEM":
        return system_hive.open(name.replace("SYSTEM\\", "", 1))
    elif name == "SOFTWARE":
        return software_hive.open("")
    elif name.split("\\")[0] == "SOFTWARE":
        return software_hive.open(name.replace("SOFTWARE\\", "", 1))
    for (user_name, user_hive) in users_hives:
        if name == user_name:
            return user_hive.open("")
        elif name.split("\\")[0] == user_name:
            return user_hive.open(name.replace(user_name + "\\", "", 1))
    return None
