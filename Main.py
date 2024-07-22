# Python program to demonstrate
# main() function
from Model import Model

print("Hello")

# Defining main function
def main():
	url = "https://docs.google.com/spreadsheets/d/1f2RsLtd1A4MpRYau_KSApaGUA4L6M0qlZmrufrY4ohg/export?format=csv"
	model = Model(url)
	model.collect(4)


main()

