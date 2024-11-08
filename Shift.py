class Shift:

    def __init__(self, day, is_surstaff, index):
        self.day = day
        self.is_surstaff = is_surstaff
        self.index = index
        self.open = False
        self.volunteers_assigned = []

    def assignVolunteer(self, volunteer):
       self.volunteers_assigned.append(volunteer)

    def getDay(self):
        return self.day

    def getIndex(self):
        return self.index

    def getAssignedVolunteers(self):
        return self.volunteers_assigned

    def setOpen(self):
        self.open = True

    def isOpen(self):
        return self.open
