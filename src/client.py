import select
import socket
from hashlib import sha1
from threading import Thread
from getpass import getpass
from time import sleep
import tkinter as tk

class Client(Thread):
    def __init__(self, host, port, textfield, file = None):
        self.host = host
        self.port = port
        self.textfield = textfield
        if file: self.file = file
        else: self.file = ""

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
                    for line in msg.split("\r\n"):
                        cmd = line.split(" ")
                        if cmd[0] == "PING":
                            self.client.send(("PONG %i" % int(cmd[1])).encode("UTF-8"))
                        elif cmd[0] == "WRITE":
                        	self.write(cmd)
                        elif cmd[0] == "KICK":
                            self.stop()
                            
        except (ConnectionAbortedError, OSError):
            print("Connexion au serveur perdu")
            self.running = False
            exit()

    def stop(self):
        self.send("QUIT")
        reply = self.client.recv(1024)
        if reply:
            print(reply.decode())
            self.running = False

    def write(self, cmd):
        #Si la longueur = 5 et que cmd[3] && cmd[4] sont vide c'est que c'est un espace ninja qui s'est glissé
        if len(cmd) == 5 and cmd[3] == "" and cmd[4] == "":
            cmd[3] = " "
        if cmd[3] == "\x08": #backspace
        	cmd[3] = ""
        	self.textfield.delete(cmd[2])
        else:
        	self.textfield.insert(cmd[2], cmd[3])


    def send(self, cmd):
        self.client.send((cmd + "\r\n").encode("UTF-8"))

def sendcommandpromt(event):
    cmd = commandprompt.get().split(" ")
    if cmd[0] == "OPEN":
        client.file = cmd[1]
    elif cmd[0] == "AUTH":
        cmd[2] = sha1(cmd[2].encode()).hexdigest()


    client.send(" ".join(cmd))
    commandprompt.delete(0, len(commandprompt.get()))

def write(event):
    if client.file != "":
        client.send("WRITE %s %s %s" % (client.file, textfield.index(tk.CURRENT), event.char))

if __name__ == '__main__':
    root = tk.Tk()
    textfield = tk.Text(root)
    textfield.bind("<Key>", write)
    commandprompt = tk.Entry(root, width=105)
    commandprompt.bind("<Return>", sendcommandpromt)
    client = Client("localhost", 12345, textfield)
    textfield.pack()
    commandprompt.pack()
    client.start()
    root.mainloop()
    client.stop()
