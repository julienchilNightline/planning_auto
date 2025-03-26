# Python program to demonstrate
# main() function
from PlanningData import PlanningData
from Solver import Solver
# Defining main function




def main():
	url = "https://docs.google.com/spreadsheets/d/1ilNov9uyRuIHTuGWLYqOiSLvK_NJ_U1AWBkbjvOrbOA/export?format=csv"
	data = PlanningData(url, 5, 3, 2025)
	solver = Solver(data)


main()

