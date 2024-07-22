class Availiability:
  volunteers = []

  def __init__(self, day, is_surstaff):
    self.day = day
    self.is_surstaff = is_surstaff

  def addVolunteer(self, volunteer):
     self.volunteers.append(volunteer)

  def getDay(self):
    return self.day






