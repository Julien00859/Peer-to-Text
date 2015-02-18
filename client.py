import socket

server = socket.socket()
server.connect(("localhost", 1234))

while True:
	msg = input()
	server.send(msg.encode("UTF-8"))
	if msg == "quit":
		server.close()
		break