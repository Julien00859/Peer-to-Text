class blackboard():

    def __init__(self):
        """Initialisation d'un tableau noir vide de contenu"""
        self.blackboard = [[]]
    
    def write(self, pos, msg):
        """Méthode permettant d'écrire dans le tableau noir
        En premier argument on prend la position du premier caractère à ajouter au format [ligne, colonne]
        En second argument on prend un string contenant le message à ajouter"""
        for c in msg:
            if c == "\n":
                #Si le charactère est un saut de ligne, on l'ajoute
                self.blackboard[pos[0]].insert(pos[1], c)
                #On déplace ensuite tout ce qui suit le \n à une nouvelle ligne
                if len(self.blackboard) == pos[0]+1:
                    self.blackboard.append(self.blackboard[pos[0]][pos[1]+1:len(self.blackboard[pos[0]])])
                else:
                    self.blackboard.insert(pos[0]+1, self.blackboard[pos[0]][pos[1]+1:len(self.blackboard[pos[0]])])
                del self.blackboard[pos[0]][pos[1]+1:len(self.blackboard[pos[0]])]
                #Pour finir on met à jour la position
                pos[0]+=1
                pos[1]=0
            else:
                #On ajoute le caractère et on met à jour la position
                self.blackboard[pos[0]].insert(pos[1], c)
                pos[1]+=1
        print(self)

    def erase(self, pos, length):
        """Méthode permettant d'effacer du contenu dans le tableau
        En premier argument on prend la position du premier caractère à effacer
        En second argument on prend la longueur de la chaîne à effacer"""
        while length > 0:
            if length >= len(self.blackboard[pos[0]]):
                #Dans le cas où l'effacement est sur plusieurs lignes, on efface le contenu de la ligne actuelle  
                #en partant de la position donnée et on déplace tout le contenu de la ligne suivante à la ligne  
                #actuelle tout en mettant à jour la longueur de la chaine qu'il reste à effacer
                length-=len(self.blackboard[pos[0]])-pos[1]
                del self.blackboard[pos[0]][pos[1]:len(self.blackboard[pos[0]])]
                self.blackboard[pos[0]].extend(self.blackboard[pos[0]+1])
                del self.blackboard[pos[0]+1]
            else:
                #Si l'effacement n'est que sur le ligne actuelle, on supprime une chaine de longueur length à partir de la position donnée
                del self.blackboard[pos[0]][pos[1]:pos[1]+length]
                length=0
        print(self)

    def end(self, line=None):
        """Fonction retourant la position du dernier caractère du tableau ou de la ligne si elle est précisée"""
        if line == None:
            #Si la ligne n'est pas donné alors on prend la dernière ligne du tableau
            line = len(self.blackboard)-1

        if len(self.blackboard[line]) == 0 or self.blackboard[line][-1] != "\n":
            #Si la ligne est vide ou qu'elle ne se termine pas par un saut de ligne alors on retourne la longueur de la ligne
            return [line, len(self.blackboard[line])]
        else:
            #Si la ligne fini par un saut de ligne alors on retourne la position juste antérieur au saut de ligne
            return [line, len(self.blackboard[line])-1]

    def save(self, file):
        """Méthode permettant d'enregistrer le contenu du tableau dans un fichier"""
        with open(file, "w") as f:
            for line in self.blackboard:
                f.write("".join(line))


    def __str__(self):
        """Fonction qui retourne une chaine formattée de la manière suivante:
            01234567890123456789
         00 Salut à tous\n
         01 Je m'appelle Julien\n
         02
        """
        s = str()
        n = int(0)
        #On chope la ligne la plus longue et imprime les unités jusqu'à atteindre la longueur de la ligne la plus longue
        s+="    {}\n".format("".join([str(n%10) for n in range(0, max([len(x) for x in self.blackboard]))]))
        for line in self.blackboard:
            #Puis par ligne on affiche le numéro
            s+="{: 03d} ".format(n)+"".join(line)
            n+=1
        return s
