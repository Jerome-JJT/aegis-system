import math
import datetime
from dateutil import parser

def pluralize(number, singular="", plural="s"):
    if number == 1:
        return singular
    else:
        return plural

def discord_time(time):
    timest = round(datetime.datetime.timestamp(parser.parse(time)))
    return f"<t:{timest}:T>"


def cardinalinator(patan):
    r = ""
    
    if (math.fabs(patan) > (math.pi / 8) * 5):
        r += "S"
    elif (math.fabs(patan) < (math.pi / 8) * 3):
        r += "N"
        
    if (patan < 0 - (math.pi / 8) and patan > -math.pi + (math.pi / 8)):
        r += "W"
    elif (patan > 0 + (math.pi / 8) and patan < math.pi - (math.pi / 8)):
        r += "E"
    
    return r

def cardinalinatorv1(patan):
    r = ""
    
    if (math.fabs(patan) > math.pi / 2):
        r += "S"
    else:
        r += "N"
        
    if (patan < 0):
        r += "W"
    else:
        r += "E"
    
    return r