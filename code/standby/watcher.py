
import os
import time
import rich
import atexit

try:
    import RPi.GPIO as GPIO
except ImportError:
    from mockGPIO import GPIO
    
from dotenv import load_dotenv

load_dotenv()


# class ControllerManager:

#     STB = int(os.getenv('CONTROL_STB'))
#     CLK = int(os.getenv('CONTROL_CLK'))
#     DIO = int(os.getenv('CONTROL_DIO'))

#     BIG_BUTTON_PIN = int(os.getenv('BIG_BUTTON_PIN'))
#     #http://razzpisampler.oreilly.com/ch07.html

#     SIZE = 8

#     button_state = [False] * SIZE
#     prev_button_state = [False] * SIZE

#     TM = None

#     def __init__(self):
#         self.TM = TMBoards(self.DIO, self.CLK, self.STB, 0)
#         GPIO.setmode(GPIO.BCM)
#         GPIO.setup(self.BIG_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

#     def update_buttons(self):
#         for num in range(self.SIZE):
#             self.prev_button_state[num] = self.button_state[num]
#             self.button_state[num] = self.TM.switches[num]
#         self.button_state[0] = self.button_state[0] or (not GPIO.input(self.BIG_BUTTON_PIN))

#     def button_just_pressed(self, num):
#         return not self.prev_button_state[num] and self.button_state[num]
    
#     def button_just_released(self, num):
#         return not self.prev_button_state[num] and self.button_state[num]

#     def get_buttons(self):
#         return self.button_state

#     # def get_buttons(self):
#     #     return [self.TM.switches[i] for i in range(self.SIZE)]

#     # def get_button(self, num):
#     #     return self.TM.switches[num]

#     def set_leds(self, vals):
#         for num, val in enumerate(vals):
#             self.TM.leds[num] = val

#     def set_led(self, num, val):
#         self.TM.leds[num] = val

#     def write_text(self, str, index=0):
#         for i in range(self.SIZE):
#             if (i >= index and i < len(str) + index):
#                 self.TM.segments[i] = str[i - index]
#             else:
#                 self.TM.segments[i] = " "
#         pass

#     def clear(self):
#         for num in range(self.SIZE):
#             self.TM.segments[num] = ' '
#             self.TM.leds[num] = False


# Tests
if __name__ == '__main__':
    
    rich.print("hello")
#     contr = ControllerManager()

#     atexit.register(lambda: contr.clear())


#     contr.write_text("abcdefghi", 2)

#     while (not contr.button_just_pressed(7)):
#         contr.update_buttons()
#         but = contr.get_buttons()
# #
#         contr.set_leds(but)

#         rich.print(but)
#         time.sleep(0.1)


#     contr.clear()
#     rich.print("END")
