# -*- coding: UTF-8 -*-

class permissions:
    """Classe de gestion des permissions. Permet de récupérer le groupe d'un utilisateur"""
    def __init__(self, permissions):
        self.groups = permissions["groups"].copy()
        self.users = permissions["users"].copy()

        for group in self.groups.keys():
            if "default" in group:
                if group["default"] = True:
                    self.default = group
                    break
        else:
            self.default=None

    def getFile(self, file, uuid=None, group=None, recurcive=True):
        """Retourne la permission du fichier par rapport à l'utilisateur ou au groupe donné. Peut se faire de manière récurcive."""
        if group == None and uuid != None:
            group = getGroup(uuid)
        elif group == None and uuid == None:
            group = self.default

        if file in self.groups[group]["files"]:
            return self.groups[group]["files"][file]

        else:
            if "*" in self.groups[group]["files"]:
                return self.groups[group]["files"]["*"]

            else:
                if "inherite" in self.groups[group]:
                    for herite in self.groups[group]["inherite"]:
                        result = self.get(file, group=herite, recurcive=False)
                        if result != None:
                            return result
                            break

                    else:
                        if recurcive == True:
                            for herite in self.groups[group]["inherite"]:
                                result = self.get(file, group=herite, recurcive=True)
                                if result != None:
                                    return result
                                    break
                            else:
                                return "none"

    def getGroup(self, uuid):
        """Retourne le groupe de l'utilisateur ou le groupe par défaut."""
        if uuid in self.users and "group" in self.users[uuid] and self.users[uuid]["group"] in self.groups:
            return self.users[uuid]["group"]
        else:
            return self.default
