# -*- coding: UTF-8 -*-

from collections import OrderedDict
from json import load
from sys import stdout

class blackboard():
    """Editeur de texte interne"""

    def __init__(self, name="blackboard", content=None):
        self.blackboard = [[]]
        self.history = OrderedDict() #{uid:(write/erase, pos, msg/lenght)}
        self.__name__ = name
        self.write(content)

    def update(self, uid, lastuid, then, pos, msg):
        """Méthode mettant à jour le tableau noir avec gestion des collision de packet
        En premier argument on prend l'identifiant de la modification actuelle
        En deuxième argument on prend l'identifiant de la dernière modification connu avant l'envoit de celle-ci
        En troisième argument on prend la méthode à appeler à la suite de la gestion des collision (write, erase)
        En quatrième argument on prend la position
        En cinquième argument on prend le message à ajouter ou la longueur à supprimer"""

        oldpos = pos.copy()

        #On fait une liste des uid connues
        histkeys = list(self.history.keys())

        #Si lastuid est dans la liste mais que ce n'est pas la dernière modification alors on doit vérifier que la position de uid ne doit pas être mise à jour
        if histkeys.count(lastuid) and histkeys[-1] != lastuid:
            #on fait une liste des modification depuis lastuid
            diffs = list(self.history.values())[histkeys.index(lastuid)+1:len(histkeys)]
            for diff in diffs:
                #pour chaque différence, on regarde si elle a eu lieu <= la position de l'actuelle modification
                if diff[1][0] <= pos[0]:
                    #on check si c'est un ajout et un retrait
                    if diff[0] == "write":
                        #si la modification a eu lieu sur une ligne antérieur à la position de la modif actuelle, on compte le nombre de saut de ligne ajouté par ces modification pour mettre à jour la ligne.
                        if diff[1][0] < pos[0]:
                            pos = [pos[0] + diff[2].count("\n"), pos[1]]

                        #si la modification a eu lieu sur la même ligne et une colonne antérieur, on calcule les différences (ligne et colonne)
                        elif diff[1][0] == pos[0] and diff[1][1] <= pos[1]:
                            pos = [pos[0] + diff[2].count("\n"), pos[1] + len(diff[2][diff[2].rfind("\n")+1:len(diff[2])])]

                    elif diff[1] == "erase":
                        while diff[2] > 0:
                            if diff[1][1] + diff[2] >= len(self.blackboard[diff[1][0]]):
                                pos[0]-=1
                            else:
                                pos[1] = diff[1][1]
            print("Updating position: {} diff(s) found, position updated from {} to {}".format(len(diffs), str(oldpos), str(pos)), file = open(load(open("config.json"))["output"], "a") if load(open("config.json"))["output"] != "sys.stdout" else stdout)

        self.history[uid] = (then.__name__, pos.copy(), msg)
        msg = len(msg) if then.__name__ == "erase" and type(msg) ==  type("") else msg
        then(pos, msg)

    def write(self, pos, msg):
        """Méthode permettant d'écrire dans le tableau noir
        En premier argument on prend la position du premier caractère à ajouter au format [ligne, colonne]
        En deuxième argument on prend un string contenant le message à ajouter"""

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
        En deuxième argument on prend la longueur de la chaîne à effacer"""
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

    def __repr__(self):
        """Fonction qui retourne le contenu du tableau noir dans un string unique non formatté"""
        s = str()
        for line in self.blackboard:
            s+="".join(line)
        return s
