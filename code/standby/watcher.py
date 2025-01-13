
import os
import time
import rich
import atexit

try:
    import RPi.GPIO as GPIO
except ImportError:
    from mockGPIO import GPIO
import Adafruit_DHT

from dotenv import load_dotenv

load_dotenv()


class ControllerManager:

    #passive infrared
    PIR_PIN = int(os.getenv('PIR_PIN'))
    CLAP_PIN = int(os.getenv('CLAP_PIN'))
    TEMP_PIN = int(os.getenv('TEMP_PIN'))


    def __init__(self):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.PIR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#        GPIO.setup(self.CLAP_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)


    def get_pir(self):
        return bool(GPIO.input(self.PIR_PIN))

    def get_clap(self):
        return not(bool(GPIO.input(self.CLAP_PIN)))

    def get_temp_humid(self):
        start_time = time.time()
        humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, self.TEMP_PIN)
        end_time = time.time()
        rich.print(start_time, end_time, end_time - start_time)
        return (humidity, temperature)

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

    oldval = False
    oldcnt = 0

    while (True):
        #res = contr.get_pir()
#        res = contr.get_clap()
#        if (oldval == res):
#            oldcnt += 1
#        else:
#            oldcnt = 0

#        oldval = res
#        rich.print(res, oldcnt)

        h, t = contr.get_temp_humid()
        print(f"Measured Temp={t}°C | Hum={h}%")

        time.sleep(0.1)


#     contr.clear()
#     rich.print("END")
