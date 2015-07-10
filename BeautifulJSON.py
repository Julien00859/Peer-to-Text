def BeautifulJSON(json):
	#Just change {"Plouf":{"Lol":"MDR"}} to:
	#{
	#	"Plouf":{
	#		"Lol":"MDR"
	#	}
	#}
    array = list()
    for l in json:
        array.append(l)
    i = int(0)
    t = int(0)
    for l in array:
        if l == "{":
            l = "{\n"
            t+=1
            for x in range(0, t):
                l += "\t"
        elif l == "}":
            l = "\n"
            t-=1
            for x in range(0, t):
                l += "\t"
            l += "}"
        elif l == "[":
            l = "[\n"
            t+=1
            for x in range(0, t):
                l += "\t"
        elif l == "]":
            l = "\n"
            t-=1
            for x in range(0, t):
                l += "\t"
            l+="]"
        elif l == ",":
            l = ",\n"
            for x in range(0, t):
                l += "\t"
        
        array[i] = l
        i += 1
    json = "".join(array).replace("\n ","\n").replace("\t ","\t")
    return json