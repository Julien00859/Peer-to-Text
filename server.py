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
        with open("config.json","r") as json_data:
            data = json.load(json_data)
            if data["output"] == "sys.stdout":
                self.output = sys.stdout
            else:
                self.output = data["output"]
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.bind((data["host"], data["port"])) #localhost:12345
            print("Serveur listening on {}:{}".format(data["host"], data["port"]), file=self.output)
            self.server.listen(5)

        self.socketlist = list()
        self.clients = dict()
        self.running = True
        self.moi = moi #Moi correspond à un objet PrivateProfile
        threading.Thread.__init__(self)

    def getUUID(self, socket):
        for uuid in self.clients:
            if "socket" in uuid:
                for sock in self.clients[uuid]["socket"].keys():
                    if socket == sock:
                        return self.clients[uuid]["uuid"]
        else:
            return None

    def connect(self, uuid):
        self.clients[uuid] = {}
        self.clients[uuid]["profile"] = PublicProfile().new(self.moi.contactes[uuid])

        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        for ip in self.clients[uuid]["profile"].ips:
            try:
                client.connect((ip, 12345))
            except:
                pass
            else:
                self.socketlist.append(client)
                client.send(json.dumps({"command":"profile","profile":self.moi.getSharableProfile()}).encode("UTF-8"))
                self.clients[uuid]["socket"] = {client:{"AuthMe":False, "AuthHim":False, "RSA-Pass":os.urandom(32), "ProfileSent":True}}
                break
        else:
            pass

    def stop(self):
        print("Stopping Server", file=self.output)
        self.running = False

    def run(self):
        print("Server Loop Started", file=self.output)
        while self.running:
            new_client, rlist, xlist = select([self.server], [], [], 0.1)
            if new_client:
                client, client_info = server.accept()
                print("New client:", client_info)
                self.socketlist.append(client)

            if self.socketlist:
                new_message, rlist, xlist = select(self.socketlist, [], [], 0.1)
                if new_message:
                    for client in new_message:
                        try:
                            msg = json.loads(client.recv(1024).decode("UTF-8"))
                            assert "command" in msg
                            uuid = getUUID(client)
                            print("Message from {} ({}):\n{}".format(client, uuid, msg), file=self.output)
                            if uuid == None or client not in self.clients[uuid]["socket"] or self.clients[uuid]["socket"][client]["AuthMe"] == False or self.clients[uuid]["socket"][client]["AuthHim"] == False:
                                #Non authentifié

                                if msg["command"] == "profile":
                                    assert "profile" in msg
                                    profile = PublicProfile(msg["profile"])

                                    if profile.uuid in self.moi.contactes:
                                    	#profile connu
	                                    if profile.uuid not in self.clients:
	                                    	#profile pas encore connecté
	                                        self.clients[profile.uuid] = {}
	                                        self.clients[profile.uuid]["profile"] = profile
	                                        self.clients[profile.uuid]["socket"] = {client:{"AuthMe":False, "AuthHim":False, "RSA-Pass":os.urandom(32), "ProfileSent":False}} 
	                                    else:
	                                    	#profile déjà connecté
	                                        self.clients[profile.uuid]["socket"][client] = {"AuthMe":False, "AuthHim":False, "RSA-Pass":os.urandom(32), "ProfileSent":False}

	                                else:
	                                	#profile inconnu
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

        print("Server Loop Stopped", file=self.output)
            