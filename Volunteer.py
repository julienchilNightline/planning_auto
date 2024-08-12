class Volunteer:
    availabilities = []
    nb_perm_pref = 0
    is_referent = False

    def __init__(self, index, name, nb_perm_pref, nb_surstaff_pref, is_referent, last_perm):
        self.index = index
        self.name = name
        self.nb_surstaff_pref = nb_surstaff_pref
        self.last_perm = last_perm

        self.cleanNbPermPref(nb_perm_pref)
        self.cleanIsReferent(is_referent)

    def setAvailability(self, availabilities):
        self.availabilities = availabilities

    def getName(self):
        return self.name

    def getAvailability(self):
        return self.availabilities

    def isAvailable(self, day):
        return 1 if day in self.availabilities else 0

    def getIndex(self):
        return self.index

    def isReferent(self):
        return 1 if self.is_referent else 0

    def getNbPermPref(self):
        return self.nb_perm_pref

    def cleanNbPermPref(self, nb_perm_pref):
        if nb_perm_pref == "Peu importe":
            self.nb_perm_pref = 3
        elif nb_perm_pref == "Pause":
            self.nb_perm_pref = 0
        else:
            self.nb_perm_pref = int(nb_perm_pref)

    def cleanIsReferent(self, is_referent):
        if is_referent == "TRUE":
            self.is_referent = True
        else:
            self.is_referent = False
