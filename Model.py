import pandas as pd


class Model:
    volunteers = []
    shifts = []

    def __init__(self, planning_url):
        self.planning_url = planning_url

    def collect(self):
        df = pd.read_csv(self.planning_url)
        print(df)
