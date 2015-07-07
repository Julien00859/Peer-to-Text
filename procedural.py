from profile import Profile
import os 

profiles = [profile for profile in os.listdir(os.getcwd()+"/profiles/") if profile.endswith(".profile")]
msg = str()
for profile in profiles:
	msg+="[{}] {}\n".format(profiles.index(profile)+1, profile[:profile.find(".profile")])

choix = int(input("Veuillez choisir un profile:\n" + msg + "[{}] Nouveau Profile\n".format(len(profiles)+1)))-1
if choix >= 0 and choix < len(profiles):
	profile = Profile()
	profile.load(profiles[choix])
	profile.getIP()
	print("\nProfile choisi: {} ({})\n".format(profile.pseudo,profile.uuid))
elif choix == len(profiles):
	profile = Profile()
	profile.new(pseudo=input("Pseudo: "), mail=input("Mail: "))
else:
	raise ValueError()

copain = Profile()
copain.load(profiles[1])
profile.addUser(copain.getSharableProfile())
profile.save()