# -*- coding: UTF-8 -*-

from tkinter.filedialog import asksaveasfile
from uuid import uuid4
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen
import json
import os
from crypto import Crypto
import rsa

class PublicProfile:
    def __init__(self, SharableProfile):
        profile = json.dumps(Crypto().crypt(SharableProfile, "super_secret_key"))
        self.uuid = profile["uuid"]
        self.pseudo = profile["pseudo"]
        self.ips = profile["ips"]
        self.public_key = profile["public_key"]

    def new(self, uuid, pseudo, ips, public_key):
        self.uuid = uuid
        self.pseudo = pseudo
        self.ips = ips
        self.public_key = public_key

    def getSharableProfile(self):
        #Ce n'est pas utile de crypter l'info, c'est juste pour avoir un string qui ne dise rien à un utilisateur lambda
        return Crypto().crypt(json.dumps({"uuid":self.uuid, "pseudo":self.pseudo, "ips":self.ips, "public_key":self.public_key}), "super_secret_key")

    def getPublicKey(self):
        n, e = self.public_key[public_str.find("(")+1:public_str.find(")")].split(", ")
        return rsa.PublicKey(int(n), int(e))

    def JSON(self):
        return json.dumps(self.array(), indent=4, sort_keys=True)

    def array(self):
        return {"uuid":self.uuid, "pseudo":self.pseudo, "ips":self.ips, "public_key":self.public_key}

    def __str__(self):
        return self.JSON()

class PrivateProfile(PublicProfile):
    def __init__(self, openfile=""):
        PublicProfile.new(self, None, None, None, None)
        if openfile != "":
            self.load(openfile)

    def new(self, pseudo="", mail="", contactes={}, blacklist=[], projets={}):
        self.pseudo = pseudo
        self.mail = mail
        self.contactes = contactes
        self.blacklist = blacklist
        self.projets = projets
        self.ips = [self.getIP()]
        self.newUUID(save=False)
        self.newRASKey(save=False)
        self.save()

    def newUUID(self, save=True):
        self.uuid = str(uuid4())
        if save:
            self.save()

    def newRASKey(self, save=True):
        public_key, private_key = rsa.newkeys(512)
        self.public_key = str(public_key)
        self.private_key = str(private_key)
        if save:
            self.save()

    def getIP(self):
        return bs(urlopen("http://whatismyip.org/"),"html.parser").span.getText()

    def save(self):
        #/profiles/Name_UUID
        for p in os.listdir(os.path.join(os.getcwd(), "profiles")):
            if p.count(self.uuid):
                os.remove(os.path.join(os.getcwd(), "profiles", p))
        with open(os.path.join(os.getcwd(), "profiles", self.pseudo + "_" + self.uuid + ".json"),"w") as file:
            file.write(self.JSON())
        
    def load(self, file):
        with open(file, "r") as json_data:
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
        user = PublicProfile(uuid=data["uuid"],pseudo=data["pseudo"],ips=data["ips"],public_key=data["public_key"])
        self.contactes[data["uuid"]] = user.array()
        self.save()

    def delUser(self, uuid):
        if uuid in self.contactes:
           del self.contactes[uuid]
        self.save()

    def blockUser(self, uuid):
        if uuid in self.contactes:
            del self.contactes[uuid]
        self.blacklist.append(uuid)
        self.save()

    def unblockUser(self, uuid):
        if uuid in self.blacklist:
            del self.blacklist[uuid]
        self.save()

    def getPrivateKey(self):
        n, e, d, p, q = self.private_key[self.private_key.find("(")+1:self.private_key.find(")")].split(", ")
        return rsa.PrivateKey(int(n), int(e), int(d), int(p), int(q))

    def array(self):
        return {"pseudo":self.pseudo, "mail":self.mail, "contactes":self.contactes, "blacklist":self.blacklist, "uuid":self.uuid, "ips":self.ips, "projets":self.projets, "public_key":self.public_key, "private_key":self.private_key}
