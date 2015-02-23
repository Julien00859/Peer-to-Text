import select
import socket
import time
import json
import hashlib
from threading import Thread
from random import randrange

def log(msg, status="INFO", doIprint=True, doIsave=True):
	"""msg = message to log; file = file where put the message; status = string that will be between []"""
	mytime = time.strftime("%d/%m/%y %H:%M:%S")
	message = mytime + " [" + str(status) + "] " + str(msg)
	if doIprint:
		print(message)

	if doIsave:
		with open("log.txt", "a") as f:
			f.write(message + "\r\n")
	return message

class Server(Thread):
	def __init__(self, host, port, listen=None):
		"""Initiation du serveur sur host et écoute sur port.

		host: (str) l'adresse sur laquel le socket sera initialisé.

		port: (int) le port sur lequel le socket écoutera

		listen: (int) le nombre de socket à écouter simultanément. Valeur par défault mise sur 5"""

		self.host = host
		self.port = port
		if listen!=None: self.listen=listen
		else: self.listen = 5

		self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.server.bind((self.host, self.port))
		self.server.listen(self.listen)
		Thread.__init__(self) 

	def run(self):
		"""Boucle principale d'écoute sur le serveur initialisé

		run: (bool) permet de stopper la boucle principale lorsque mis sur false

		clients: (dict) mapping contenant la liste des socket-client en key et leurs infos en value"""

		self.run = True
		self.clients = {}

		#Boucle principale, les grosses méthode seront dans des fonctions afin d'y apporter une docstring approprié
		while self.run:

			#Acceptation des nouveaux clients
			newClients, wlist, xlist = select.select([self.server], [], [], 0.1)
			for client in newClients:
				socket, adress = self.server.accept()
				log("[+] %s" % adress[0])
				self.clients[socket] = {}
				self.clients[socket]["IP"] = adress[0]
				self.clients[socket]["authentificated"] = False
				self.clients[socket]["ping"] = self.ping(socket)

			#Écoute les clients ayant qqch à dire
			if len(self.clients.keys()) > 0:
				newMessages, wlist, xlist = select.select(self.clients.keys(), [], [], 0.5)
				if len(newMessages) > 0:
					for client in newMessages:

						try:
							msg = client.recv(1024).decode("UTF-8")
						except ConnectionAbortedError:
							kick(client, "Connection Aborted")
						else:
							for line in msg.split("\r\n"):
								cmd = line.split(" ")
								log(" ".join([cmd[x] for x in range(1, len(cmd))]), status=cmd[0])

								if cmd[0] == "PONG":
									self.pong(client, cmd)

								if cmd[0] == "AUTH":
									self.auth(client, cmd)

				#Ping check
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
							self.clients[client]["ping"] = self.ping(client)
				del tempClientsList

	def pong(self, sender, cmd):
		"""Commande PONG met la valeur PingRND sur -1 et le PingTime sur l'heure actuelle

		sender: le socket qui a envoyé la commande

		cmd[]: La liste contenant l'ensemble des mots de la commande

		cmd[0]: La commande PONG

		cmd[1]: Le nombre aléatoire envoyé par ping que l'utilisateur a du réenvoyer

		PingRND: Mis sur -1 que le PingCheck() ne kick pas l'utilisateur

		PingTime: Mis sur l'heure actuelle afin de permettre à PingCheck() de réenvoyer une requête PING d'ici 30 secondes"""

		try:
			assert self.clients[sender]["ping"][0] == int(cmd[1])
		except (AssertionError, IndexError, ValueError, TypeError):
			self.kick(sender, "Pong Failed")
		else:
			self.clients[sender]["ping"] = (-1, time.time())

	def auth(self, sender, cmd):
		"""Commande AUTH permet d'authentifier le socket

		sender: le socket qui a envoyé la commande

		cmd[]: la liste contenant l'emsemble des mots de la commande

		cmd[0] la commande AUTH

		cmd[1] l'email de l'utilisateur

		cmd[2] le mot de passe hashé en SHA1 de cet utilisateur"""

		with open("config.json") as json_data:
			try:
				assert json.load(json_data)["users"][cmd[1]]["password"] == cmd[2]
				assert self.clients[sender]["authentificated"] == False
			except (AssertionError, IndexError):
				sender.send("Authentication Failed !".encode("UTF-8"))
				#hashlib.sha1((cmd[2]).encode()).hexdigest()
			else:
				self.clients[sender]["authentificated"] = True
				sender.send("Successful Authentication".encode("UTF-8"))

	def mapping(self, socket=None):
		"""Simple méthode qui affiche toute la mapping d'un client donné ou tout le monde si personne n'a été donné

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
				"IP": str() #Servant d'altérnative à username
			}
		}
		"""
		if socket==None: return self.clients
		else: return self.clients[socket]

	def ping(self, socket):
		"""Envoie une requête Ping au socket donné et enregistre des infos dans la mapping clients

		PingRND: Un nombre aléatoire compris entre 10k et 100k envoyé au socket et que celui-ci devra retourner

		PingTime: L'heure à laquel la requête a été envoyé, permet d'évaluer la vitesse (à la seconde près) et de détecter une exception PingTimeOut"""

		PingRND = randrange(10000,100000)
		PingTime = time.time()
		socket.send(("PING %i %d" % (PingRND, PingTime)).encode("UTF-8"))
		log(PingRND, status="Ping")
		return (PingRND, PingTime)

	def kick(self, socket, msg=None):
		"""Permet de fermer la connexion avec le socket donné et de le supprimer de la mapping clients

		socket: le socket à fermer

		msg: le message de kick à afficher. Default: Kicked"""

		if msg==None: msg="Kicked"
		log("Kicking %s for %s !" % (self.clients[socket]["IP"], msg), status="KICK")
		socket.close()
		del self.clients[socket]

	def stop(self):
		log("Stopping Server")
		tempClientsList = []
		for client in self.clients.keys():
			tempClientsList.append(client)
		for client in tempClientsList:
			self.kick(client, "Stopping Server")
		del tempClientsList
		self.run = False

#Lancement de la classe
server = Server("localhost", 1234)
server.start()

while True:
	msg = input()
	if msg == "stop":
		server.stop()
		break
	elif msg == "info":
		print(server.mapping())
