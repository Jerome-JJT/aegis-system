
import os
import time
import rich
import datetime
import threading
import json
import click

try:
    import RPi.GPIO as GPIO
except ImportError:
    from .mockGPIO import GPIO

#try:
from code._common.dht import DHT
#except ImportError:
#    from .mockAdafruit_DHT import Adafruit_DHT

import websockets
from websockets.sync.server import serve

from dotenv import load_dotenv

load_dotenv(override=True)


class StandbyManager:
    _instance = None

    is_sleeping = True
    curr_timer = datetime.datetime.now() + datetime.timedelta(minutes=10)

    captors = {
        "int": {
            "dht": None,
            "temperature": 0,
            "humidity": 0,
        },
        "ext": {
            "dht": None,
            "temperature": 0,
            "humidity": 0,
        }

    }
    curr_temperature = 0
    curr_humidity = 0

    #passive infrared
    PIR_PIN = int(os.getenv('PIR_PIN'))
    CLAP_PIN = int(os.getenv('CLAP_PIN'))
    TEMP_INT_PIN = int(os.getenv('TEMP_INT_PIN'))
    TEMP_EXT_PIN = int(os.getenv('TEMP_EXT_PIN'))

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(StandbyManager, cls).__new__(cls)

            GPIO.setmode(GPIO.BOARD)

            if (cls._instance.TEMP_INT_PIN > 0):
                cls._instance.captors["int"]["dht"] = DHT(cls._instance.TEMP_INT_PIN, True)

            if (cls._instance.TEMP_EXT_PIN > 0):
                cls._instance.captors["ext"]["dht"] = DHT(cls._instance.TEMP_EXT_PIN, True)

            if (cls._instance.PIR_PIN > 0):
                GPIO.setup(cls._instance.PIR_PIN, GPIO.IN)

            if (cls._instance.CLAP_PIN > 0):
                GPIO.setup(cls._instance.CLAP_PIN, GPIO.IN)
                GPIO.add_event_detect(cls._instance.CLAP_PIN, GPIO.RISING, cls._instance.clap_cb)

        #    GPIO.setup(cls._instance.CLAP_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            # GPIO.add_event_detect(cls._instance.CLAP_PIN, GPIO.BOTH, callback=cls._instance.get_clap, bouncetime=300)

        return cls._instance


    def get_pir(self):
#        rich.print(self.PIR_PIN)
        val = bool(GPIO.input(self.PIR_PIN))
#        rich.print("PIR VALUE", val)
        return val

    def clap_cb(self, channel):
        rich.print("[magenta]CLAP CB RISING")

        manager.curr_timer = max(manager.curr_timer, datetime.datetime.now() + datetime.timedelta(minutes=10))

    def get_clap(self):
#        rich.print(self.CLAP_PIN)
        val = not(bool(GPIO.input(self.CLAP_PIN)))
        return val

    def get_temp_humid(self, dht):
        start_time = time.time()

        res = dht.read()
        for i in range(0, 15):
            if  (res.is_valid()):
                break
            else:
                time.sleep(2)
                res = dht.read()

        end_time = time.time()
        rich.print("TIME FOR TEMP", start_time, end_time, end_time - start_time, res.is_valid(), res.humidity, res.temperature)

        if (res.is_valid()):
            return (res.humidity, res.temperature)
        else:
            return (None, None)


CLIENTS = dict()
manager = StandbyManager()


def sleep_watcher():
    global CLIENTS
    manager = StandbyManager()
    old_curr_timer = None

    while True:

#        rich.print("CMP", manager.curr_timer, datetime.datetime.now(), manager.is_sleeping)

        if (manager.curr_timer < datetime.datetime.now() and manager.is_sleeping == False):
            manager.is_sleeping = True
            rich.print(f"[magenta]TURNING OFF SCREEN", datetime.datetime.now())
            os.system("/usr/bin/sudo /home/admin/aegis-system/services/manage_hdmi.sh off")

        elif (manager.curr_timer > datetime.datetime.now() and manager.is_sleeping == True):
            manager.is_sleeping = False
            rich.print(f"[magenta]TURNING ON SCREEN", datetime.datetime.now())
            os.system("/usr/bin/sudo /home/admin/aegis-system/services/manage_hdmi.sh on")

        if (old_curr_timer != manager.curr_timer):
            old_curr_timer = manager.curr_timer

            for sockid in CLIENTS:
                try:
                    CLIENTS[sockid].send(json.dumps({
                        'type': 'SLEEP',
                        'timer': manager.curr_timer.strftime("%Y-%m-%d, %H:%M:%S")
                    }))
                except websockets.exceptions.ConnectionClosedError:
                    if (sockid in CLIENTS):
                        CLIENTS.remove(sockid)
                    rich.print(f"[yellow]unsubscribed {str(sockid)[:8]}")

        time.sleep(3)


