from ortools.sat.python import cp_model


class Solver:
    is_feasible = {}
    four_ppl = {}
    preference_match = {}

    def __init__(self, data):
        self.planningData = data
        self.shifts = data.getShifts()
        self.volunteers = data.getVolunteers()
        self.model = cp_model.CpModel()
        self.var_X = {}

        self.initBoolVar()
        self.initConstraints()
        self.initObjectiveFunction()

    def initBoolVar(self):
        for i in self.volunteers:
            for p in self.shifts:
                self.var_X[(i.getIndex(), p.getDay())] = self.model.NewBoolVar(f"X_i{i}_p{p}")

    def initConstraints(self):
        self.constraintsOnShift(3, 4)
        self.constraintsOnVolunteer()

    def constraintsOnShift(self, min_volunteers, max_volunteers):
        for p in self.shifts:
            self.is_feasible[(p.getDay())] = self.model.NewBoolVar(f"V_nb_vols{p}")
            self.four_ppl[(p.getDay())] = self.model.NewBoolVar(f"four_ppl{p}")

            # Un permanence est faisable avec au moins 3 volontaires
            self.model.Add(sum((self.var_X[i.getIndex(), p.getDay()] * i.isAvailable(p)) for i in self.volunteers) >= min_volunteers).OnlyEnforceIf(self.is_feasible[p.getDay()])

            # Une permanence est faisable s'il y a max 4 volontaires
            self.model.Add(sum((self.var_X[i.getIndex(), p.getDay()] * i.isAvailable(p)) for i in
                               self.volunteers) <= max_volunteers).OnlyEnforceIf(
                self.is_feasible[p.getDay()])

            # Une permanence est faisable s'il y a au moins un référent par permanence
            self.model.Add(sum(((self.var_X[i.getIndex(), p.getDay()] * i.isAvailable(p)) * i.isReferent()) for i in
                               self.volunteers) >= 1).OnlyEnforceIf(
                self.is_feasible[p.getDay()])

            # On encourage les permanences à 4 personnes et plus
            self.model.Add(sum(
                (self.var_X[i.getIndex(), p.getDay()] * i.isAvailable(p)) for i in self.volunteers) >= 4).OnlyEnforceIf(
                self.four_ppl[p.getDay()])
            self.model.Add(sum(
                (self.var_X[i.getIndex(), p.getDay()] * i.isAvailable(p)) for i in self.volunteers) < 4).OnlyEnforceIf(
                self.four_ppl[p.getDay()].Not())

    def constraintsOnVolunteer(self):
        for i in self.volunteers:
            # Pour chaque bénévole, il faut que le nombre de permanence assigné soit inférieur à 3
            self.model.Add(sum(self.var_X[i.getIndex(), p.getDay()] for p in self.shifts) <= 3)

            # Pour chaque bénévole, si le nombre de permanence assignées correspond au souhait du bénévole alors on encourage
            self.preference_match[(i.getIndex())] = self.model.NewBoolVar(f"preference_match{i}")

            self.model.Add(sum(self.var_X[i.getIndex(), p.getDay()] * i.isAvailable(p) for p in
                               self.shifts) <= i.getNbPermPref()).OnlyEnforceIf(
                self.preference_match[i.getIndex()])
            self.model.Add(sum(self.var_X[i.getIndex(), p.getDay()] * i.isAvailable(p) for p in
                               self.shifts) > i.getNbPermPref()).OnlyEnforceIf(
                self.preference_match[i.getIndex()].Not())

        # Une pause d'au moins 6 jours entre deux permanences
        time_break = self.planningData.getTimeBreak()

        for i in self.volunteers:
            for p in self.shifts:
                nextShift = self.planningData.getNextShift(p.getIndex(), time_break)
                self.model.Add(sum(self.var_X[i.getIndex(), w.getDay()] for w in nextShift) <= 1)

    def initObjectiveFunction(self):
        self.model.Maximize(
            sum(
                (self.is_feasible[p.getDay()]) + (0.2 * self.four_ppl[p.getDay()]) + (self.preference_match[i.getIndex()])
                for i in self.volunteers
                for p in self.shifts
            )
        )
