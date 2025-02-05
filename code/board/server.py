#!/usr/bin/env python

import rich
import json
import time

import click
import threading
import datetime
import pytz
import websockets

from websockets.sync.server import serve

from code.board.cff import conn_search, station_search
from code._common.app_config import ConfigManager
from code._common.discord_message import create_discord_payload, send_discord_payload
from code._common.utils import pluralize, discord_time

CLIENTS = dict()
conf_manager = ConfigManager()
buffers = {}


def handle(websocket):
    try:
        for message in websocket:
            try:
                payload = json.loads(message)
                if (payload.get("COMMAND") == "SUBSCRIBE"):
                    rich.print(f"[yellow]subscribed {str(websocket.id)[:8]}")
                    CLIENTS.update({websocket.id: websocket})

                    for sub_buffer in buffers.keys():
                        check = next(filter(lambda x: x["id"] == sub_buffer, conf_manager.check_list))
                        websocket.send(json.dumps({
                            'id': sub_buffer, 
                            'name': check.get('name') or '', 
                            'elems': list(buffers[sub_buffer].values()) or []
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



def notify(changes, infos):
    embed = {
        'message_type': 'embed',
        # embed["thumbnail"] = f'{fetched["avatar_url"]}',
        'footer_text': datetime.datetime.now().astimezone(tz=pytz.timezone('Europe/Zurich')).strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # cat = "undefined"
    # if (cmpp["category"] == "R"):
    #     cat = "train"


    embed['title'] = f'`{infos["start"]["name"]}` to `{infos["to"]}` at {infos["start"]["time"][11:16]}\n'
    embed['title'] += f'{infos["start"]["delay"]} {pluralize(infos["start"]["delay"], "minute", "minutes")} delay'
    
    embed['fields'] = dict({
        k.capitalize(): f'ref: {v["old"]}{chr(10) if len(str(v["new"])) > 0 else " "}new: {v["new"]}' for k, v in changes.items()
    })
    
    payload = create_discord_payload(embed)
    send_discord_payload(payload)



def check_changes(elem, conf):
    changes = {}
    conf_id = conf.get("id")
    elem_id = elem["name"]

    # First changes detection
    if elem_id not in buffers[conf_id].keys():
        buffers[conf_id][elem_id] = {
            **elem,
            "last_update": round(datetime.datetime.timestamp(datetime.datetime.now()))
        }
        
        if (elem["start"]["delay"] != None and elem["start"]["delay"] >= conf.get("min_delay") or 0):
            changes["delay"] = {"old": "-", "new": elem["start"]["delay"]}

            if (elem["start"]["prono_time"] != None and elem["start"]["time"] != elem["start"]["prono_time"]):
                changes["time"] = {
                    "old": discord_time(elem["start"]["time"]),
                    "new": discord_time(elem["start"]["prono_time"])
                }
            
        if (elem["start"]["prono_platform"] != None and elem["start"]["platform"] != elem["start"]["prono_time"]):
            changes["platform"] = {
                "old": discord_time(elem["start"]["platform"]),
                "new": discord_time(elem["start"]["prono_platform"])
            }

    # Get old or actual if not exists
    buffer_elem = buffers[conf_id][elem_id]

    # Diff checks
    if (elem["start"]["delay"] != None and 
        (
            (elem["start"]["delay"] > buffer_elem["start"]["delay"] and elem["start"]["delay"] >= conf.get("min_delay")) or
            (elem["start"]["delay"] < buffer_elem["start"]["delay"] and buffer_elem["start"]["delay"] >= conf.get("min_delay")) 
        )
    ):
        changes["delay"] = {
            "old": buffer_elem["start"]["delay"], 
            "new": elem["start"]["delay"]
        }
        
        if (elem["start"]["prono_time"] != None and 
            elem["start"]["prono_time"] != buffer_elem["start"]["prono_time"]
        ):
            changes["prono_time"] = {
                "old": discord_time(buffer_elem["start"]["prono_time"]),
                "new": discord_time(elem["start"]["prono_time"])
            }
        
    if (elem["start"]["prono_platform"] != None and
        elem["start"]["prono_platform"] != buffer_elem["start"]["prono_platform"]
    ):
        changes["prono_platform"] = {
            "old": discord_time(buffer_elem["start"]["prono_platform"]),
            "new": discord_time(elem["start"]["prono_platform"])
        }

    # time_compare = datetime.datetime.isoformat(parser.parse(elem["start"]["time"]))[11:]
    time_compare = elem["start"]["time"][11:]

    # rich.print(conf)
    if (len(changes) > 0 and conf.get("notify_start") != None and (
        conf.get("notify_end") == None or (
            time_compare >= conf.get("notify_start") and 
            time_compare <= conf.get("notify_end")
        )
    )):
        notify(changes, elem)

    buffers[conf_id][elem_id] = {
        **elem,
        "last_update": round(datetime.datetime.timestamp(datetime.datetime.now()))
    }

def update(check):
    conf_id = check["id"]
    if (conf_id not in buffers.keys()):
        buffers[conf_id] = {}

    if (check.get('type') == 'connection'): # period start and period end
        res = conn_search(q=check.get('query'), l=check.get('checks') or 5)

    elif (check.get('type') == 'stationboard'): # period start and period end
        res = station_search(q=check.get('query'), l=check.get('checks') or 5)

    if (check.get('display') == True):
        for sockid in CLIENTS:
            try:
                CLIENTS[sockid].send(json.dumps({
                    'id': conf_id, 
                    'name': check.get('name'), 
                    'elems': res
                }))
            except websockets.exceptions.ConnectionClosedError:
                if (sockid in CLIENTS):
                    CLIENTS.pop(sockid)
                rich.print(f"[yellow]unsubscribed {str(sockid)[:8]}")

    for elem in res:
        try:
            check_changes(elem, check)
        except Exception as e:
            rich.print("[red]", 'unexpected error', e, elem)

    tcmp = round(datetime.datetime.timestamp(datetime.datetime.now())) - ((check.get("check_frequency") or 30) * 2)
    buffers[conf_id] = {k: v for k, v in buffers[conf_id].items() if v["last_update"] > tcmp}


def updater(check):
    rich.print(f"[green]updater {check['id']} started")
    while True:
        update(check)
        time.sleep(check.get("check_frequency") or 60)

@click.command()
@click.option("--server", "-s", type=bool, is_flag=True, default=False, help="update all")
def main(server=False):
    threads = []

    for check in conf_manager.check_list:
        threads.append(threading.Thread(target=updater, args=(check,)))
        threads[-1].start()
        time.sleep(1)

    if (server):
        rich.print("[magenta]Started server")
        with serve(handle, "localhost", 8765) as server:
            server.serve_forever()
    else:
        rich.print("[magenta]SERVERLESS MODE")

    for thread in threads:
        thread.join()


if __name__ == "__main__":
    main()