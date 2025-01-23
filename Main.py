# Python program to demonstrate
# main() function
from PlanningData import PlanningData
from Solver import Solver
# Defining main function




def main():
	url = "https://docs.google.com/spreadsheets/d/1AkYubhXbRQ-aD3V23JidfSY0b3lqcNJhvT5j_YJx6dI/export?format=csv"
	data = PlanningData(url, 5, 2, 2025)
	solver = Solver(data)


main()

