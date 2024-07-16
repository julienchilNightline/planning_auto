# Python program to demonstrate
# main() function
from Model import Model

print("Hello")

# Defining main function
def main():
	url = "https://docs.google.com/spreadsheets/d/14n0elXUp9rN6lqsZQsjPdEMXfBem2Gvmx4Gnv41LLFU/export?format=csv"
	model = Model(url)
	model.collect()


main()

