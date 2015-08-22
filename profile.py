# -*- coding: UTF-8 -*-

from tkinter.filedialog import asksaveasfile
from uuid import uuid4
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen
import json
import os

from Crypto.PublicKey import RSA
from Crypto.Cipher import AES

class PublicProfile:
    def __init__(self, SharableProfile=None, uuid=None, pseudo=None, ips=None, public_key=None):
        if SharableProfile:
            profile = json.dumps(AES.new(b"ultra_secret_key", 3, b"this is useless.").decrypt(SharableProfile))
            self.uuid = profile["uuid"]
            self.pseudo = profile["pseudo"]
            self.ips = profile["ips"]
            self.public_key = profile["public_key"]
        else:
            self.uuid = uuid
            self.pseudo = pseudo
            self.ips = ips
            self.public_key = public_key

    def getSharableProfile(self):
        #Ce n'est pas utile de crypter l'info, c'est juste pour avoir un string qui ne dise rien à un utilisateur lambda
        return AES.new(b"ultra_secret_key", 3, b"this is useless.").encrypt(json.dumps({"uuid":self.uuid, "pseudo":self.pseudo, "ips":self.ips, "public_key":self.public_key}))

    def JSON(self):
        return json.dumps(self.array(), indent=4, sort_keys=True)

    def array(self):
        return {"uuid":self.uuid, "pseudo":self.pseudo, "ips":self.ips, "public_key":self.public_key.exportKey()}

    def __str__(self):
        return self.JSON()

class PrivateProfile(PublicProfile):
    def __init__(self, openfile="", passphrase=""):
        PublicProfile()
        if openfile != "":
            self.load(openfile, passphrase)

    def getIP(self):
        return bs(urlopen("http://whatismyip.org/"),"html.parser").span.getText()

    def save(self):
        #/profiles/Name_UUID
        for p in os.listdir(os.path.join(os.getcwd(), "profiles")):
            if p.count(self.uuid):
                os.remove(os.path.join(os.getcwd(), "profiles", p))
        with open(os.path.join(os.getcwd(), "profiles", self.pseudo + "_" + self.uuid + ".json"),"w") as file:
            file.write(self.JSON())

    def load(self, file, passphrase):
        data = json.load(open(file, "r"))
        try:
            self.private_key = RSA.importKey(data["private_key"], passphrase=passphrase)
        except Exception as ex:
            print(ex)
        else:
            self.passphrase = passphrase
            self.pseudo = data["pseudo"]
            self.mail = data["mail"]
            self.contactes = data["contactes"]
            self.blacklist = data["blacklist"]
            self.uuid = data["uuid"]
            self.ips = data["ips"]
            self.projets = data["projets"]
            self.public_key = RSA.importKey(data["public_key"])

            if self.ips.count(self.getIP())==0:
                self.ips.append(self.getIP())
                self.save()

    def addUser(self, profile_array):
        user = PublicProfile(uuid=profile_array["uuid"],pseudo=profile_array["pseudo"],ips=profile_array["ips"],public_key=profile_array["public_key"])
        if profile_array["uuid"] not in self.contactes:
            self.contactes[profile_array["uuid"]] = user.array()
        self.save()

    def delUser(self, uuid):
        if uuid in self.contactes:
           del self.contactes[uuid]
        self.save()

    def blockUser(self, uuid):
        if uuid in self.contactes:
            del self.contactes[uuid]
        if uuid not in self.blacklist:
            self.blacklist.append(uuid)
        self.save()

    def unblockUser(self, uuid):
        if uuid in self.blacklist:
            del self.blacklist[uuid]
        self.save()

    def array(self):
        return {"pseudo":self.pseudo, "mail":self.mail, "contactes":self.contactes, "blacklist":self.blacklist, "uuid":self.uuid, "ips":self.ips, "projets":self.projets, "public_key":self.public_key.exportKey().decode(), "private_key":self.private_key.exportKey(passphrase=self.passphrase).decode()}
