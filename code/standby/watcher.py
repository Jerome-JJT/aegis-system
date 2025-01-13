
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


class ControllerManager:

    #passive infrared
    PIR_PIN = int(os.getenv('PIR_PIN'))
    def __init__(self):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.PIR_PIN, GPIO.IN)	


    def get_pir(self):
        return GPIO.input(self.PIR_PIN)

    # def update_buttons(self):
    #     for num in range(self.SIZE):
    #         self.prev_button_state[num] = self.button_state[num]
    #         self.button_state[num] = self.TM.switches[num]
    #     self.button_state[0] = self.button_state[0] or (not GPIO.input(self.BIG_BUTTON_PIN))

    # def button_just_pressed(self, num):
    #     return not self.prev_button_state[num] and self.button_state[num]
    
    # def button_just_released(self, num):
    #     return not self.prev_button_state[num] and self.button_state[num]
    # def get_buttons(self):
    #     return [self.TM.switches[i] for i in range(self.SIZE)]

    # def get_button(self, num):
    #     return self.TM.switches[num]

    # def set_leds(self, vals):
    #     for num, val in enumerate(vals):
    #         self.TM.leds[num] = val

    # def set_led(self, num, val):
    #     self.TM.leds[num] = val

    # def write_text(self, str, index=0):
    #     for i in range(self.SIZE):
    #         if (i >= index and i < len(str) + index):
    #             self.TM.segments[i] = str[i - index]
    #         else:
    #             self.TM.segments[i] = " "
    #     pass

    # def clear(self):
    #     for num in range(self.SIZE):
    #         self.TM.segments[num] = ' '
    #         self.TM.leds[num] = False


# Tests
if __name__ == '__main__':
    
    rich.print("hello")
    contr = ControllerManager()

#     atexit.register(lambda: contr.clear())


#     contr.write_text("abcdefghi", 2)

    while (True):
        res = contr.get_pir()
        rich.print(res)
        
        time.sleep(0.1)


#     contr.clear()
#     rich.print("END")
