# -*- coding: UTF-8 -*-

import json
import socket
import threading
import urllib.request
from time import time, sleep, strftime
from select import select
from sys import stdout

from Crypto.PublicKey import RSA
from Crypto import Random

from blackboard import *
from permissions import *
from profile import *

class server(threading.Thread):
    def __init__(self, moi):
        """Initialise le serveur via la configuration se trouvant dans /config.json
        Prend le premier argument le PrivateProfile du client local"""
        with open("config.json","r") as json_data:
            data = json.load(json_data)
            self.output = stdout if data["output"] == "sys.stdout" else open(data["output"], "a")
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.bind((data["host"], data["port"])) #localhost:12345
            self.server.listen(5)
            print("Serveur listening on {}:{}".format(data["host"], data["port"]), file=self.output)

            self.IDE = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.IDE.bind((data["IDE_host"], data["IDE_port"]))
            self.IDE.listen(1)
            print("IDE listening on {}:{}".format(data["host"], data["IDE_port"]), file=self.output)


        self.socketlist = list() #Liste des sockets (pour select)
        self.clients = dict() #Mapping des clients
        self.moi = moi #Objet PrivateProfile
        self.random = Random.new() #Un objet random pour ne pas avoir à le recréer à chaque fois
        threading.Thread.__init__(self)

    def getUUID(self, socket):
        """Retourne l'UUID du socket donnné, si aucun UUID n'est trouvé, on retourne None"""
        for uuid in self.clients:
            if "socket" in self.clients[uuid]:
                for sock in self.clients[uuid]["socket"].keys():
                    if socket == sock:
                        return uuid
        else:
            return None

    def connect(self, uuid):
        """Essais d'établir une connexion avec un uuid sur le réseau. Pour se faire, on
        tente d'établir une connexion avec toutes les IPs enregistrées dans la liste des
        ips du contacte."""
        self.clients[uuid] = {}
        self.clients[uuid]["profile"] = PublicProfile(uuid=uuid, pseudo=self.moi.contactes[uuid]["pseudo"], mail=self.moi.contactes[uuid]["mail"], ips=self.moi.contactes[uuid]["ips"], public_key=RSA.importKey(self.moi.contactes[uuid]["public_key"]))
        port = json.load(open("config.json","r"))["port"]

        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        for ip in self.clients[uuid]["profile"].ips:
            try:
                client.connect((ip, port))
            except:
                pass
            else:
                self.socketlist.append(client)
                self.send({"command":"profile","profile":self.moi.PublicJSON()})
                self.clients[uuid]["socket"] = {client:{"AuthMe":False, "AuthHim":False, "RSA-Pass":self.random.read(64), "ProfileSent":True}}
        else:
            pass

    def send(self, socket, msg):
        try:
            socket.send("{}\r\n".format(json.dumps(msg)).encode("UTF-8"))
        except Exception as ex:
            print(ex)
            self.kick(socket)

    def recv(self, socket):
        """Parse the message sent by the socket
        Convert the string recieved
            {"command":"ping"}\r\n{"command":"write"}\r\n{"command":"erase"}\r\n
        to the list
            [{"command":"ping"},{"command":"write"},{"command":"erase"}]"""

        try:
            msg = socket.recv(2048).decode("UTF-8")
        except Exception as ex:
            print(ex)
            self.kick(socket)
            return []
        else:
            r = [[]]
            bracket = 0
            find = False
            for char in msg:
                if char == "{":
                    bracket+=1
                    r[-1].append(char)
                elif char == "}":
                    bracket-=1
                    r[-1].append(char)
                elif bracket == 0 and char == "\r":
                    find = True
                elif bracket == 0 and find == True and char == "\n":
                    find = False
                    r[-1] = "".join(r[-1])
                    r.append([])
                else:
                    find = False
                    r[-1].append(char)
            return r[0:len(r)-1]

    def kick(self, socket):
        if socket in self.socketlist:
            self.socketlist.remove(socket)
        for uuid in self.clients.keys():
            if "socket" in self.clients[uuid]:
                if socket is self.clients[uuid]["socket"]:
                    del self.clients[uuid]["socket"][socket]
                    if len(self.clients[uuid]["socket"]) == 0:
                        del self.clients[uuid]

    def stop(self):
        """Stop le serveur"""
        print("Stopping Server", file=self.output)
        self.running = False

    def run(self):
        """Server main loop"""
        print("Server Loop Started", file=self.output)
        self.running = True
        while self.running:

            #Listen for news clients ans and them to the socket list
            new_client, rlist, xlist = select([self.server], [], [], 0.1)
            if new_client:
                client, client_info = self.server.accept()
                print("New client:", client_info)
                self.socketlist.append(client)

            if self.socketlist:
                #listen for news messages and deals each message.
                new_message, rlist, xlist = select(self.socketlist, [], [], 0.1)
                if new_message:
                    for client in new_message:
                        for msgjson in self.recv(client):
                            msg = json.loads(msgjson)
                            assert "command" in msg
                            uuid = self.getUUID(client) #Try to get the UUID for the socket that have sent the message
                            print("{} Message from {}: {}".format(strftime("%x-%X"), uuid if uuid else client, msg["command"]), file=self.output)

                            if msg["command"] == "pong":
                                ping = time() - msg["time"]
                                if ():
                                    pass
                            else:
                                if uuid == None or client not in self.clients[uuid]["socket"] or self.clients[uuid]["socket"][client]["AuthMe"] == False or self.clients[uuid]["socket"][client]["AuthHim"] == False:
                                    #Non authentifié

                                    if msg["command"] == "profile":
                                        assert "profile" in msg
                                        profile = PublicProfile(msg["profile"])

                                        if profile.uuid in self.moi.contactes:
                                            #Profile whitelisté
                                            if profile.uuid not in self.clients:
                                                #Profile pas encore connecté
                                                self.clients[profile.uuid] = {}
                                                self.clients[profile.uuid]["profile"] = profile
                                                self.clients[profile.uuid]["socket"] = {client:{"AuthMe":False, "AuthHim":False, "RSA-Pass":self.random.read(64), "ProfileSent":False}}
                                            elif client not in self.clients[profile.uuid]["socket"]:
                                                #Profile déjà connecté
                                                self.clients[profile.uuid]["socket"][client] = {"AuthMe":False, "AuthHim":False, "RSA-Pass":self.random.read(64), "ProfileSent":False}

                                            self.send(client, {"command":"RSA-Auth-Send","Auth-Pass":self.clients[profile.uuid]["profile"].public_key.encrypt(self.clients[profile.uuid]["socket"][client]["RSA-Pass"], self.random.read(8))[0].decode("latin-1")})

                                        elif profile.uuid in profile.moi.blacklist:
                                            #Profile blacklisté
                                            client.close() #Oui ceci est bourrin

                                        else:
                                            #Profile inconnu
                                            if input("{} ({}) vous a ajouté à sa liste d'amis, accepter la connexion ? Oui/Non".format(profile.pseudo, profile.uuid)).lower().startswith("o"):
                                                self.moi.addUser(profile.array())
                                                self.clients[profile.uuid] = {}
                                                self.clients[profile.uuid]["profile"] = profile
                                                self.clients[profile.uuid]["socket"] = {client:{"AuthMe":False, "AuthHim":False, "RSA-Pass":self.random.read(64), "ProfileSent":False}}
                                                self.send(client, {"command":"RSA-Auth-Send","Auth-Pass":self.clients[profile.uuid]["profile"].public_key.encrypt(self.clients[profile.uuid]["socket"][client]["RSA-Pass"], self.random.read(8))[0].decode("latin-1")})

                                    if msg["command"] == "RSA-Auth-Send":
                                        assert "Auth-Pass" in msg
                                        try:
                                            self.send(client, {"command":"RSA-Auth-Recv","Auth-Pass": RSA.importKey(self.moi.contactes[uuid]["public_key"]).encrypt(self.moi.private_key.decrypt(msg["Auth-Pass"].encode("latin-1")), self.random.read(8))[0].decode("latin-1")})
                                        except:
                                            self.send(client, {"command":"RSA-Auth-State","State":"Fail"})

                                    if msg["command"] == "RSA-Auth-Recv":
                                        assert "Auth-Pass" in msg
                                        try:
                                            assert self.moi.private_key.decrypt(msg["Auth-Pass"].encode("latin-1")) == self.clients[uuid]["socket"][client]["RSA-Pass"]
                                        except:
                                            self.send(client, json.dumps({"command":"RSA-Auth-State","State":"Fail"})
                                        else:
                                            self.clients[uuid]["socket"][client]["AuthHim"] = True
                                            self.send(json.dumps({"command":"RSA-Auth-State","State":"Success"})

                                            #Mise à jour du profil local
                                            if self.moi.contactes[uuid]["pseudo"] != self.clients[uuid]["profile"].pseudo:
                                                self.moi.contactes[uuid]["pseudo"] = self.clients[uuid]["profile"].pseudo
                                            if self.moi.contactes[uuid]["mail"] != self.clients[uuid]["profile"].mail:
                                                self.moi.contactes[uuid]["mail"] = self.clients[uuid]["profile"].mail
                                            for ip in self.clients[uuid]["profile"].ips:
                                                if not ip in self.moi.contactes[uuid]["ips"]:
                                                    self.moi.contactes[uuid]["ips"].append(ip)
                                                    self.moi.save()

                                            #Envois du profile si l'autentification n'en n'est qu'à la moitié
                                            if self.clients[uuid]["socket"][client]["ProfileSent"] == False:
                                                sleep(1)
                                                self.send(client, {"command":"profile","profile":self.moi.PublicJSON()})
                                                self.clients[uuid]["socket"][client]["ProfileSent"] = True

                                    if msg["command"] == "RSA-Auth-State":
                                        assert "State" in msg
                                        if msg["State"] == "Success":
                                            self.clients[uuid]["socket"][client]["AuthMe"] = True
                                else:
                                    pass

                    # for uuid in self.clients.keys():
                    #     if "socket" in self.clients[uuid]:
                    #         for socket in self.clients[uuid]["socket"].keys():
                    #             if "ping" not in self.clients[uuid]["socket"][socket]:
                    #                 self.clients[uuid]["socket"][socket]["ping"] = (0, -1) # Timestamp last ping, latence (secondes) il faut que je vois pour des ms
                    #
                    #             if (time() - self.clients[uuid]["socket"][socket]["ping"][0]) > 180:
                    #                 self.clients[uuid]["socket"][socket]["ping"] = (time(), -1)
                    #                 socket.send(json.dumps({"command":"PING","time":time()}).encode("UTF-8"))


            #Listen for news clients ans and them to the socket list
            if "IDE_client" not in self.__dict__.keys()
                IDE, rlist, xlist = select([self.IDE], [], [], 0.1)
                if IDE:
                    self.IDE_client = self.server.accept()[0]
                    print("IDE Hooked", file=self.output)

            else:
                IDE, rlist, xlist = select([self.IDE_client], [], [], 0.1)
                if IDE:
                    for IDE_message in json.loads(self.recv(IDE[0])):
                        print(IDE_message, file=self.output)


        self.server.close()
        print("Server Stopped", file=self.output)
