
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
    
try:
    import Adafruit_DHT
except ImportError:
    from .mockAdafruit_DHT import Adafruit_DHT

import websockets
from websockets.sync.server import serve

from dotenv import load_dotenv

load_dotenv()


class StandbyManager:
    _instance = None
    
    curr_timer = 1900
    curr_temperature = 0
    curr_humidity = 0

    #passive infrared
    PIR_PIN = int(os.getenv('PIR_PIN'))
    CLAP_PIN = int(os.getenv('CLAP_PIN'))
    TEMP_PIN = int(os.getenv('TEMP_PIN'))
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(StandbyManager, cls).__new__(cls)
            cls._instance.curr_temperature = 0
            cls._instance.curr_humidity = 0
            
            GPIO.cleanup()

            GPIO.setmode(GPIO.BOARD)
            GPIO.setup(cls._instance.PIR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(cls._instance.CLAP_PIN, GPIO.IN)
#            GPIO.setup(cls._instance.CLAP_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(cls._instance.CLAP_PIN, GPIO.BOTH, callback=cls._instance.get_clap, bouncetime=300)
#            GPIO.add_event_callback(cls._instance.CLAP_PIN, cls._instance.get_clap)
    
        return cls._instance
    

    def get_pir(self):
        return bool(GPIO.input(self.PIR_PIN))

    def get_clap(self, chan):
        val = not(bool(GPIO.input(self.CLAP_PIN)))
        rich.print("MOVE to", val)

        if (val == True):
            self.curr_timer = datetime.datetime.now()
        #return not(bool(GPIO.input(self.CLAP_PIN)))

    def get_temp_humid(self):
        start_time = time.time()
        humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, self.TEMP_PIN)
        end_time = time.time()
        rich.print(start_time, end_time, end_time - start_time)
        return (humidity, temperature)




CLIENTS = dict()
manager = StandbyManager()


def sleep_watcher():
    global CLIENTS
    manager = StandbyManager()

    while True:
        pir = manager.get_pir()

        if (pir == True):
            manager.curr_timer = datetime.datetime.now()

        for sockid in CLIENTS:
            try:
                CLIENTS[sockid].send(json.dumps({
                    'type': 'SLEEP',
                    'timer': manager.curr_timer,
                }))
            except websockets.exceptions.ConnectionClosedError:
                if (sockid in CLIENTS):
                    CLIENTS.remove(sockid)
                rich.print(f"[yellow]unsubscribed {str(sockid)[:8]}")

        time.sleep(30)


def temp_watcher():
    global CLIENTS
    manager = StandbyManager()

    while True:
        humidity, temperature = manager.get_temp_humid()

        manager.curr_temperature = temperature
        manager.curr_humidity = humidity

        for sockid in CLIENTS:
            try:
                CLIENTS[sockid].send(json.dumps({
                    'type': 'TEMP',
                    'temperature-int': manager.curr_temperature,
                    'humidity-int': manager.curr_humidity
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
                        'temperature-int': manager.curr_temperature,
                        'humidity-int': manager.curr_humidity
                    }))
                    websocket.send(json.dumps({
                        'type': 'SLEEP',
                        'timer': manager.curr_timer,
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

    # threads.append(threading.Thread(target=sleep_watcher, args=()))
    # threads[-1].start()
    threads.append(threading.Thread(target=temp_watcher, args=()))
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

#     rich.print("hello")

#     oldval = False
    oldcnt = 0

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
