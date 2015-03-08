import select
import socket
import json
from hashlib import sha1
from threading import Thread
from getpass import getpass
from time import sleep
import tkinther as tk

class Client(Thread):
    def __init__(self, host, port = 1234):
        self.host = host
        self.port = port

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((self.host, self.port))
        Thread.__init__(self)

    def run(self):
        self.running = True
        try:
            while self.running:
                NewMessage, wlist, xlist = select.select([self.client], [], [], 1)
                if len(NewMessage) > 0:
                    msg = self.client.recv(1024).decode("UTF-8")
                    print(msg)
                    sleep(5)
                    for line in msg.split("\r\n"):
                        cmd = line.split(" ")
                        if cmd[0] == "PING":
                            self.client.send(("PONG %i" % int(cmd[1])).encode("UTF-8"))
                        elif cmd[0] == "KICKED":
                            self.running = False
                        elif cmd[0] == "WRITE":
                        	
        except (ConnectionAbortedError, OSError):
            print("Connexion au serveur perdu")
            self.running = False

    def stop(self):
        self.send("QUIT")
        reply = self.client.recv(1024)
        if reply:
            print(reply.decode())
            self.running = False

    def send(self, cmd):
        self.client.send(cmd.encode("UTF-8"))

def IG(Thread):
	def __init__(self, socket, file):
		self.client = socket
		self.file = file
		root = tk.Tk()
		self.textfield = tk.Text(root)
		self.textfield.bind("<Key>", write)
		Thread.__init__(self)

	def write(event):
		self.client.send(("WRITE %s %s %s" % (self.file, textfield.index(tk.CURRENT), event.char)).encode())

	def run():
		self.textfield.pack()


def main():
    client = Client("localhost", 1234)
    client.start()
    ig = IG(client)
    ig.start()

    try:
        while True:
            msg = input()
            if msg == "auth":
                client.send("AUTH %s %s" % (input("Adresse E-Mail : "), sha1(getpass("Mot de passe : ").encode()).hexdigest()))
            else:
                client.send(msg)
    except KeyboardInterrupt:
        if client.running: client.stop()

if __name__ == '__main__':
    main()
