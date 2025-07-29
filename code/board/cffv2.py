import sys
import time
import math
import rich
import requests
import datetime
import pytz

from .._common.utils import pluralize, cardinalinator, discord_time
from .._common.discord_message import create_discord_payload, send_discord_payload

def parse_loc(loc):

    # rich.print("LOC", loc)

    nloc = { 
        "name": loc["name"],
        "coordinate": {
            "lat": loc["lat"],
            "lon": loc["lon"],
        },
        
        "time": loc["departure"].split(' ')[-1],
        "delay": int(loc["dep_delay"]) if 'dep_delay' in loc.keys() else 0,

        "platform": loc["*L"],
    }
    
    return nloc

def parse_con(con):

    # rich.print("CON", con)
    
    ncon = {
        "id": con["legs"][0]['tripid'],
        "train": parse_loc(con["legs"][0]),
        "from": con['from'],
        "to": con['to'],
         
        "duration": con["duration"],
        "category": con["legs"][0]["type"],
        "name": con["legs"][0]["name"],
        "disruptions": " ".join(map(lambda x: str(x), con["disruptions"])) if 'disruptions' in con.keys() else ''
    }

    diff_first = {
        "x": con["legs"][0]["lon"] - con["legs"][-1]["lon"],
        "y": con["legs"][0]["lat"] - con["legs"][-1]["lat"]
    }
    diff_first = {
        "x": con["legs"][0]["lon"] - con["legs"][-1]["lon"],
        "y": con["legs"][0]["lat"] - con["legs"][-1]["lat"]
    }
    
    ncon["raw_dir"] = math.atan2(diff_first["y"], diff_first["x"])
    ncon["dir"] = cardinalinator(ncon["raw_dir"])

    return ncon

def conn_search(q="from=Chavornay&to=Renens", l=2):
    # limiter = "&fields[]=connections/from&fields[]=connections/to&fields[]=connections/duration&fields[]=connections/transfers&fields[]=connections/products"

    try:
        # url = f"http://transport.opendata.ch/v1/connections?{q}&limit={l}"
        url = f"https://search.ch/timetable/api/route.json?show_delays=1&show_trackchanges=1&{q}&num={l}&time=7:00"
        # rich.print("REQ", url)
        req = requests.get(url)

        if (req.ok):
            js = req.json()

            # rich.print(js)
            cons = list(map(lambda x: parse_con({**x}), js["connections"]))

            # rich.print(cons)
            
            return cons

        else:
            rich.print(f"[red]FAIL {req.status_code} {req.reason}")
            return []

    except requests.exceptions.ConnectionError:
        rich.print(f"[red]FAIL ConnectionError")
        return []
    

buffer = {}

if (len(sys.argv) >= 2):
    
    if (sys.argv[1] == "0"):
        aa = conn_search(l = 4)
    
    elif (sys.argv[1] == "2"):
        pass
        # while True:
            
            # # res = conn_search(q="from=Zurich&to=Munchen", l = 4)
            # res = conn_search(l = 4)
            # rich.print(res)
            
            # todel = list(buffer.keys())
            
            # for r in res:
            #     changes = {}
            #     # rich.print(r)
            #     idd = r["name"]
            #     if idd in list(buffer.keys()):
            #         todel.remove(idd)
                
            #     if idd not in buffer.keys():
            #         buffer[idd] = r
                    
            #         if (r["start"]["delay"] != None and r["start"]["delay"] >= 2):
            #             changes["delay"] = {"old": "-", "new": r["start"]["delay"]}

            #             if (r["start"]["prono_time"] != None and r["start"]["time"] != r["start"]["prono_time"]):
            #                 changes["time"] = {
            #                     "old": discord_time(r["start"]["time"]),
            #                     "new": discord_time(r["start"]["prono_time"])
            #                 }
                        
            #         if (r["start"]["prono_platform"] != None and r["start"]["platform"] != r["start"]["prono_time"]):
            #             changes["platform"] = {
            #                 "old": discord_time(r["start"]["platform"]),
            #                 "new": discord_time(r["start"]["prono_platform"]),
            #             }
                        
            #     cmpp = buffer[idd]

            #     if (r["start"]["delay"] != cmpp["start"]["delay"]):
            #         changes["delay"] = {
            #             "old": cmpp["start"]["delay"], 
            #             "new": r["start"]["delay"]
            #         }
                    
            #     if (r["start"]["prono_time"] != cmpp["start"]["prono_time"]):
            #         changes["prono_time"] = {
            #             "old": discord_time(cmpp["start"]["prono_time"]),
            #             "new": discord_time(r["start"]["prono_time"])
            #         }
                    
            #     if (r["start"]["prono_platform"] != buffer[idd]["start"]["prono_platform"]):
            #         changes["prono_platform"] = {
            #             "old": discord_time(cmpp["start"]["prono_platform"]),
            #             "new": discord_time(r["start"]["prono_platform"])
            #         }
                    
            #     # rich.print(idd, changes)
                
            #     if (len(changes)):
            #         embed = {
            #             'message_type': 'embed',
            #             # embed["thumbnail"] = f'{fetched["avatar_url"]}',
            #             'footer_text': datetime.datetime.now().astimezone(tz=pytz.timezone('Europe/Zurich')).strftime('%Y-%m-%d %H:%M:%S')
            #         }
                    
            #         # cat = "undefined"
            #         # if (cmpp["category"] == "R"):
            #         #     cat = "train"


            #         embed['title'] = f'{r["start"]["name"]} to {r["to"]} at {cmpp['start']['time'][11:16]}\n'
            #         embed['title'] += f'{cmpp['start']['delay']} {pluralize(cmpp['start']['delay'], 'minute', 'minutes')} delay'
                    
            #         embed['fields'] = dict({
            #             k.capitalize(): f'ref: `{v["old"]}`{'\n' if len(str(v['new'])) > 10 else ' '}new: `{v["new"]}`' for k, v in changes.items()
            #         })
                    
            #         payload = create_discord_payload(embed)
            #         send_discord_payload(payload)

            #         rich.print(idd, embed)
            #         rich.print()
                    
                
            # # rich.print("BUFFER", buffer)
            # for to in todel:
            #     del buffer[to]
            
            # time.sleep(60)
