import pandas as pd

from Volunteer import Volunteer


class Model:
    volunteers = []
    shifts = []

    def __init__(self, planning_url):
        self.planning_url = planning_url

    def collect(self, name_column_position):
        df = pd.read_csv(self.planning_url)
        data = df.copy()

        # Setting column as column title
        data.columns = data.iloc[name_column_position]
        data = data.drop(name_column_position)
        data = data.reset_index()

        print(data.head())

        # Keeping useful column
        final_table_columns = ['name', 'nb_perm', 'nb_surstaff', 'is_referent', 'last_perm', 'dispo_perm',
                               'dispo_surstaff']
        data = data.drop(columns=[col for col in data if col not in final_table_columns])
        data.name = data.name.str.replace('.', '')

        # Extracting volunteers infos
        volunteers_infos = data.copy()
        volunteers_infos = volunteers_infos[['name', 'nb_perm', 'nb_surstaff', 'is_referent', 'last_perm']]
        volunteers_infos = volunteers_infos.rename(columns={'name': 'full_name'})
        volunteers_infos = volunteers_infos.dropna()

        # Building the list of volunteers object
        for index, row in volunteers_infos.iterrows():
            self.volunteers.append(Volunteer(row.full_name, row.nb_perm, row.nb_surstaff, row.is_referent, row.last_perm))


        print(volunteers_infos)


