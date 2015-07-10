from tkinter.filedialog import asksaveasfile
from uuid import uuid4
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen
import json
from os import getcwd
from crypto import Crypto
from BeautifulJSON import BeautifulJSON

class PublicProfile:
    def __init__(self, uuid, ips):
        self.uuid = uuid
        self.ips = ips

    def getSharableProfile(self):
        #Ce n'est pas utile de crypter l'info, c'est juste pour avoir un string qui ne dise rien à un utilisateur lambda
        return Crypto().crypt(self.JSON(), "mega_secret_key")

    def JSON(self):
        return json.dumps(self.array())

    def array(self):
        return {"uuid":self.uuid, "ips":self.ips}

class PrivateProfile(PublicProfile):
    def __init__(self, openfile=""):
        PublicProfile.__init__(self, None, None)
        if openfile != "":
            self.load(openfile)

    def new(self, pseudo="", mail="", statut="", contactes={}, blacklist=[], projets={}):
        self.pseudo = pseudo
        self.mail = mail
        self.statut = statut
        self.contactes = contactes
        self.blacklist = blacklist
        self.projets = projets
        self.ips = [self.getIP()]
        self.newUUID()

    def newUUID(self):
        self.uuid = str(uuid4())

    def getIP(self):
        return bs(urlopen("http://whatismyip.org/"),"html.parser").span.getText()

    def save(self):
        #/profiles/Name_UUID
        with open(getcwd() + "/profiles/" + self.pseudo + "_" + self.uuid,"w") as file:
            file.write(BeautifulJSON(self.JSON()))
        
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
                        
        if self.ips.count(self.getIP())==0:
            self.ips.append(self.getIP())

    def addUser(self, SharableProfile):
        data = json.loads(Crypto().crypt(SharableProfile, "mega_secret_key"))
        user = PublicProfile(uuid=data["uuid"],ips=data["ips"])
        self.contactes[data["uuid"]] = user.array()

    def delUser(self, uuid):
        del self.contactes[uuid]

    def array(self):
        return {"pseudo":self.pseudo, "mail":self.mail, "contactes":self.contactes, "blacklist":self.blacklist, "uuid":self.uuid, "ips":self.ips, "projets":self.projets}
