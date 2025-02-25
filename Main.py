# Python program to demonstrate
# main() function
from PlanningData import PlanningData
from Solver import Solver
# Defining main function




def main():
	url = "https://docs.google.com/spreadsheets/d/1Q01JqjO-8K6MTAwEPNVLSnxxFuKculjSRLgjyUKM8TY/export?format=csv"
	data = PlanningData(url, 4, 3, 2025)
	solver = Solver(data)


main()

