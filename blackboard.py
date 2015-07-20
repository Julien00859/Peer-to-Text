class blackboard():

    def __init__(self):
        self.blackboard = [[]]
    
    def write(self, pos, msg):
        for c in msg:
            if c == "\n":
                self.blackboard[pos[0]].insert(pos[1], c)
                if len(self.blackboard) == pos[0]+1:
                    self.blackboard.append(self.blackboard[pos[0]][pos[1]+1:len(self.blackboard[pos[0]])])
                else:
                    self.blackboard.insert(pos[0]+1, self.blackboard[pos[0]][pos[1]+1:len(self.blackboard[pos[0]])])
                del self.blackboard[pos[0]][pos[1]+1:len(self.blackboard[pos[0]])]
                pos[0]+=1
                pos[1]=0
            else:
                self.blackboard[pos[0]].insert(pos[1], c)
                pos[1]+=1
        print(self)

    def erase(self, pos, length):
        while length > 0:
            if length >= len(self.blackboard[pos[0]]):
                length-=len(self.blackboard[pos[0]])-pos[1]
                del self.blackboard[pos[0]][pos[1]:len(self.blackboard[pos[0]])]
                self.blackboard[pos[0]].extend(self.blackboard[pos[0]+1])
                del self.blackboard[pos[0]+1]
            else:
                del self.blackboard[pos[0]][pos[1]:pos[1]+length]
                length=0
        print(self)

    def end(self, line=None):
        if line == None:
            line = len(self.blackboard)-1
        if len(self.blackboard[line]) == 0 or self.blackboard[line][-1] != "\n":
            return [line, len(self.blackboard[line])]
        else:
            return [line, len(self.blackboard[line])-1]

    #  01234567890123456789
    #0 Salut à tous\n
    #1 Je m'appelle Julien\n
    #2
    def __str__(self):
        s = str()
        n = int(0)
        s+="    {}\n".format("".join([str(n%10) for n in range(0, max([len(x) for x in self.blackboard]))]))
        for line in self.blackboard:
            s+="{: 03d} ".format(n)+"".join(line)
            n+=1
        return s
