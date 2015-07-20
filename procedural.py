from profile import *
from server import *
from blackboard import *
from tkinter.filedialog import askopenfilename
import json
import os

#On vérifie que le dossier "profiles" et que le fichier "config.json" existent, sinon on les crée
ls = os.listdir(os.getcwd())
if not "profiles" in ls:
	os.mkdir("profiles")
if not "config.json" in ls:
	with open("config.json","w") as f:
		f.write(json.dumps({"host":"localhost","port":48256,"output":"sys.stdout"}, indent=4))

#On liste les profiles existant dans le dossier /profiles/ et on propose également d'en créer un nouveau ou d'en importer un
profiles = list()
print("\nSelect your profil:")
for p in os.listdir(os.path.join(os.getcwd(),"profiles")):
	if p.endswith(".json"):
		profiles.append(os.path.join(os.getcwd(),"profiles", p))
		print("{:02d}. {}\t{}".format(len(profiles), p[p.find("_")+1:p.find(".")], p[:p.find("_")]))
print("{:02d}. New Profile".format(len(profiles)+1))
print("{:02d}. Import Profile".format(len(profiles)+2))

#On demande à l'utilisateur de faire un choix
while "moi" not in locals():
	try:
		choix = int(input("Veuillez entrer votre choix: "))-1
		assert 0 <= choix <= len(profiles)+1
	except Exception as ex:
		print(ex)
	else:
		if choix < len(profiles):
			moi = PrivateProfile(profiles[choix])
		elif choix == len(profiles):
			moi = PrivateProfile().new(pseudo=input("Pseudo: "), mail=input("Mail: "))
		elif choix == len(profiles)+1:
			moi = PrivateProfile(askopenfilename(initialdir=os.getcwd(),title="Importer un profile"))

#On initialise le serveur sur un autre thread et on écoute les requêtes
server = server(moi)
server.start()

#On initialise l'éditeur de texte interne
b = blackboard()

#Une console est lancée à des fins de debuging
print("\nPython Shell - Type 'stop' to stop all the process.")
while True:
	try:
		msg = input(">>> ")
		if msg=="stop":
			break
		eval(msg)
	except Exception as ex:
		print(ex)

#On arrête le serveur et on stoppe le serveur
print("Stopping...")
server.stop()
print("Stopped")
