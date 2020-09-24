import requests
from bs4 import BeautifulSoup
import difflib
import html
import os
from time import sleep

URL = "https://www.kinzig-schule.de"
WEBHOOK_URL = os.environ.get("check.webhook_url")
Interval = os.environ.get("check.interval")

if WEBHOOK_URL == None:
    print("Webhook URL not found. (Env)")
    exit(code=1)


if Interval == None:
    print("Interval not found. (Env)")
    exit(code=1)

old_content = ""
total_check = 0


'''
Sends notifications to msteams
'''
def spread_updates(changes):
    changes_as_text = ""
    info = {"+": 0, "-": 0, "?": 0}
    num = 0
    
    for line in changes:
        line = html.escape(line)

        # Info
        if line.startswith("+"):
            info["+"] = info["+"] + 1
        if line.startswith("-"):
            info["+"] = info["-"] + 1
        if line.startswith("?"):
            info["+"] = info["?"] + 1

        num = num + 1
        if num < 220:
            changes_as_text = str(changes_as_text) + str(line) + "\n"

    info_ges = 0
    for i in info:
        info_ges = info_ges + info[i]

    changes_as_info = f"# {info_ges}: + {info['+']}, - {info['-']}, ? {info['?']}"

    data = {
        "@type": "MessageCard",
        "@context": "http://schema.org/extensions",
        "themeColor": "0076D7",
        "summary": "New Update",
        "sections": [
            {
                "activityTitle": "Neues Update",
                "activitySubtitle": f"{changes_as_info}",
                "markdown": False
            },
            {
                "text": f"<pre>{changes_as_text}</pre>"
            }
        ]
    }

    req = requests.post(WEBHOOK_URL, json=data)

'''
Checks for updates
'''
def check_page():
    global old_content

    # Read HTML
    frm = BeautifulSoup(requests.get(URL).content.decode(
        "UTF-8"), features="html.parser")
    pretty = frm.prettify()

    # Content changed:ç
    changesAsText = ""

    # Check content
    if pretty == old_content:
        old_content = pretty
        return False

    # Uncomment this later.
    if False: #old_content == "":
        print("Initial snapshot. Ignore this.")
        return True

    # Updated:
    res = difflib.unified_diff(old_content.split("\n"), pretty.split("\n"))
    old_content = pretty
    spread_updates(res)
    return True

while True:
    total_check = total_check + 1
    total_changes = 0
    print(f"Check: {total_check} | Changes: {total_changes}", end="\r")
    if check_page():
        total_changes = total_changes + 1
    sleep(Interval)
