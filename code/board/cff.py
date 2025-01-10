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
    
    nloc = { 
        "id": loc["station"]["id"],
        "name": loc["station"]["name"],
        "coordinate": loc["station"]["coordinate"],
        
        "time": loc["departure"] if loc["departure"] != None else loc["arrival"],
        "prono_time": loc["prognosis"]["departure"] if loc["departure"] != None else loc["prognosis"]["arrival"],

        "platform": loc["platform"],
        "prono_platform": loc["prognosis"]["platform"],

        "delay": loc["delay"],
        # "prognosis": loc["prognosis"],
    }
    
    return nloc

def parse_con(con):
    
    ncon = {
        "start": parse_loc(con["from"]),
        "end": parse_loc(con["to"]),
        "to": con["to"]["station"]["name"],
        
        "duration": con["duration"],
        "transfers": con["transfers"],
        # "products": ",".join(con["products"]) if type(con["products"]) == type([]) else con["products"],
        "category": con["sections"][0]["journey"]["category"],
        "name": con["sections"][0]["journey"]["name"]
    }

    diff_first = {
        "x": con["to"]["station"]["coordinate"]["x"] - con["from"]["station"]["coordinate"]["x"],
        "y": con["to"]["station"]["coordinate"]["y"] - con["from"]["station"]["coordinate"]["y"]
    }
    diff_first = {
        "x": con["to"]["station"]["coordinate"]["x"] - con["from"]["station"]["coordinate"]["x"],
        "y": con["to"]["station"]["coordinate"]["y"] - con["from"]["station"]["coordinate"]["y"]
    }
    
    ncon["raw_dir"] = math.atan2(diff_first["y"], diff_first["x"])
    ncon["dir"] = cardinalinator(ncon["raw_dir"])

    return ncon

def parse_stationboard(st):

    nst = {
        "start": parse_loc(st["stop"]),
        "name": st["name"],
        "category": st["category"],
        "number": st["number"],
        "operator": st["operator"],
        "to": st["to"],
        "end": parse_loc(st["passList"][-1]),
        # "dest": parse_loc(st["passList"][1]),
    }
    
    # diff = {
    #     "x": nst["dest"]["coordinate"]["x"] - nst["stop"]["coordinate"]["x"],
    #     "y": nst["dest"]["coordinate"]["y"] - nst["stop"]["coordinate"]["y"]
    # }
    diff_first = {
        "x": st["passList"][1]["station"]["coordinate"]["x"] - st["stop"]["station"]["coordinate"]["x"],
        "y": st["passList"][1]["station"]["coordinate"]["y"] - st["stop"]["station"]["coordinate"]["y"]
    }
    # nst["diff"] = diff
    # nst["diff_first"] = diff_first
    
    
    
    nst["raw_dir"] = math.atan2(diff_first["y"], diff_first["x"])
    nst["dir"] = cardinalinator(nst["raw_dir"])
    
    return nst




def conn_search(q="from=Chavornay&to=Renens", l=10):
    
    # limiter = "&fields[]=connections/from&fields[]=connections/to&fields[]=connections/duration&fields[]=connections/transfers&fields[]=connections/products"

    url = f"http://transport.opendata.ch/v1/connections?{q}&limit={l}"
    rich.print("REQ", url)
    req = requests.get(url)

    if (req.ok):
        js = req.json()
        
        cons = list(map(lambda x: parse_con(x), js["connections"]))

        # rich.print(cons)
        
        return cons

    else:
        rich.print(f"[red]FAIL {req.status_code} {req.reason}")
        return []

def station_search(q="station=Renens, Village", l=10):
    
    url = f"http://transport.opendata.ch/v1/stationboard?{q}&limit={l}"
    rich.print("REQ", url)
    req = requests.get(url)

    if (req.ok):
        js = req.json()

        stati = list(map(lambda x: parse_stationboard(x), js["stationboard"]))
        
        # rich.print(stati)
        
        return stati

    else:
        rich.print(f"[red]FAIL {req.status_code} {req.reason}")
        return []


buffer = {}

if (len(sys.argv) >= 2):
    
    if (sys.argv[1] == "0"):
        aa = conn_search(l = 4)
    
    elif (sys.argv[1] == "1"):
        aa = station_search(l = 4)
        
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
