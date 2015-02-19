import select
import socket
import threading
from getpass import getpass

class server(threading.Thread):
	def __init__(self, host, port=1234):
		threading.Thread.__init__(self)
		self.host = host
		self.port = port
		self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.server.connect((self.host, self.port))
		self.running = True

	def run(self):
		while self.running:
			try:
				NewMessage, wlist, xlist = select.select([self.server], [], [], 1)
				if len(NewMessage) > 0:
					msg = self.server.recv(1024).decode("UTF-8")
					for line in msg.split("\r\n"):
						cmd = line.split(" ")
						if len(cmd) > 1:
							if cmd[0] == "PING":
								print(msg)
								self.server.send(("PONG %i" % int(cmd[1])).encode("UTF-8"))
			except OSError:
				pass

	def stop(self):
		self.running = False
		self.server.close()

server = server("localhost", 1234)
server.start()

input()
server.stop()
