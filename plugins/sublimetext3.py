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
        self.sel = -1
        self.b = False
        self.curseurs = []

    def on_activated(self, view):
        self.length = view.size()
        try:
            print("Activé:", os.path.split(view.file_name())[-1])
        except:
            pass

    def on_selection_modified(self, view):
        self.curseurs = []
        for curseur in view.sel():
            print("Curseur:", curseur.begin(), curseur.end(), curseur.end()-curseur.begin())
            self.curseurs.append(curseur)

    def on_modified(self, view):
        curseurs = self.curseurs if self.curseurs else view.sel()
        for region in curseurs:
            try:
                msg = {}
                msg["command"] = "write" if self.length < view.size() else "erase"
                msg["pos"] = view.rowcol(region.begin() + (0 if msg["command"]=="write" or region.size()>0 else -1))
                if msg["command"] == "write":
                    msg["msg"] = view.substr(sublime.Region(view.text_point(msg["pos"][0], msg["pos"][1]), region.end()+1))
                else:
                    msg["length"] = region.size() if region.size()>0 else 1
                msg["file"] = os.path.split(view.file_name())[-1]
                
                print("Type: {}, File: {}, Position: {}, Length: {}, Text: {}".format(msg["command"], msg["file"], msg["pos"], msg["length"] if "length" in msg else None, msg["msg"] if "msg" in msg else None))
                self.server.send(msg)
                self.length = view.size()
            except Exception as ex:
                print(ex)


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