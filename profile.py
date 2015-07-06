from urllib.request import urlopen
from bs4 import BeautifulSoup as bs
from uuid import uuid4
from tkinter.filedialog import asksaveasfile
import json

if __name__ == "__main__":
    from sys import argv
    if len(argv) > 1:
        if argv[1].endswith(".profile"):
            with open(argv[1], "r") as json_data:
                profile = json.load(json_data)
            ip = bs(urlopen("http://whatismyip.org/"), "html.parser").span.getText()
            if profile["ip"].count(ip) == 0:
                profile["ip"].append(ip)
            with open(argv[1], "w") as file:
                file.write(json.dumps(profile))
    else:
        profile = {"uuid":str(uuid4()),"ip":[bs(urlopen("http://whatismyip.org/"), "html.parser").span.getText()]}
        with asksaveasfile(mode="w", defaultextension=".profile") as file:
            file.write(json.dumps(profile))
    print(profile)
