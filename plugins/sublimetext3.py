import sublime, sublime_plugin
import socket
from threading import Thread
import os.path
import json

class P2T(sublime_plugin.EventListener):
    def __init__(self):
        print("Initialisé")
        self.server = server_class()
        self.server.start()
        self.length = -1

    def on_activated(self, view):
        self.length = view.size()
        try:
            print("Activé:", os.path.split(view.file_name())[-1])
        except:
            pass

    def on_modified(self, view):
        for region in view.sel():
            print("Type: {}, File: {}, Begin: {} {}, End: {} {}, Length: {}, Text: {}".format("+" if self.length < view.size() else "-", os.path.split(view.file_name())[-1], region.begin(), view.rowcol(region.begin()), region.end(), view.rowcol(region.end()), region.size(), view.substr(region if region.size() > 0 else region.begin()-1)))
            msg = {}
            msg["command"] = "write" if self.length < view.size() else "erase"
            msg["pos"] = view.rowcol(region.begin()-1) if msg["command"] == "write" else view.rowcol(region.begin())
            msg["msg"] = view.substr(region if region.size() > 0 else region.begin()-1)
            msg["length"] = 1
            msg["file"] = os.path.split(view.file_name())[-1]
            self.server.send(msg)
            self.length = view.size()

class server_class(Thread):
    def __init__(self):
        self.server = socket.socket()
        self.server.connect(("localhost", 48256))
        Thread.__init__(self)

    def run(self):
        self.running = True
        while self.running:
            msg = self.server.recv(1024)
            if not msg:
                self.running = False
        self.server.close()
        print("Fermé")

    def send(self, msgdict):
        self.server.send("{}\r\n".format(json.dumps(msgdict)).encode())
        print("Sent:", json.dumps(msgdict))

    def stop(self):
        self.server.close()