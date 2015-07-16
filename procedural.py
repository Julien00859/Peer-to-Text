from profile import *
from server import *
import json
import os

def test(test):
	while True:
		try:
			return eval(test)
		except Exception as ex:
			print(ex)

profiles = list()
for p in os.listdir(os.getcwd()+"/profiles/"):
	profiles.append(p)
	print("{:02d}. {}\t{}".format(len(profiles), p[p.find("_")+1:], p[:p.find("_")]))

moi = test("PrivateProfile(profiles[int(input(\"\\nSelect your profile: \"))-1])")

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
