from random import randint

class Crypto: 
    def __init__(self):
        self.tab = self.tabgen()
        self.key = self.keygen(128)

    def tabgen(self):
        tab=list()
        for i in range(128-32):
            tab.append([chr(i) for i in range(32,128)])
            for n in range(i):
                tab[i].append(tab[i].pop(0))
        return tab
    
    def keygen(self, length):
        key=str()
        for i in range(length):
            key+=self.tab[0][randint(32, 128-32-1)]
        return key

    def crypt(self, msg, key):
        secret=str()
        for i in range(len(msg)):
            secret+=self.tab[0][self.tab[self.tab[0].index(msg[i])].index(key[i%len(key)])]
        return secret

if __name__ == '__main__':
    import sys
    c=crypto()
    if len(sys.argv)>2:
        with open(sys.argv[1],"r") as fr:
            secret = c.crypt(fr.read(), sys.argv[2])
            if len(sys.argv)>4:
                if sys.argv[3] == ">":
                    with open(sys.argv[4],"w") as fw:
                        fw.write(secret)
                elif sys.argv[3] == ">>":
                    with open(sys.argv[4],"a") as fw:
                        fw.write(secret)
                else:
                    print("Unknow char: " + str(sys.argv[3]))
                    
            else:
                print(secret)
    else:
        print(str(sys.argv[0]) + " file key [>|>> outpout]")
            
