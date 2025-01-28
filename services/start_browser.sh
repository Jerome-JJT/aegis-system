#!/bin/bash

export XDG_RUNTIME_DIR="/run/user/1000"

(sleep 30 && /home/admin/aegis-system/env/bin/python -c 'import keyboard; import time; keyboard.press_and_release("space"); time.sleep(2); keyboard.press_and_release("f11")') &

/usr/bin/midori /home/admin/index.html
