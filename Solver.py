from ortools.sat.python import cp_model

class Solver:
    is_feasible = {}
    four_ppl = {}
    preference_match = {}
    var_X = {}

    def __init__(self, data):
        self.planningData = data
        self.shifts = data.getShifts()
        self.volunteers = data.getVolunteers()
        self.model = cp_model.CpModel()
        self.solver = cp_model.CpSolver()

        self.initBoolVar()
        self.initConstraints()
        self.initObjectiveFunction()
        self.solve()
        self.printPlanning()

    def initBoolVar(self):
        for i in self.volunteers:
            for p in self.shifts:
                self.var_X[(i.getIndex(), p.getDay())] = self.model.NewBoolVar(f"X_i{i.getIndex()}_p{p.getDay()}")

    def initConstraints(self):
        self.constraintsOnShift(3, 4)
        #self.constraintsOnVolunteer()

    def constraintsOnShift(self, min_volunteers, max_volunteers):
        for p in self.shifts:
            self.is_feasible[(p.getDay())] = self.model.NewBoolVar(f"V_nb_vols{p.getDay()}")
            self.four_ppl[(p.getDay())] = self.model.NewBoolVar(f"four_ppl{p.getDay()}")

            # for vol in self.volunteers:
                #print("name:" + vol.getName() + "is availiable : " + str(vol.isAvailable(p.getDay())))


            # Une permanence est faisable avec au moins 3 volontaires
            self.model.Add(sum(((self.var_X[i.getIndex(), p.getDay()]) * i.isAvailable(p.getDay())) for i in self.volunteers) >= min_volunteers).OnlyEnforceIf(self.is_feasible[p.getDay()])

            # Une permanence est faisable s'il y au max 4 volontaires
            self.model.Add(sum(((self.var_X[i.getIndex(), p.getDay()]) * i.isAvailable(p.getDay())) for i in self.volunteers) <= max_volunteers).OnlyEnforceIf(self.is_feasible[p.getDay()])

            '''
            # Une permanence est faisable s'il y a au moins un référent par permanence
            self.model.Add(sum(((self.var_X[i.getIndex(), p.getDay()] * i.isAvailable(p.getDay())) * i.isReferent()) for i in self.volunteers) >= 1).OnlyEnforceIf(self.is_feasible[p.getDay()])
            '''

            '''
            # On encourage les permanences à 4 personnes et plus
            self.model.Add(sum(
                (self.var_X[i.getIndex(), p.getDay()] * i.isAvailable(p)) for i in self.volunteers) >= 4).OnlyEnforceIf(
                self.four_ppl[p.getDay()])
            self.model.Add(sum(
                (self.var_X[i.getIndex(), p.getDay()] * i.isAvailable(p)) for i in self.volunteers) < 4).OnlyEnforceIf(
                self.four_ppl[p.getDay()].Not())
            '''

    def constraintsOnVolunteer(self):
        for i in self.volunteers:
            # Pour chaque bénévole, il faut que le nombre de permanence assigné soit inférieur à 3
            self.model.Add(sum(self.var_X[i.getIndex(), p.getDay()] for p in self.shifts) <= 3)

            '''
            # Pour chaque bénévole, si le nombre de permanence assignée correspond au souhait du bénévole alors on encourage
            self.preference_match[(i.getIndex())] = self.model.NewBoolVar(f"preference_match{i}")

            self.model.Add(sum(self.var_X[i.getIndex(), p.getDay()] * i.isAvailable(p) for p in
                               self.shifts) <= i.getNbPermPref()).OnlyEnforceIf(
                self.preference_match[i.getIndex()])
            self.model.Add(sum(self.var_X[i.getIndex(), p.getDay()] * i.isAvailable(p) for p in
                               self.shifts) > i.getNbPermPref()).OnlyEnforceIf(
                self.preference_match[i.getIndex()].Not())
            '''
        '''
        # Une pause d'au moins 6 jours entre deux permanences
        time_break = self.planningData.getTimeBreak()

        for i in self.volunteers:
            for p in self.shifts:
                nextShift = self.planningData.getNextShift(p.getIndex(), time_break)
                self.model.Add(sum(self.var_X[i.getIndex(), w.getDay()] for w in nextShift) <= 1)
                '''


    def initObjectiveFunction(self):
        self.model.Maximize(
            sum(
                (self.is_feasible[p.getDay()]) for p in self.shifts
                ## + (0.2 * self.four_ppl[p.getDay()]) + (self.preference_match[i.getIndex()])
                #for i in self.volunteers
            )
        )

    def solve(self):

        # Set max time solver
        self.solver.parameters.max_time_in_seconds = 30.0

        solution_printer = cp_model.ObjectiveSolutionPrinter()
        status = self.solver.Solve(self.model, solution_printer)

        print(f"Status = {self.solver.StatusName(status)}")
        print(f"Number of solutions found: {solution_printer.solution_count()}")

        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            for p in self.shifts:
                if (self.solver.Value(self.is_feasible[(p.getDay())])) == 1:
                    p.setOpen()

                    for i in self.volunteers:
                        if self.solver.Value(self.var_X[(i.getIndex(), p.getDay())]) == 1:
                            print(f"Vol {i.getName()} is assigned to perm {p.getDay()} and is availiable : {i.isAvailable(p.getDay())}")
                            p.assignVolunteer(i)

       ##     for i in self.volunteers:
        ##       if self.solver.Value(self.preference_match[(i.getIndex())]) == 1:
        ##        i.setPreferenceMatched()


        else:
            print("No solutions found !")

    def printPlanning(self):
        for p in self.shifts:
            if(p.isOpen):
                print(f"PERMANENCE OUVERTE LE {p.getDay()}")
                for vol in p.volunteers_assigned:
                    print(vol.getName())