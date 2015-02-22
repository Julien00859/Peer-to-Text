import select
import socket
import threading
import json
import hashlib
from getpass import getpass

class server(threading.Thread):
	def __init__(self, host, port=1234):
		threading.Thread.__init__(self)
		self.host = host
		self.port = port
		self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.server.connect((self.host, self.port))

	def run(self):
		self.running = True
		while self.running:
			NewMessage, wlist, xlist = select.select([self.server], [], [], 1)
			if len(NewMessage) > 0:
				msg = self.server.recv(1024).decode("UTF-8")
				for line in msg.split("\r\n"):
					cmd = line.split(" ")
					if len(cmd) > 1:
						if cmd[0] == "PING":
							print(msg)
							self.server.send(("PONG %i" % int(cmd[1])).encode("UTF-8"))

	def stop(self):
		self.running = False

	def send(self, cmd):
		self.server.send()

with open("config.json") as json_data:
	data = json.load(json_data)

server = server(data["connection"]["host"],data["connection"]["port"])
server.start()

