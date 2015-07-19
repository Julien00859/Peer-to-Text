from profile import *
from server import *
from tkinter.filedialog import askopenfilename
import json
import os

for w in os.walk(os.getcwd()):
	if not w[0].count(".git") and not w[0].count("__pycache__"):
		if "template" not in w.dirnames:
			os.mkdir(os.path.join(w.dirpath, "template"))
		else:
			if "config.json" not in w.dirnames["template"]:
				pass
			if "anonymous.json" not in w.dirnames["template"]:
				pass
		if "profiles" not in w.dirnames:
			os.mkdir(os.path.join(w.dirpath, "profiles"))

input("[END]")


profiles = list()
for p in os.listdir(os.getcwd()+"/profiles/"):
	profiles.append(p)
	print("{:02d}. {}\t{}".format(len(profiles), p[p.find("_")+1:p.find(".")], p[:p.find("_")]))
print("{:02d}. Nouveau profile".format(len(profiles)+1))
print("{:02d}. Importer un profile".format(len(profiles)+2))

while True:
	try:
		choix = int(input("\nVeuillez entrer votre choix: "))
		assert 1 <= choix <= len(profiles)+2
	except Exception as ex:
		print(ex)
	else:
		if choix in profiles:
			moi = PrivateProfile(profiles[choix])
		elif choix == len(profiles)+1:
			moi = PrivateProfile().new(pseudo=input("Pseudo: "), mail=input("Mail: "))
		elif choix == len(profiles)+2:
			moi = PrivateProfile(askopenfilename(initialdir=os.getcwd(),title="Importer un profile"))

server = server(moi)
server.start()

print("\nPython Shell - Type 'stop' to stop all the process.")
while True:
	try:
		msg = input(">>> ")
		if msg=="stop":
			break
		eval(msg)
	except Exception as ex:
		print(ex)

print("Stopping...")
server.stop()
print("Stopped")
