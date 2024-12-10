# Python program to demonstrate
# main() function
from PlanningData import PlanningData
from Solver import Solver
# Defining main function




def main():
	url = "https://docs.google.com/spreadsheets/d/10JViIv7f2q8BF4TKiWcENLpU5_PYkHuYeEITSrrtlBU/export?format=csv"
	data = PlanningData(url, 5, 12, 2024)
	solver = Solver(data)


main()

