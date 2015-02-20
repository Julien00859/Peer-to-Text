import select
import socket
import time
from random import randrange

def ping(socket):
	"""On envoit une requête Ping à socket, cette requête contient:
	1) Un nombre aléatoire compris entre 0 et 10.000 que le client devra retourner
	2) L'heure à laquel la requête a été envoyé
	Le nombre ainsi que l'heure sont retournés et seront stoqués dans clients[socket]["time"]
	Lorsque que le socket pingué renvoit un Pong, on vérifie que le nombre envoyé est bien le nombre stocké,
	ensuite on défini la valeur du nombre alatoire sur -1 afin qu'on sache qu'il a été pingué."""
	PingRND = randrange(10000)
	PingTime = time.time()
	socket.send(("PING %i %d" % (PingRND, PingTime)).encode("UTF-8"))
	return (PingRND, PingTime)

def kick(socket, msg):
	"""On supprime le socket donné de la mapping et on le ferme."""
	print(msg)
	del clients[socket]
	try:
		socket.close()
	except:
		pass


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("localhost",1234))
server.listen(5)

#Mapping client
clients = {}
#clients[socket] = {}
#clients[socket]["ping"] = (PingRND, PingTime)
#clients[socket]["pong"] = []


#Boucle principale
running = True
while running:

	#On select le socket server pour voir s'il y a des nouveau clients
	newClients, wlist, xlist = select.select([server], [], [], 0.1)
	for client in newClients:
		#Pour chaque nouveau client, on l'accepte, on le sauvegarde dans la mapping et on le ping.
		socket, adress = server.accept()
		clients[socket] = {}
		clients[socket]["ping"] = ping(socket)

	#On select cette fois-ci la liste complete des clients (s'il y en a) pour voir s'ils ont qqch à nous dire
	if len(clients.keys()) > 0:
		newMessages, wlist, xlist = select.select(clients.keys(), [], [], 0.5)
		if len(newMessages) > 0:
			for client in newMessages:

				#On reçoit le message et on le parse pour en faire qqch. Si la connexion a été interrompu
				#d'une manière fortuite, le supprime le client de la mapping
				try:
					msg = client.recv(1024).decode("UTF-8")
				except ConnectionAbortedError:
					kick(client, "Connection Aborted")
				else:

					#Pour chaque ligne du message, on va spliter la ligne pour avoir une liste comme ceci: ["PONG",12485]
					for line in msg.split("\r\n"):
						cmd = line.split(" ")

						"""La discution avec le client se fait ici cmd[0] contient la commande envoyée par le client,
						ce qui suit sont des arguments. Pour suivre l'exemple de IRC, les commandes sont en majuscule"""

						#Réponse à une requête Ping. Doit avoir en argument 1 le même nombre que PingRND (cf Ping())
						if cmd[0] == "PONG":
							#Une exception est levée si:
							# 1) L'assert fail: le nombre retourné n'est pas le même que le nombre stocké
							# 2) Le convertion str > int a fail
							# 3) L'argument n°1 n'existe pas
							try:
								assert clients[client]["ping"][0] == int(cmd[1])
								print("Pong !")
								clients[client]["ping"] = (-1, time.time())

							except:
								kick(client, "Pong Error")



	"""Ping Checkout"""
	timeNow = time.time() 	#On sauvegarde une valeur de time pour ne pas à avoir toujours la recalculer
	#On crée une liste temporaire qui contiendra le nom des socket afin de pouvoir modifier clients.keys()
	clientsList = []
	for client in clients.keys():
		clientsList.append(client)

	#Chaque client aura soit un PingRND d'une valeur supérieur à 0, ce qui signifie qu'il est en train de se faire ping)
	#Soit un PingRND de valeur -1, ce qui signifie qu'il s'est fait ping ces 30 dernières secondes.
	# 1° cas: Si après 30 secondes aucun pong n'est arrivé, on kick le client
	# 2° cas: Après 30 secondes, on re-ping le client
	for client in clientsList:
		if clients[client]["ping"][0] != -1: #Cas n°1
			if timeNow - clients[client]["ping"][1] > 30:
				#La connexion a expiré
				kick(client, "Ping Timeout")
		else: #Cas n°1
			if timeNow - clients[client]["ping"][1] > 30:
				clients[client]["ping"] = ping(client) #Si il y a eu 30 secondes depuis le dernier ping, on ping de nouveau
	del clientsList #J'avais dis que c'était temporaire :p
	"""End of Ping Checkout"""
			