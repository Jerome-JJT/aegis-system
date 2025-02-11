


import os
import sys
import json
import requests
import rich
import time
from dotenv import load_dotenv

load_dotenv()

# any(e > 0 for e in [1,2,'joe'])
# all(e > 0 for e in [1,2,'joe'])

def create_discord_payload(content = {}):
    payload = {
        "username": "AEGIS",
        "embeds": [],
    }

    if (content.get('message_type') == 'embed'):
        embed = {
            "title": content["title"],
            "color": 32896, 
        }
        if (content.get("description") != None):
            embed["description"] = content.get("description")
        if (content.get("url") != None):
            embed["url"] = content.get("url")
        if (content.get("thumbnail") != None):
            embed["thumbnail"] = {
                "url": content.get("thumbnail")
            }

        if (content.get("image") != None):
            embed["image"] = {
                "url": content.get("image")
            }

        if (content.get("fields") != None):
            embed["fields"] = []
            for name, value in content.get("fields").items():
                embed["fields"].append({"name": name, "value": value})


        if (content.get("footer_text") != None or content.get("footer_icon") != None):
            embed["footer"] = {}
            if (content.get("footer_text")):
                embed["footer"]["text"] = content.get("footer_text")
            if (content.get("footer_icon")):
                embed["footer"]["icon_url"] = content.get("footer_icon")

        payload["embeds"].append(embed)

    else:
        payload["content"] = content["content"]

    return payload

def send_discord_payload(payload):
    # rich.print("Message :", msg)

    try:
        headers = {
            'Content-Type': 'application/json'
        }

        if os.getenv('DISCORD_MSGS') == None or len(os.getenv('DISCORD_MSGS')) < 20:
            raise Exception("No discord webhook url") 
    
        response = requests.post(os.getenv('DISCORD_MSGS'), data=json.dumps(payload), headers=headers)

        if response.status_code != 204:
            rich.print(f'Send error')
            raise Exception(f'Send error', response.text)

    except Exception as e:
        rich.print(f'Error {str(e)}')

def send_discord_message(payload):
    # rich.print("Message :", msg)

    try:
        payload = create_discord_payload({"content": payload})

        headers = {
            'Content-Type': 'application/json'
        }

        if os.getenv('DISCORD_MSGS') == None or len(os.getenv('DISCORD_MSGS')) < 20:
            raise Exception("No discord webhook url") 
        
        response = requests.post(os.getenv('DISCORD_MSGS'), data=json.dumps(payload), headers=headers)

        if response.status_code != 204:
            rich.print(f'Send error')
            if ("retry_after" in response.json()):
                rich.print("Wait", response.json()["retry_after"] * 3)
                time.sleep(response.json()["retry_after"] * 3)

                response = requests.post(os.getenv('DISCORD_MSGS'), data=json.dumps(payload), headers=headers)

            else:
                raise Exception(f'Send error', response.text)

    except Exception as e:
        rich.print(f'Error {str(e)}')

if __name__ == '__main__':
    if (len(sys.argv) >= 2 and sys.argv[1] == "stdin"):
         for line in sys.stdin:
            send_discord_message(line)
    else:
        send_discord_message(" ".join(sys.argv[1:]))
