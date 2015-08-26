import sublime, sublime_plugin
import socket
from threading import Thread

class P2T(sublime_plugin.EventListener):
    def __init__(self):
        print("Initialisé")
        server = server_class()

    def on_modified(self, view):
        pass

class server_class(Thread):
    def __init__(self):
        self.server = socket.socket()
        self.server.connect(("localhost", 12345))
        Thread.__init__(self)

    def run:
        self.running = True
        while self.running:
            print(self.server.recv(1024).decode())
