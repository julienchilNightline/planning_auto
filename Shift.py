class Shift:
    volunteers_assigned = []

    def __init__(self, day, is_surstaff, index):
        self.day = day
        self.is_surstaff = is_surstaff
        self.index = index

    def assignVolunteer(self, volunteer):
        self.volunteers_assigned.append(volunteer)

    def getDay(self):
        return self.day

    def getIndex(self):
        return self.index

