#!/bin/env python3

import re
import subprocess
import time

def run(cmd):
    a = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    output = a.stdout.read().decode('utf-8')
    return output


# coordinate system
#  .-------> x
#  |
#  |
#  V
#  y


class CoordMixin:
    @property
    def top(self):
        return self.y

    @property
    def bottom(self):
        return self.y + self.h

    @property
    def left(self):
        return self.x

    @property
    def right(self):
        return self.x + self.w

    def contains(self, x, y):
        return self.left <= x <= self.right and self.bottom >= y >= self.top

    @property
    def center(self):
        return (self.x + self.w // 2, self.y + self.h // 2)


class Screen(CoordMixin):
    def __init__(self, name, w, h, x, y):
        self.name = name
        self.w = w
        self.h = h
        self.x = x
        self.y = y
        self.left_screen = None
        self.right_screen = None
        self.top_screen = None
        self.bottom_screen = None

    def __repr__(self):
        return f'{self.name} [{self.w}*{self.h} {self.x}x {self.y}y]'



class Screens:
    def __init__(self):
        self.screens = []
        for line in run("""xrandr --current | grep -P '[^\\s]+ connected'""").strip().split('\n'):
            match = re.findall('([^\\s]+) connected.*?(\\d+)x(\\d+)\\+(\\d+)\\+(\\d+)', line)
            if match:
                match = match[0]
                name, w, h, x, y = match
                self.screens.append(Screen(name, int(w), int(h), int(x), int(y)))

    def get_screen_for_pos(self, pos):
        x, y = pos
        for screen in self.screens:
            if screen.contains(x, y):
                return screen

    def get_right(self, screen):
        return min((other for other in self.screens), key=lambda other: abs(screen.right - other.left))

    def get_left(self, screen):
        return min((other for other in self.screens), key=lambda other: abs(screen.left - other.right))

    def get_top(self, screen):
        return min((other for other in self.screens), key=lambda other: abs(screen.top - other.bottom))

    def get_bottom(self, screen):
        return min((other for other in self.screens), key=lambda other: abs(screen.bottom - other.top))



class Windows:
    def __init__(self):
        self.windows = []
        for window_id in run("xdotool search --onlyvisible '\\w+'").strip().split('\n'):
            if window_id:
                self.windows.append(Window(window_id))

    def get_right(self, window):
        return min((other for other in self.windows), key=lambda other: abs(window.right - other.left))

    def get_left(self, window):
        return min((other for other in self.windows), key=lambda other: abs(window.left - other.right))

    def get_above(self, window):
        return min((other for other in self.windows), key=lambda other: abs(window.top - other.bottom))

    def get_below(self, window):
        return min((other for other in self.windows), key=lambda other: abs(window.bottom - other.top))


class Window(CoordMixin):
    def __init__(self, window_id):
        self.window_id = window_id
        self.x = None
        self.y = None
        self.w = None
        self.h = None
        self.name = None
        self.update_position()

    def __repr__(self):
        return f'{self.name} {self.window_id} [{self.w}*{self.h} {self.x}x {self.y}y]'

    @classmethod
    def get_active(cls):
        return Window(run('xdotool getactivewindow').split('\n')[0])

    def focus(self):
        run(f'xdotool windowraise {self.window_id}')

    def unmaximize_window(self):
        run(f'wmctrl -ir {self.window_id} -b remove,maximized_vert,maximized_horz')
        self.update_position()

    def get_maximized_state(self):
        window_horz_maxed=bool(run(f'''xprop -id {self.window_id} _NET_WM_STATE | grep '_NET_WM_STATE_MAXIMIZED_HORZ'''))
        window_vert_maxed=bool(run(f'''xprop -id {self.window_id} _NET_WM_STATE | grep '_NET_WM_STATE_MAXIMIZED_VERT'''))
        return (window_horz_maxed, window_vert_maxed)

    def update_position(self):
        wininfo = run(f'xwininfo -id {self.window_id}')
        self.x = int(re.search('Absolute upper-left X:\s+-?(\d+)', wininfo).group(1))
        self.y = int(re.search('Absolute upper-left Y:\s+-?(\d+)', wininfo).group(1))
        self.w = int(re.search('Width:\s+(\d+)', wininfo).group(1))
        self.h = int(re.search('Height:\s+(\d+)', wininfo).group(1))
        self.name = re.search('xwininfo: Window id: 0x[0-9a-f]+ (.+)', wininfo).group(1)

    def get_position(self):
        return (self.x, self.y)

    def move(self, pos):
        x, y = pos
        run(f'xdotool windowmove {self.window_id} {x} {y}')

    @property
    def center(self):
        return (self.x + self.w // 2, self.y + self.h // 2)


def add(pos1, pos2):
    return (pos1[0] + pos2[0], pos1[1] + pos2[1])

def sub(pos1, pos2):
    return (pos1[0] - pos2[0], pos1[1] - pos2[1])

import sys
if len(sys.argv) > 1:
    command = sys.argv[1]

    screens = Screens()
    window = Window.get_active()
    current_screen = screens.get_screen_for_pos(window.center)
    if command in ['--left', '--right', '--top', '--bottom']:
        if command == '--right':
            new_screen = screens.get_right(current_screen)
        elif command == '--left':
            new_screen = screens.get_left(current_screen)
        elif command == '--top':
            new_screen = screens.get_top(current_screen)
        elif command == '--bottom':
            new_screen = screens.get_bottom(current_screen)
        window.unmaximize_window()
        new_position = sub(new_screen.center, (window.w // 2, window.h // 2))
        window.move(new_position)
    elif command.startswith('--focus-'):
        wins = Windows()
        if command == '--focus-right':
            wins.get_right(window).focus()
        elif command == '--focus-left':
            wins.get_left(window).focus()
        elif command == '--focus-above':
            wins.get_above(window).focus()
        elif command == '--focus-right':
            wins.get_below(window).focus()


