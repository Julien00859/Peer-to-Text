import socket
import select
from random import randrange

server = socket.socket()
server.bind(("localhost",1234))
server.listen(5)

clients = {}

running = True
while running:
	newClients, wlist, xlist = select.select([server], [], [], 0.5)
	for client in newClients:
		socket, adress = server.accept()
		clients[socket] = {}
		clients[socket]["name"] = clients[socket]["IP"] = adress[0]
		ping = randrange(10000)
		clients[socket]["ping"] = ping
		socket.send(("PING %i" % ping).encode("UTF-8"))

		print("[+] {}".format(adress[0]))

	if len(clients.keys()) > 0:
		newMessages, wlist, xlist = select.select(clients.keys(), [], [], 0.5)
		if len(newMessages) > 0:
			for client in newMessages:
				msg = client.recv(1024).decode("UTF-8")
				for line in msg.split("\n"):
					word = line.split(" ")

					if len(word) > 1:
						if word[0] == "PONG":
							print("%s PONG %i" % (clients[client]["name"], int(word[1])))
							assert int(word[1]) == clients[client]["ping"]