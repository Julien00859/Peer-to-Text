from tkinter.filedialog import asksaveasfile
from uuid import uuid4
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen
import json
from os import getcwd
import crypto
from BeautifulJSON import BeautifulJSON

class Profile:
    def __init__(self):
        pass

    def new(self, pseudo="", mail="", statut="", contactes={}, blacklist=[], uuid=str(uuid4()), ips=[bs(urlopen("http://whatismyip.org/"),"html.parser").span.getText()], projets={}, *args, **gwargs):
        self.pseudo = pseudo
        self.mail = mail
        self.statut = statut
        self.contactes = contactes
        self.blacklist = blacklist
        self.uuid = uuid
        self.ips = ips
        self.projets = projets

    def newUUID(self):
        self.uuid = str(uuid4)

    def getIP(self):
        ip = bs(urlopen("http://whatismyip.org/"),"html.parser").span.getText()
        if self.ips.count(ip) == 0:
            self.ips.append(ip)

    def save(self):
        with asksaveasfile(title="Save Profile", defaultextension=".profile", initialdir=getcwd()+"/profiles/", initialfile=self.pseudo) as file:
            file.write(BeautifulJSON(self.JSON()).replace(" ",""))
        
    def load(self, file):
        with open(getcwd() + "/profiles/" + file, "r") as json_data:
            data = json.load(json_data)
        self.pseudo = data["pseudo"]
        self.mail = data["mail"]
        self.contactes = data["contactes"]
        self.blacklist = data["blacklist"]
        self.uuid = data["uuid"]
        self.ips = data["ips"]
        self.projets = data["projets"]

    def getSharableProfile(self):
        return crypto.Crypto().crypt(json.dumps({"uuid":self.uuid,"ips":self.ips}), "secret_key")

    def addUser(self, SharableProfile):
        data = json.loads(crypto.Crypto().crypt(SharableProfile, "secret_key"))
        user = Profile()
        user.new(uuid=data["uuid"],ips=data["ips"])
        self.contactes[data["uuid"]] = user.array()

    def JSON(self):
        return json.dumps(self.array())

    def array(self):
        return {"pseudo":self.pseudo, "mail":self.mail, "contactes":self.contactes, "blacklist":self.blacklist, "uuid":self.uuid, "ips":self.ips, "projets":self.projets}
        