# move-window-to-screen
A small helper tool to move a focused window from one screen to another using standard X cli tools

## Requires the following command line tools to work

 - `xrandr`
 - `xdotool`
 - `wmctrl`
 - `xprop`
 
 oh, and it's `python 3.7 or higher` only as it requires the new f-string syntax.
 
## Usage

The program should be bound to shortcuts using your window manager, I use Ctrl-Super-W to move a window upwards, Ctrl-Super-S to move it downwards etc.

Moving the currently focused window to the next screen upwards

    move_window_to_screen.py --top
  
To test this in the command line without key-bindings you can just issue a sleep in the terminal and then switch to the window you want to move:

    sleep 4 && move_window_to_screen.py --bottom

Currenly you can use the following switches:

    --right
    --left
    --top
    --bottom
