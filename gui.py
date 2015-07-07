import tkinter as tk
import json
import sys
import os
from time import sleep

class GUI(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.grid()
        self.navbar()
        
        tk.Label(self, text="Profiles").grid(row=2,column=1)
        self.Profile = tk.Listbox(self, selectmode="SINGLE")
        for file in os.listdir(os.getcwd() + "\\profiles\\"):
            if file.endswith(".profile"):
                self.Profile.insert(tk.END, file[:file.find(".")])
        self.Profile["heigh"] = len(self.Profile.get(0, tk.END))
        self.Profile.grid(row=3,column=1)
        self.Profile.bind("<Key>", self.updateProfileSelection)
        self.Profile.bind("<Button>", self.updateProfileSelection)
                
        self.showAccueil(None)

    def updateProfileSelection(self, event):
        if self.Profile.get(self.Profile.curselection())[0]:
            if tk.messagebox.askyesno(title="Are you sure ?", message="Are you sure to select the profile " + self.Profile.get(self.Profile.curselection()) +" ?"):
                self.ProfileSelected = self.Profile.get(self.Profile.curselection())
            #Ask for passphrase
        
    
    def navbar(self):
        i =1
        self.Logo = tk.Label(self, text="Peer-to-Text !")
        self.Logo.grid(row=1,column=i)
        self.Logo.bind("<Button-1>", self.showAccueil)

        i+=1
        self.Accueil = tk.Label(self, text="Accueil")
        self.Accueil.grid(row=1,column=i)
        self.Accueil.bind("<Button-1>", self.showAccueil)
        
        i+=1
        self.Amis = tk.Label(self, text="Amis")
        self.Amis.grid(row=1,column=i)
        self.Amis.bind("<Button-1>", self.showAmis)

        i+=1
        self.Projets = tk.Label(self, text="Projets")
        self.Projets.grid(row=1,column=i)
        self.Projets.bind("<Button-1>", self.showProjets)
        
        i+=1
        self.Messagerie = tk.Label(self, text="Messagerie")
        self.Messagerie.grid(row=1,column=i)
        self.Messagerie.bind("<Button-1>", self.showMessagerie)
        
        i+=1
        self.Parametres = tk.Label(self, text="Paramètres")
        self.Parametres.grid(row=1,column=i)
        self.Parametres.bind("<Button-1>", self.showParametres)
        
        i+=1
        self.Profil = tk.Label(self, text="Profil")
        self.Profil.grid(row=1,column=i)
        self.Profil.bind("<Button-1>", self.showProfil)
        
        i+=1
        self.Logout = tk.Label(self, text="Déconnexion")
        self.Logout.grid(row=1,column=i)
        self.Logout.bind("<Button-1>", self.logout)
    
    def showAccueil(self, event):
        print("Accueil")

    def showAmis(self, event):
        print("Amis")
        
    def showProjets(self, event):
        print("Projets")

    def showMessagerie(self, event):
        print("Mess")

    def showParametres(self, event):
        print("Para")

    def showProfil(self, event):
        print("Profil")
            
        tk.Label(self, text="Pseudo").grid(row=2, column=1)
        self.pseudoEntry = tk.Entry(self)
        self.pseudoEntry.bind("<Key-Return>", self.updatePseudo)
        self.pseudoEntry.grid(row=2, column=2)
        with open("profile.json","r") as json_data:
            data = json.load(json_data)
            content = tk.StringVar()
            self.pseudo=data["pseudo"]
            content.set(self.pseudo)
            self.pseudoEntry["textvariable"] = content
            
        self.uuidEntry = tk.Entry(self)
        content = tk.StringVar()
        content.set(json.dumps(self.uuid(self.pseudo + ".profile")))
        self.uuidEntry["textvariable"] = content
        self.uuidEntry.grid(row=3, column=2)
        

    def updatePseudo(self, event):
        self.pseudo = self.pseudoEntry.get()
        with open("config.json","w") as file:
            file.write(json.dumps({"pseudo":self.pseudo}))
        print(self.pseudo)
        
        

    def logout(self, event):
        print("Bye")

    def uuid(self):
        from urllib.request import urlopen
        from bs4 import BeautifulSoup as bs
        from uuid import uuid4
        profile = {"uuid":str(uuid4()),"ip":[bs(urlopen("http://whatismyip.org/"), "html.parser").span.getText()]}
        print(profile)
        return profile

    def saveProfile(self, event):
        with filedialog.asksaveasfile(mode="w", defaultextension=".profile") as file:
            file.write(json.dumps(profile))
    
    
root = tk.Tk()
gui = GUI(root)
gui.mainloop()
