import select
import socket
import time
import json
import logging
from hashlib import sha1
from threading import Thread
from random import randrange

logging.getLogger().setLevel(logging.INFO)

class Server(Thread):
    def __init__(self, port, host = "0.0.0.0", listen = 5):
        """
        Initiation du serveur, mise en écoute sur l'host et le port.

        :type port: int
        :param port: Le port TCP sur lequel le serveur écoutera.

        :type host: str
        :param host: L'adresse IP v4 sur lequel le serveur écoutera. Valeur par défaut : 0.0.0.0 (Ecoute toutes les adresses IPs).

        :type listen: int
        :param listen: Le nombre de socket à écouter simultanément. Valeur par défaut : 5.
        """

        self.host = host
        self.port = port
        self.listen = listen

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.server.listen(self.listen)
        Thread.__init__(self) 

    def run(self):
        """
        Boucle principale d'écoute sur le serveur initialisé
        
        Variable :
            bool run: Permet de stopper la boucle principale lorsque mis sur false
            dict clients: Dictionnaire contenant la liste des clients. En key, nous trouvons le socket-client et en value nous trouvons un dictionnaire avec le ping, l'username, l'adresse mail, l'authentification, l'adresse Ip et les fichiers ouverts ?
        """

        self.run = True
        self.clients = {}
        self.files = {}

        # Boucle principale, les grosses méthode seront dans des fonctions afin d'y apporter une docstring approprié
        while self.run: 
            # Acceptation des nouveaux clients
            newClients, wlist, xlist = select.select([self.server], [], [], 0.1)
            for client in newClients:
                socket, adress = self.server.accept()
                self.clients[socket] = {}
                self.clients[socket]["ping"] = self.ping(socket)
                self.clients[socket]["username"] = ""
                self.clients[socket]["email"] = ""
                self.clients[socket]["authentificated"] = False
                self.clients[socket]["IP"] = adress[0]
                self.clients[socket]["files"] = []

            # Écoute les clients ayant qqch à dire
            if len(self.clients.keys()) > 0:
                newMessages, wlist, xlist = select.select(self.clients.keys(), [], [], 0.5)
                if len(newMessages) > 0:
                    for client in newMessages:
						try:
                            msg = client.recv(1024).decode("UTF-8")
						except (OSError, ConnectionAbortedError):
							# Le client s'est deconnecté ou un problème est arrivé. On le kick
							kick(client)
						else:
                            for line in msg.split("\r\n"):
                                cmd = line.split(" ")
                                logging.info(" ".join(cmd))

                                if cmd[0] == "PONG":
                                    self.pong(client, cmd)
                                elif cmd[0] == "AUTH":
                                    self.auth(client, cmd)
                                elif cmd[0] == "QUIT":
                                    self.kick(client, "You have been disconnected !")

                                elif self.clients[socket]["authentificated"]:
                                    if cmd[0] == "OPEN":
                                        self.open(client, cmd)
                                    if self.clients[socket]["files"]:
                                        if cmd[0] == "WRITE":
                                            self.write(client, cmd)
                                        if cmd[0] == "SEND":
                                            # SEND <file> <len>
                                            # socket.recv(len).decode()
                                            pass
								elif cmd[0] == "OPEN" or cmd[0] == "WRITE" or cmd[0] == "SEND":
									self.clients[client].send(("ERROR %s: You must be authentificated to use this command" % cmd[0]).encode())
								else:
									self.clients[client].send(("ERROR %s: Unknown command." % cmd[0]).encode())
            # Ping check
            timeNow = time.time()
            tempClientsList = []
            for client in self.clients.keys():
                tempClientsList.append(client)

            for client in tempClientsList:
                if self.clients[client]["ping"][0] != -1:
                    if timeNow - self.clients[client]["ping"][1] > 30:
                        kick(client, "Ping Timeout")
                else:
                    if timeNow - self.clients[client]["ping"][1] > 30:
                        try:
                            self.clients[client]["ping"] = self.ping(client)
                        except ConnectionResetError:
                            self.kick(socket, "Ping Timeout")
            del tempClientsList
    def pong(self, sender, cmd):
        """
        Commande PONG met la valeur PingRND sur -1 et le PingTime sur l'heure actuelle

        PingRND: Mis sur -1 que le PingCheck() ne kick pas l'utilisateur.
        PingTime: Mis sur l'heure actuelle afin de permettre à PingCheck() de réenvoyer une requête PING d'ici 30 secondes.

        :type sender: socket
        :param sender: Le socket qui a envoyé la commande.

        :type cmd: dict
        :param cmd: Un dictionnaire contenant l'ensemble des mots de la commande. cmd[0]: La commande PONG. cmd[1]: Le nombre aléatoire envoyé par ping que l'utilisateur a du réenvoyer.
        """

        try:
            assert self.clients[sender]["ping"][0] == int(cmd[1])
        except (AssertionError, IndexError, ValueError, TypeError):
            self.kick(sender, "Pong Failed")
        else:
            self.clients[sender]["ping"] = (-1, time.time())

    def auth(self, sender, cmd):
        """
        Commande AUTH permet d'authentifier le socket

        :type sender: socket
        :param sender: Le socket qui a envoyé la commande.

        :type cmd: dict
        :param cmd: Un dictionnaire contenant l'ensemble des mots de la commande. cmd[0] la commande AUTH. cmd[1] l'email de l'utilisateur. cmd[2] le mot de passe hashé en SHA1 de cet utilisateur.
        """

        # Utilisation temporaire d'un fichier
        with open("config.json") as json_data:
            try:
                assert sha1(json.load(json_data)["users"][cmd[1]]["password"].encode()).hexdigest() == cmd[2]
            except AssertionError:
                logging.warning("Authentication Failed for %s (Wrong Password)" % cmd[1])
                sender.send("ERROR AUTH: Incorrect password".encode())
            except KeyError:
                logging.warning("Authentication Failed for %s (Incorrect mail adress)" % cmd[1])
                sender.send("ERROR AUTH: Incorrect mail adress".encode())
            except IndexError:
                logging.warning("%s miss taping command %s: %s" % (self.clients[sender]["IP"], cmd[0], " ".join(cmd)))
                sender.send("ERROR AUTH: OPEN <file>".encode())
            else:
                if not self.clients[sender]["authentificated"]:
                    self.clients[sender]["authentificated"] = True
                    logging.info("Successful Authentication for %s" % (cmd[1]))
                    sender.send("OK AUTH: Successful Authentication".encode("UTF-8"))
                else:
                    logging.warning("Authentication Failed for %s (Already Authentificated)" % (cmd[1]))
                    sender.send("Authentication Failed ! (Already Authentificated)".encode("UTF-8"))

    def open(self, sender, cmd):
        """
        Commande OPEN permet d'ouvrir un fichier.
        Le serveur enverra une commande "SEND <file> <len(file.read().encode("UTF-8")>"
        Suivi du fichier sous forme d'un classique tableau de char
        Et pour finir la liste de tous les changements depuis l'ouverture du fichier.

        :type sender: socket
        :param sender: Le socket qui a envoyé la commande.

        :type cmd: dict
        :param cmd: Un dictionnaire contenant l'ensemble des mots de la commande. cmd[0] la commande OPEN. cmd[1] le nom du fichier. ??
        """

        try:
            self.files[cmd[1]]["users"].append(sender)
        except KeyError:
            try:
                with open(cmd[1], "r") as file:
                    content = file.read()
                    sender.send(("SEND %s %i" % (cmd[1], len(content.encode("UTF-8")))).encode())
                    sender.send(content.encode("UTF-8"))
                    for change in self.files[cmd[1]]["changes"]:
                        sender.send(("WRITE %s" % change).encode("UTF-8"))
                logging.info("New file opened: %s" % cmd[1])
            except FileNotFoundError:
                with open(cmd[1], "w") as file:
                    self.files[cmd[1]] = {"users":[sender],"changes":[]}
                sender.send(("SEND %s 0" % cmd[1]).encode())
            finally:
                self.files[cmd[1]] = {"users":[sender],"changes":[]}
                self.clients[sender]["files"].append(cmd[1])
        except IndexError:
            logging.warning("%s miss taping command %s: %s" % (self.clients[sender]["IP"], cmd[0], " ".join(cmd)))
            sender.send("ERROR OPEN command: OPEN <file>".encode())

    def write(self, sender, cmd):
        """
        Commande WRITE permet d'écrire sur un fichier ouvert

        :type sender: socket
        :param sender: Le socket qui a envoyé la commande.

        :type cmd: dict
        :param cmd: Un dictionnaire contenant l'ensemble des mots de la commande. cmd[0] la commande WRITE. cmd[1] le fichier sur lequel écrire. cmd[2] l'index (de type tkinter.Text().index()). cmd[3] le message à écrire.
        """

        try:
            if self.files[cmd[1]]["users"].count(sender):
                for client in self.file[cmd[1]]["users"]:
                    if client != sender:
                        logging.debug("%s: %s" % (self.clients[sender]["IP"], " ".join(cmd)))
                        self.files[cmd[1]]["changes"].append([x for x in cmd if x >= 2])
                        client.send(cmd.encode())
            else:
                logging.warning("%s tried to write on %s" % (self.clients[sender]["IP"], cmd[1]))
                sender.send("ERROR WRITE: File must be opened first".encode())
        except IndexError:
            logging.warning("%s miss taping command %s: %s" % (self.clients[sender]["IP"], cmd[0], " ".join(cmd)))
            sender.send("ERROR WRITE command: WRITE <file> <index> <message>".encode())

    def kick(self, socket, msg = "Kicked", file = None):
        """
        Permet de fermer la connexion avec le socket donné et de le supprimer de la mapping clients

        :type sender: socket
        :param sender: Le socket à fermer

        :type msg: str
        :param msg: Le message de kick à afficher. Defaut: Kicked

        :type file: str
        :param file: Si on doit seulement kicker un user d'un fichier en particulier
        """

        if file:
            logging.warning("Kicking %s from %s for %s !" % (self.clients[socket]["IP"], file, msg))
			try:
				socket.send(("KICKED %s %s" % (file, msg)).encode("UTF-8"))
            self.files[file].remove(socket)
        else:
            logging.warning("Kicking %s for %s !" % (self.clients[socket]["IP"], msg))
			try:
				socket.send(("KICKED %s" % msg).encode("UTF-8"))
            for file in self.clients[socket]["files"]:
                self.files[file].remove(socket)
            del self.clients[socket]
            socket.close()

    def ping(self, socket):
        """
        Envoie une requête Ping au socket donné et enregistre des infos dans la mapping clients

        :type PingRND: int
        :param PingRND: Un nombre aléatoire compris entre 10k et 100k envoyé au socket et que celui-ci devra retourner

        :type PingTime: int
        :param PingTime: L'heure à laquel la requête a été envoyé, permet d'évaluer la vitesse (à la seconde près) et de détecter une exception PingTimeOut
        """

        PingRND = randrange(10000, 100000)
        PingTime = time.time()
        socket.send(("PING %i %d" % (PingRND, PingTime)).encode("UTF-8"))
        logging.debug("PING " + str(PingRND))
        return (PingRND, PingTime)

    def stop(self):
        """
        Permet d'arrêté proprement le serveur Socket
        """

        logging.warning("Stopping Server")
        tempClientsList = []
        for client in self.clients.keys():
            tempClientsList.append(client)
        for client in tempClientsList:
            self.kick(client, "Stopping Server")
        del tempClientsList
        self.run = False

    def usersMapping(self, socket = None):
        """
        Simple méthode qui affiche toute la mapping d'un client donné ou tout le monde si personne n'a été donné

        clients={ #Mapping générale
            socket={ #Un socket-client
                "ping":tulpe(
                    int(PingRND), #CF Ping()
                    int(PingTime) #CF Ping()
                ),
                "username":str(), #Le nom d'utilisateur à afficher
                "email":str(), #L'email servant lors de l'authentification
                "password": sha1(password), #Le mot de passe servant lors de l'authentification hashé en SHA1
                "authentificated": bool(), #Si le client est authentifié ou non
                "IP": str(), #Servant d'altérnative à username
                "files": list() #La liste des fichiers ouvert par le client
            }
        }
        """
        
        if socket == None:
            return self.clients
        else:
            return self.clients[socket]

    def filesMapping(self, file = None):
        """
        Simple méthode qui retourne la mapping files entière ou simplement pour le fichier donné

        files={ #Mapping générale
            fichier={ #Un fichier random
                "users":list(), #La liste des sockets lisant ce fichier
                "changes": list() #La liste des WRITE depuis l'envoie du fichier au premier client
            }
        }
        """

        if file == None:
            return self.files
        else:
            return self.files[file]

def main():
    server = Server(1234)
    server.start()
    try:
        while True:
            msg = input()
            if msg == "users":
                print(server.usersMapping())
            elif msg == "files":
                print(server.filesMapping())
            else:
                exec(msg)
    except KeyboardInterrupt:
        server.stop()

if __name__ == '__main__':
    main()
