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
        self.printResultsForSheet()

    def initBoolVar(self):
        for i in self.volunteers:
            self.preference_match[i.getIndex()] = self.model.NewBoolVar(f"preference_match{i.getIndex()}")

            for p in self.shifts:
                self.var_X[(i.getIndex(), p.getDay())] = self.model.NewBoolVar(f"X_i{i.getIndex()}_p{p.getDay()}")

        for p in self.shifts:
            self.is_feasible[(p.getDay())] = self.model.NewBoolVar(f"is_feasible{p.getDay()}")
            self.four_ppl[(p.getDay())] = self.model.NewBoolVar(f"four_ppl{p.getDay()}")

    def initConstraints(self):
        self.constraintsOnShift(3, 4)
        self.constraintsOnVolunteer()

    def constraintsOnShift(self, min_volunteers, max_volunteers):
        for p in self.shifts:
            # Une permanence est faisable avec au moins 3 volontaires
            self.model.Add(sum(((self.var_X[i.getIndex(), p.getDay()]) * i.isAvailable(p.getDay())) for i in
                               self.volunteers) >= min_volunteers).OnlyEnforceIf(self.is_feasible[p.getDay()])

            # Une permanence est faisable s'il y au max 4 volontaires
            self.model.Add(sum(((self.var_X[i.getIndex(), p.getDay()]) * i.isAvailable(p.getDay())) for i in
                               self.volunteers) <= max_volunteers).OnlyEnforceIf(self.is_feasible[p.getDay()])

            # Une permanence est faisable s'il y a au moins un référent par permanence
            self.model.Add(sum(
                ((self.var_X[i.getIndex(), p.getDay()] * i.isAvailable(p.getDay())) * i.isReferent()) for i in
                self.volunteers) >= 1).OnlyEnforceIf(self.is_feasible[p.getDay()])

            # On encourage les permanences à 4 personnes et plus
            self.model.Add(sum(
                (self.var_X[i.getIndex(), p.getDay()] * i.isAvailable(p.getDay())) for i in
                self.volunteers) == 4).OnlyEnforceIf(
                self.four_ppl[p.getDay()])
            self.model.Add(sum(
                (self.var_X[i.getIndex(), p.getDay()] * i.isAvailable(p.getDay())) for i in
                self.volunteers) < 4).OnlyEnforceIf(
                self.four_ppl[p.getDay()].Not())

    def constraintsOnVolunteer(self):
        time_break = self.planningData.getTimeBreak()
        for i in self.volunteers:
            # Pour chaque bénévole, il faut que le nombre de permanence assigné soit inférieur au minimum entre 3 et le nombre de perm souhaitée
            self.model.Add(sum(self.var_X[i.getIndex(), p.getDay()] for p in self.shifts) <= min(3, i.getNbPermPref()))

            # Pour chaque bénévole, il faut au max 2 référence
            self.model.Add(sum(
                (self.var_X[i.getIndex(), p.getDay()] * i.isReferent()) for p in
                self.shifts) <= 2)

            # Une pause d'au moins 6 jours entre deux permanences
            for p in self.shifts:
                # Obtenir les permanences futures dans la fenêtre de 6 jours
                next_shifts = self.planningData.getNextShift(p.getIndex(), time_break)

                # Empêcher d'assigner le volontaire à deux permanences dans cette fenêtre
                self.model.Add(
                    sum(self.var_X[i.getIndex(), w.getDay()] for w in next_shifts) + self.var_X[
                        i.getIndex(), p.getDay()] <= 1
                )

            # Empêcher d'assigner le volontaire si la dernière permanence est trop proche
            if i.last_perm:
                for p in self.shifts:
                    days_since_last_perm = (p.getDate() - i.last_perm).days
                    if 0 <= days_since_last_perm < time_break:
                        # Empêcher d'assigner le volontaire si la dernière permanence est trop proche
                        self.model.Add(self.var_X[i.getIndex(), p.getDay()] == 0)

            # On encourage le respect du nombre de perm préféré par les volontaires
            self.model.Add(sum(self.var_X[i.getIndex(), p.getDay()] * i.isAvailable(p.getDay()) for p in
                               self.shifts) == i.getNbPermPref()).OnlyEnforceIf(
                self.preference_match[i.getIndex()])
            self.model.Add(sum(self.var_X[i.getIndex(), p.getDay()] * i.isAvailable(p.getDay()) for p in
                               self.shifts) < i.getNbPermPref()).OnlyEnforceIf(
                self.preference_match[i.getIndex()].Not())

    def initObjectiveFunction(self):

        self.model.Maximize(
            sum(
                (self.is_feasible[p.getDay()] + self.preference_match[i.getIndex()])
                for i in self.volunteers
                for p in self.shifts
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
                            p.assignVolunteer(i)

        else:
            print("No solutions found !")

    def printPlanning(self):
        countNbPerm = 0
        nbAssignement = 0
        nbPermFourPeople = 0

        for p in self.shifts:
            if p.isOpen():
                countNbPerm += 1
                nbAssignement += len(p.volunteers_assigned)
                if (len(p.volunteers_assigned) >= 4):
                    nbPermFourPeople += 1

                print(f"PERMANENCE OUVERTE LE {p.getDay()}")
                for vol in p.volunteers_assigned:
                    print(f"{vol.getName()} is referent : {vol.isReferent()}")

        print(f"nombre de permanence faisables : {countNbPerm}")
        print(f"nombre d'assignements : {nbAssignement}")
        print(f"nombre de permanence à quatre personnes : {nbPermFourPeople}")

    def printResultsForSheet(self):
        # Titre des colonnes : bénévole / date
        headers = ["Bénévole / Date"] + [f"Jour {p.getDay()} ({p.getDate().strftime('%d/%m')})" for p in self.shifts if
                                         p.isOpen()]
        header_line = "\t".join(headers)

        # Contenu des lignes
        rows = []
        for vol in self.volunteers:
            row = [vol.getName()]
            for p in self.shifts:
                if p.isOpen():
                    if vol in p.getAssignedVolunteers():
                        if vol.isReferent():
                            row.append("X (Référent)")
                        else:
                            row.append("X")
                    else:
                        row.append("INDISPO" if vol.isAvailable(p.getDay()) == 0 else "DISPO")  # Case vide si non assigné
            rows.append("\t".join(row))

        # Calcul des statistiques
        count_nb_perm = sum(1 for p in self.shifts if p.isOpen())
        nb_perm_four_people = sum(1 for p in self.shifts if len(p.getAssignedVolunteers()) >= 4)

        # Affichage des statistiques
        stats = [
            "",  # Ligne vide pour séparer le tableau des stats
            f"Nombre de permanences faisables : {count_nb_perm}",
            f"Nombre de permanences à 4 personnes : {nb_perm_four_people}"
        ]

        # Affichage dans la console
        print(header_line)
        for row in rows:
            print(row)

        for stat in stats:
            print(stat)
