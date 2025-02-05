#!/bin/bash

export XDG_RUNTIME_DIR="/run/user/1000"

/usr/bin/sleep 180

echo "GIRST"
echo $(/usr/bin/whoami)
echo "SEC"

(/usr/bin/sleep 200 && /usr/bin/sudo /home/admin/aegis-system/env/bin/python -c 'import os; import keyboard; import time; print(os.environ); keyboard.press_and_release("space"); time.sleep(2); keyboard.press_and_release("f11")' && echo 'KEYBOARD DONE' && >&2 echo "KEYBOARD PLOP") &
#/usr/bin/sudo /home/admin/aegis-system/env/bin/python -c 'import keyboard; import time; keyboard.press_and_release("space"); time.sleep(2); keyboard.press_and_release("f11")' &

#/usr/bin/midori /home/admin/index.html
/usr/bin/midori http://localhost:8000
