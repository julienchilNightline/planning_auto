# Python program to demonstrate
# main() function
from PlanningData import PlanningData
from Solver import Solver
# Defining main function
def main():
	url = "https://docs.google.com/spreadsheets/d/1f2RsLtd1A4MpRYau_KSApaGUA4L6M0qlZmrufrY4ohg/export?format=csv"
	data = PlanningData(url, 4)


	print("breakpoint")

	solver = Solver(data)



main()

