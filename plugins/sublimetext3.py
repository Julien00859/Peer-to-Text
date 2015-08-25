import sublime, sublime_plugin
import socket
from threading import Thread

class P2T(sublime_plugin.EventListener):
    def __init__(self):
        print("Initialisé")
        server = server_class()

    def on_modified(self, view):
        for region in view.sel():
            if region.size() == 0:
                print(view.substr())

class server_class(Thread):
    def __init__(self):
        self.server = socket.socket()
        self.server.connect(("localhost", 12345))
        self.server.listen(1)
        Thread.__init__(self)
