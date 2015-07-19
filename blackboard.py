class blackboard():
    #0 Salut à tous\n
    #1 Je m'appelle\n
    #2 Julien\n
    #  012345678901\n

    def __init__(self):
        self.blackboard = [[]]
    
    def write(pos, msg):
        for c in msg:
            if c == "\n":
                self.blackboard[pos[0]].insert(pos[1], c)
                pos[0]+=1
                pos[1]=0
            else:
                self.blackboard[pos[0]].insert(pos[1], c)
                pos[1]+=1

    def erase(pos, length):
        while length > 0
            if pos[1] == 0 and length >= len(blackboard[pos[0]]):
                del blackboard[pos[0]]
                length-=len(blackboard[pos[0]])
            elif len(blackboard[pos[0]]) < length:
                del blackboard[pos[0]][pos[1], len(blackboard[pos[0]]))
                length-=(len(blackboard[pos[0]]-pos[1]))
                pos[0]+=1
                pos[1]=0
            else:
                del blackboard[pos[0]][pos[1], pos[1]+length]
                length=0