def pir_watcher():
    global CLIENTS
    manager = StandbyManager()
    rich.print(f"[magenta]PIR watcher loaded")

    while True:
        pir = manager.get_pir()

        if (pir == True):
            rich.print(f"[magenta]detect PIR")
            manager.curr_timer = max(manager.curr_timer, datetime.datetime.now() + datetime.timedelta(minutes=10))

        time.sleep(0.4)

def clap_watcher():
    global CLIENTS
    manager = StandbyManager()
    rich.print(f"[magenta]CLAP watcher loaded")

    while True:
        clap = manager.get_clap()

        if (clap == True):
            rich.print(f"[magenta]detect CLAP")
            manager.curr_timer = max(manager.curr_timer, datetime.datetime.now() + datetime.timedelta(minutes=10))

        time.sleep(1)


def temp_watcher(place = 'int'):
    global CLIENTS
    manager = StandbyManager()
    rich.print(f"[magenta]TEMP {place} watcher loaded")

    while True:
        humidity, temperature = manager.get_temp_humid(manager.captors[place]['dht'])

        if (temperature != None and humidity != None):
            manager.captors[place]['temperature'] = temperature
            manager.captors[place]['humidity'] = humidity

            for sockid in CLIENTS:
                try:
                    CLIENTS[sockid].send(json.dumps({
                        'type': 'TEMP',
                        f'temperature-{place}': manager.captors[place]['temperature'],
                        f'humidity-{place}': manager.captors[place]['humidity']
                    }))
                except websockets.exceptions.ConnectionClosedError:
                    if (sockid in CLIENTS):
                        CLIENTS.remove(sockid)
                    rich.print(f"[yellow]unsubscribed {str(sockid)[:8]}")

        time.sleep(3)


def handle(websocket):
    try:
        for message in websocket:
            try:
                payload = json.loads(message)
                if (payload.get("COMMAND") == "SUBSCRIBE"):
                    rich.print("[yellow]subscribed")
                    CLIENTS.update({websocket.id: websocket})

                    websocket.send(json.dumps({
                        'type': 'TEMP',
                        'temperature-in': manager.captors['in']['temperature'],
                        'humidity-int': manager.captors['int']['humidity'],
                        'temperature-ext': manager.captors['ext']['temperature'],
                        'humidity-ext': manager.captors['ext']['humidity']
                    }))
                    websocket.send(json.dumps({
                        'type': 'SLEEP',
                        'timer': manager.curr_timer.strftime("%Y-%m-%d, %H:%M:%S"),
                    }))

            except json.decoder.JSONDecodeError:
                rich.print(f"[red]unparsable {message}")

    except websockets.exceptions.ConnectionClosedError:
        if (websocket.id in CLIENTS):
            CLIENTS.pop(websocket.id)
        rich.print(f"[yellow]unsubscribed {str(websocket.id)[:8]}")
        pass
    finally:
        if (websocket.id in CLIENTS):
            CLIENTS.pop(websocket.id)
        rich.print(f"[yellow]unsubscribed {str(websocket.id)[:8]}")


@click.command()
@click.option("--server", "-s", type=bool, is_flag=True, default=False, help="update all")
def main(server=False):
    threads = []

#    threads.append(threading.Thread(target=clap_watcher, args=()))
#    threads[-1].start()

    threads.append(threading.Thread(target=sleep_watcher, args=()))
    threads[-1].start()

    if (manager.PIR_PIN > 0):
        threads.append(threading.Thread(target=pir_watcher, args=()))
        threads[-1].start()

    if (manager.TEMP_INT_PIN > 0):
        threads.append(threading.Thread(target=temp_watcher, args=('int',)))
        threads[-1].start()
    if (manager.TEMP_EXT_PIN > 0):
        threads.append(threading.Thread(target=temp_watcher, args=('ext',)))
        threads[-1].start()

    if (server):
        with serve(handle, "localhost", 8766) as server:
            server.serve_forever()
    else:
        rich.print("[magenta]SERVERLESS MODE")

    for thread in threads:
        thread.join()

if __name__ == '__main__':
    main()

    while (True):
#         res = manager.get_pir()
        res = manager.get_clap()
# #        if (oldval == res):
# #            oldcnt += 1
# #        else:
# #            oldcnt = 0

# #        oldval = res
        rich.print(res, oldcnt)

#         # h, t = manager.get_temp_humid()
#         # print(f"Measured Temp={t}°C | Hum={h}%")

#         time.sleep(0.1)
