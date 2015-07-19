class blackboard():
    #0 Salut à tous\n
    #1 Je m'appelle\n
    #2 Julien
    #  0123456789012

    def __init__(self):
        self.blackboard = [[]]
    
    def write(self, pos, msg):
        for c in msg:
            if c == "\n":
                self.blackboard[pos[0]].insert(pos[1], c)
                pos[0]+=1
                pos[1]=0
                if len(self.blackboard) == pos[0]:
                    self.blackboard.append([])
                else:
                    self.blackboard.insert(pos[0], [])
            else:
                self.blackboard[pos[0]].insert(pos[1], c)
                pos[1]+=1
        print(self)

    def erase(self, pos, length):
        while length > 0:
            if pos[1] == 0 and length >= len(self.blackboard[pos[0]]):
                del self.blackboard[pos[0]]
                length-=len(self.blackboard[pos[0]])
            elif len(self.blackboard[pos[0]]) < length:
                del self.blackboard[pos[0]][pos[1]:len(self.blackboard[pos[0]])]
                length-=(len(self.blackboard[pos[0]]-pos[1]))
                pos[0]+=1
                pos[1]=0
            else:
                del self.blackboard[pos[0]][pos[1]:pos[1]+length]
                length=0
        print(self)

    def __str__(self):
        s = str()
        n = int(0)
        for line in self.blackboard:
            s+="{: 03d} ".join(line).format(n)
            n+=1
        return s
