#Import
import select
import socket
import threading
import time
from random import randrange

def ping(socket):
	PingRND = randrange(10000)
	PingTime = time.time()
	socket.send(("PING %i %d" % (PingRND, PingTime)).encode("UTF-8"))
	return (PingRND, PingTime)

def kick(socket):
	print("Kicked")
	del clients[socket]
	socket.close()


#Server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("localhost",1234))
server.listen(5)

#Clients mapping
clients = {}
#clients[socket] = {}
#clients[socket]["ping"] = (PingRND, PingTime)


#Main loop
running = True
while running:

	#Look for news clients
	newClients, wlist, xlist = select.select([server], [], [], 0.1)
	for client in newClients:
		socket, adress = server.accept()
		clients[socket] = {}
		clients[socket]["ping"] = ping(socket)

	if len(clients.keys()) > 0:
		#Looking for new messages
		newMessages, wlist, xlist = select.select(clients.keys(), [], [], 0.5)
		if len(newMessages) > 0:
			for client in newMessages:

				#Receive the message and parse it to do things
				try:
					msg = client.recv(1024).decode("UTF-8")
				except ConnectionAbortedError:
					print("Connection lost")
					del clients[client]
				else:
					for line in msg.split("\r\n"):
						cmd = line.split(" ")
						if cmd[0] == "PONG":
							#Execpt if int() fail or if there is no cmd[1]
							try:
								assert clients[client]["ping"][0] == int(cmd[1])
								print("Pong !")
								clients[client]["ping"] = (-1, time.time())
							except:
								print("Pong Error")
								kick(client)

	#Ping command
	timeNow = time.time()
	for client in clients.keys():
		if clients[client]["ping"][0] != -1:
			if timeNow - clients[client]["ping"][1] > 30:
				#La connexion a expiré
				print("Ping timeout !")
				#kick(client)
		else:
			#Si le PingRND vaut -1 c'est que le client a réussi un précédent ping
			if timeNow - clients[client]["ping"][1] > 30:
				#Si il y a eu 30 secondes depuis le dernier ping, on ping de nouveau
				clients[client]["ping"] = ping(client)
			