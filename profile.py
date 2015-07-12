from tkinter.filedialog import asksaveasfile
from uuid import uuid4
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen
import json
from os import getcwd
from crypto import Crypto
import rsa
from BeautifulJSON import BeautifulJSON

class PublicProfile:
    def __init__(self, SharableProfile):
        profile = json.dumps(Crypto().crypt(SharableProfile, "super_secret_key"))
        self.uuid = profile["uuid"]
        self.ips = profile["ips"]
        self.public_key = profile["public_key"]

    def new(self, uuid, ips, public_key):
        self.uuid = uuid
        self.ips = ips
        self.public_key = public_key

    def getSharableProfile(self):
        #Ce n'est pas utile de crypter l'info, c'est juste pour avoir un string qui ne dise rien à un utilisateur lambda
        return Crypto().crypt(json.dumps({"uuid":self.uuid, "ips":self.ips, "public_key":self.public_key}), "super_secret_key")

    def getPublicKey(self):
        n, e = self.public_key[public_str.find("(")+1:public_str.find(")")].split(", ")
        return rsa.PublicKey(int(n), int(e))

    def JSON(self):
        return json.dumps(self.array())

    def array(self):
        return {"uuid":self.uuid, "ips":self.ips, "public_key":self.public_key}

    def __str__(self):
        return self.JSON()

class PrivateProfile(PublicProfile):
    def __init__(self, openfile=""):
        PublicProfile.new(self, None, None, None)
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
        self.newRASKey()
        self.save()

    def newUUID(self):
        self.uuid = str(uuid4())
        self.save()

    def newRASKey(self):
        public_key, private_key = rsa.newkeys(512)
        self.public_key = str(public_key)
        self.private_key = str(private_key)
        self.save()

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
            self.private_key = data["private_key"]
            self.public_key = data["public_key"]
                        
        if self.ips.count(self.getIP())==0:
            self.ips.append(self.getIP())
            self.save()

    def addUser(self, SharableProfile):
        data = json.loads(Crypto().crypt(SharableProfile, "super_secret_key"))
        user = PublicProfile(uuid=data["uuid"],ips=data["ips"],public_key=data["public_key"])
        self.contactes[data["uuid"]] = user.array()
        self.save()

    def delUser(self, uuid):
        del self.contactes[uuid]
        self.save()

    def getPrivateKey(self):
        n, e, d, p, q = self.private_key[self.private_key.find("(")+1:self.private_key.find(")")].split(", ")
        return rsa.PrivateKey(int(n), int(e), int(d), int(p), int(q))

    def array(self):
        return {"pseudo":self.pseudo, "mail":self.mail, "contactes":self.contactes, "blacklist":self.blacklist, "uuid":self.uuid, "ips":self.ips, "projets":self.projets, "public_key":self.public_key, "private_key":self.private_key}
