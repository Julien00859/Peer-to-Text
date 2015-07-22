from profile import *
import json
import os
import rsa
from select import select
import socket
import sys
import threading

class server(threading.Thread):
    def __init__(self, moi):
        """Initialise le serveur via la configuration se trouvant dans /config.json
        Prend le premier argument le PrivateProfile du client local"""
        with open("config.json","r") as json_data:
            data = json.load(json_data)
            if data["output"] == "sys.stdout":
                self.output = sys.stdout
            else:
                self.output = data["output"]
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.bind((data["host"], data["port"])) #localhost:12345
            self.server.listen(5)
            print("Serveur listening on {}:{}".format(data["host"], data["port"]), file=self.output)

        self.socketlist = list() #Liste des sockets (pour select)
        self.clients = dict() #mapping des clients
        self.moi = moi #Objet PrivateProfile
        threading.Thread.__init__(self)

    def getUUID(self, socket):
        """Retourne l'UUID du socket donnné, si aucun UUID n'est trouvé, on retourne None"""
        for uuid in self.clients:
            if "socket" in uuid:
                for sock in self.clients[uuid]["socket"].keys():
                    if socket == sock:
                        return self.clients[uuid]["uuid"]
        else:
            return None

    def connect(self, uuid):
        """Essais d'établir une connexion avec un uuid sur le réseau. Pour se faire, on
        tente d'établir une connexion avec toutes les IPs enregistrées dans la liste des
        ips du contacte."""
        self.clients[uuid] = {}
        self.clients[uuid]["profile"] = PublicProfile().new(self.moi.contactes[uuid])
        port = json.dumps(open("config.json","r").read())["port"]

        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        for ip in self.clients[uuid]["profile"].ips:
            try:
                client.connect((ip, port))
            except:
                pass
            else:
                self.socketlist.append(client)
                client.send(json.dumps({"command":"profile","profile":self.moi.getSharableProfile()}).encode("UTF-8"))
                self.clients[uuid]["socket"] = {client:{"AuthMe":False, "AuthHim":False, "RSA-Pass":os.urandom(32), "ProfileSent":True}}
        else:
            pass

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
                client, client_info = server.accept()
                print("New client:", client_info)
                self.socketlist.append(client)

            if self.socketlist:
                #listen for news messages and deals each message.
                new_message, rlist, xlist = select(self.socketlist, [], [], 0.1)
                if new_message:
                    for client in new_message:
                        try:
                            #Convert the message sent in json to a map
                            msg = json.loads(client.recv(1024).decode("UTF-8"))
                            assert "command" in msg
                            #Try to get the UUID for the socket that have sent the message
                            uuid = getUUID(client)
                            print("Message from {} ({}):\n{}".format(client, uuid, msg), file=self.output)
                            
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
                                            self.clients[profile.uuid]["socket"] = {client:{"AuthMe":False, "AuthHim":False, "RSA-Pass":os.urandom(32), "ProfileSent":False}} 
                                        else:
                                            #Profile déjà connecté
                                            self.clients[profile.uuid]["socket"][client] = {"AuthMe":False, "AuthHim":False, "RSA-Pass":os.urandom(32), "ProfileSent":False}
                                        client.send(json.dumps({"command":"RSA-Auth-Send","Auth-Pass":rsa.encrypt(self.clients[profile.uuid]["socket"][client]["RSA-Pass"], self.moi.contactes[profile.uuid]["public_key"])}).encode("UTF-8"))


                                    elif profile.uuid in profile.moi.blacklist:
                                        #Profile blacklisté
                                        client.close() #Oui ceci est bourrin

                                    else:
                                        #Profile inconnu
                                        if input("{} ({}) vous a ajouté à sa liste d'amis, accepter la connexion ? Oui/Non".format(profile.pseudo, profile.uuid)).lower().startswith("o"):
                                            self.moi.addUser(msg["profile"])
                                            self.clients[profile.uuid] = {}
                                            self.clients[profile.uuid]["profile"] = profile
                                            self.clients[profile.uuid]["socket"] = {client:{"AuthMe":False, "AuthHim":False, "RSA-Pass":os.urandom(32), "ProfileSent":False}}
                                            client.send(json.dumps({"command":"RSA-Auth-Send","Auth-Pass":rsa.encrypt(self.clients[profile.uuid]["socket"][client]["RSA-Pass"], self.moi.contactes[profile.uuid]["public_key"])}).encode("UTF-8"))
                                                                
                                if msg["command"] == "RSA-Auth-Send":
                                    assert "Auth-Pass" in msg
                                    try:
                                        client.send(json.dumps({"command":"RSA-Auth-Recv","Auth-Pass":rsa.encrypt(rsa.decrypt(msg["Auth-Pass"], self.moi.private_key), self.moi.contactes[uuid]["public_key"])}).encode("UTF-8"))
                                    except:
                                        client.send(json.dumps({"command":"RSA-Auth-State","State":"Fail"}).encode("UTF-8"))

                                if msg["command"] == "RSA-Auth-Recv":
                                    assert "Auth-Pass" in msg
                                    try:
                                        assert rsa.decrypt(msg["Auth-Pass"], self.moi.private_key) == self.clients[uuid]["socket"][client]["RSA-Pass"]
                                    except:
                                        client.send(json.dumps({"command":"RSA-Auth-State","State":"Fail"}).encode("UTF-8"))
                                    else:
                                        self.clients[uuid]["socket"][client]["AuthHim"] = True
                                        client.send(json.dumps({"command":"RSA-Auth-State","State":"Success"}).encode("UTF-8"))
                                        if not self.clients[uuid]["socket"][client]["ProfileSent"]:
                                            client.send(json.dumps({"command":"profile","profile":self.moi.getSharableProfile()}).encode("UTF-8"))
                                            self.clients[uuid]["socket"][client]["ProfileSent"] = True

                                            #Mise à jour du profil local
                                            if self.clients[uuid]["profile"].pseudo != self.moi.contacte[uuid].pseudo:
                                                self.clients[uuid]["profile"].pseudo = self.moi.contacte[uuid].pseudo
                                            for ip in self.clients[uuid]["profile"].ips:
                                                if not self.moi.contacte[uuid].ips.contains(ip):
                                                    self.moi.contacte[uuid].ips.append(ip)
                                                    self.moi.save()

                                if msg["command"] == "RSA-Auth-State":
                                    assert "State" in msg
                                    if msg["State"] == "Success":
                                        self.clients[uuid]["socket"][client]["AuthMe"] = True
                            else:
                                pass
                                #Authentifié
                        except Exception as ex:
                            print(ex)

        self.server.close()
        print("Server Stopped", file=self.output)
