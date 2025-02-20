# Python program to demonstrate
# main() function
from PlanningData import PlanningData
from Solver import Solver
# Defining main function




def main():
	url = "https://docs.google.com/spreadsheets/d/1omBoCEb19DmFxf0IM2JM3V6Rypoat1K6/export?format=csv"
	data = PlanningData(url, 3, 6, 2025)
	solver = Solver(data)


main()

