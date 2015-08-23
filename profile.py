# -*- coding: UTF-8 -*-

from tkinter.filedialog import asksaveasfile
from urllib.request import urlopen
import json
import os

from Crypto.PublicKey import RSA

class PublicProfile:
    def __init__(self, SharableProfile=None, uuid=None, pseudo=None, ips=None, public_key=None, mail=None):

        if SharableProfile:
            SharableProfile = json.loads(SharableProfile)
            self.uuid = SharableProfile["uuid"]
            self.pseudo = SharableProfile["pseudo"]
            self.ips = SharableProfile["ips"]
            self.public_key = RSA.importKey(SharableProfile["public_key"])
            self.mail = SharableProfile["mail"]
        else:
            self.uuid = uuid
            self.pseudo = pseudo
            self.ips = ips
            self.public_key = public_key
            self.mail = mail

    def PublicJSON(self):
        return json.dumps(self.PublicArray())

    def PublicArray(self):
        return {"mail":self.mail, "uuid":self.uuid, "pseudo":self.pseudo, "ips":self.ips, "public_key":self.public_key.exportKey().decode()}

    def __str__(self):
        return self.JSON()

class PrivateProfile(PublicProfile):
    def __init__(self, openfile="", passphrase=""):
        PublicProfile()
        if openfile != "":
            self.load(openfile, passphrase)

    def getIP(self):
        return json.loads(urlopen("http://www.telize.com/geoip/").read().decode())["ip"]

    def save(self):
        #/profiles/Name_UUID
        for p in os.listdir(os.path.join(os.getcwd(), "profiles")):
            if p.count(self.uuid):
                os.remove(os.path.join(os.getcwd(), "profiles", p))
        with open(os.path.join(os.getcwd(), "profiles", self.pseudo + "_" + self.uuid + ".json"),"w") as file:
            file.write(self.PrivateJSON())

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

    def addUser(self, PublicProfile):
        user = PublicProfile(PublicProfile)
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

    def PrivateArray(self):
        return {"pseudo":self.pseudo, "mail":self.mail, "contactes":self.contactes, "blacklist":self.blacklist, "uuid":self.uuid, "ips":self.ips, "projets":self.projets, "public_key":self.public_key.exportKey().decode(), "private_key":self.private_key.exportKey(passphrase=self.passphrase).decode()}

    def PrivateJSON(self):
        return json.dumps(self.PrivateArray(), indent=4, sort_keys=True)
