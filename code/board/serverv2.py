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

from code.board.cffv2 import conn_search
from code._common.app_config import ConfigManager
from code._common.discord_message import create_discord_payload, send_discord_payload
from code._common.utils import pluralize, discord_time

CLIENTS = dict()
conf_manager = ConfigManager()
buffers = {}


def notify(changes, infos, conf_name):
    embed = {
        'message_type': 'embed',
        # embed["thumbnail"] = f'{fetched["avatar_url"]}',
        'footer_text': datetime.datetime.now().astimezone(tz=pytz.timezone('Europe/Zurich')).strftime('%Y-%m-%d %H:%M:%S')
    }

    embed['title'] = f'{conf_name}: `{infos["from"]}` to `{infos["to"]}` at {infos["train"]["time"]}\n'
    embed['title'] += f'{infos["train"]["delay"]} {pluralize(infos["train"]["delay"], "minute", "minutes")} delay'

    embed['fields'] = dict({
        k.capitalize(): f'ref: {v["old"]}{chr(10) if len(str(v["new"])) > 0 else " "}new: {v["new"]}' for k, v in changes.items()
    })

    payload = create_discord_payload(embed)
    send_discord_payload(payload)



def check_changes(elem, conf):
    changes = {}
    conf_id = conf.get("id")
    elem_id = elem["id"]

    # rich.print('tt', elem)

    # First changes detection
    if elem_id not in buffers[conf_id].keys():
        buffers[conf_id][elem_id] = {
            **elem,
            # 'train': {**elem['train'], 'delay': 10},
            "last_update": round(datetime.datetime.timestamp(datetime.datetime.now()))
        }

        if(elem["train"]["delay"] >= conf.get("min_delay")):
            changes["delay"] = {
                "old": '',
                "new": elem["train"]["delay"]
            }

        if('!' in elem["train"]["platform"]):
            changes["platform"] = {
                "old": '',
                "new": elem["train"]["platform"]
            }


    # Get old or actual if not exists
    buffer_elem = buffers[conf_id][elem_id]

    # rich.print('cmp', elem, buffer_elem)

    # Diff checks
    if (elem["train"]["delay"] != None and
        (
            (elem["train"]["delay"] > buffer_elem["train"]["delay"] and elem["train"]["delay"] >= conf.get("min_delay")) or
            (elem["train"]["delay"] < buffer_elem["train"]["delay"] and buffer_elem["train"]["delay"] >= conf.get("min_delay"))
        )
    ):
        changes["delay"] = {
            "old": buffer_elem["train"]["delay"],
            "new": elem["train"]["delay"]
        }

    if (elem["train"]["platform"] != None and
        (elem["train"]["platform"] != buffer_elem["train"]["platform"] or
         '!' in f'{elem["train"]["platform"]} {buffer_elem["train"]["platform"]}')
    ):
        changes["platform"] = {
            "old": buffer_elem["train"]["platform"],
            "new": elem["train"]["platform"]
        }

    if (elem["disruptions"] != None and
        elem["disruptions"] != buffer_elem["disruptions"]
    ):
        changes["disruptions"] = {
            "old": buffer_elem["disruptions"],
            "new": elem["disruptions"]
        }

    # time_compare = datetime.datetime.isoformat(parser.parse(elem["start"]["time"]))[11:]
    time_compare = elem["train"]["time"]

    if (len(changes) > 0 and conf.get("notify_start") != None and (
        conf.get("notify_end") == None or (
            time_compare >= conf.get("notify_start") and
            time_compare <= conf.get("notify_end")
        )
    )):
        notify(changes, elem, conf.get("name") or "")

    buffers[conf_id][elem_id] = {
        **buffers[conf_id][elem_id],
        **elem,
        "last_update": round(datetime.datetime.timestamp(datetime.datetime.now()))
    }
    buffers[conf_id][elem_id]

def update(check):
    conf_id = check["id"]
    if (conf_id not in buffers.keys()):
        buffers[conf_id] = {}

    res = []

    time_compare = datetime.datetime.now().strftime("%H:%M:%S")

    if (check.get("check_start") != None and (
        check.get("check_end") == None or (
            time_compare >= check.get("check_start") and
            time_compare <= check.get("check_end")
        )
    )):
        if (check.get('type') == 'connection'): # period start and period end
            res = conn_search(q=check.get('query'), l=check.get('checks') or 5)
            # rich.print('res', res)

    for elem in res:
        try:
            check_changes(elem, check)
        except Exception as e:
            rich.print("[red]", 'unexpected error', e, elem)

    tcmp = round(datetime.datetime.timestamp(datetime.datetime.now())) - ((check.get("check_frequency") or 30) * 0.8)
    buffers[conf_id] = {k: v for k, v in buffers[conf_id].items() if v["last_update"] > tcmp}


def updater(check):
    rich.print(f"[green]updater {check['id']} started")
    while True:
        try:
            update(check)
        except Exception as e:
            rich.print(f"[red]Whole loop error: {str(e)}")
        time.sleep(check.get("check_frequency") or 60)

@click.command()
@click.option("--server", "-s", type=bool, is_flag=True, default=False, help="update all")
def main(server=False):
    threads = []


    for check in conf_manager.check_list:
        # updater(check)
        threads.append(threading.Thread(target=updater, args=(check,)))
        threads[-1].start()
        time.sleep(1)

    if (server):
        rich.print("[magenta]Started server")
    else:
        rich.print("[magenta]SERVERLESS MODE")

    for thread in threads:
        thread.join()


if __name__ == "__main__":
    main()