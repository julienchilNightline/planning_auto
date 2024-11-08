import pandas as pd

from Shift import Shift
from Volunteer import Volunteer


class PlanningData:
    volunteers = []
    shifts = []
    time_break = 6

    def __init__(self, planning_url, name_column_position):
        self.planning_url = planning_url
        self.collect(name_column_position)

    def collect(self, name_column_position):
        df = pd.read_csv(self.planning_url)
        data = df.copy()

        # Setting column as column title
        data.columns = data.iloc[name_column_position]
        data = data.drop(name_column_position)
        data = data.reset_index()

        # Keeping useful column
        final_table_columns = ['name', 'nb_perm', 'nb_surstaff', 'is_referent', 'last_perm', 'dispo_perm',
                               'dispo_surstaff']
        data = data.drop(columns=[col for col in data if col not in final_table_columns])
        data.name = data.name.str.replace('.', '')

        # Extracting volunteers infos
        volunteers_infos = data.copy()
        volunteers_infos = volunteers_infos[['name', 'nb_perm', 'nb_surstaff', 'is_referent', 'last_perm']]
        volunteers_infos = volunteers_infos.rename(columns={'name': 'full_name'})

        # Extracting volunteers normal availabilities
        volunteers_availabilities = data.copy()
        volunteers_availabilities = volunteers_availabilities[['name', 'dispo_perm']]
        volunteers_availabilities = self.extractAvailabilities(volunteers_availabilities)

        volunteers_availabilities_df = pd.DataFrame(volunteers_availabilities.items())
        volunteers_availabilities_df.rename(columns={volunteers_availabilities_df.columns[0]: "full_name"},
                                            inplace=True)
        volunteers_availabilities_df.rename(columns={volunteers_availabilities_df.columns[1]: "availabilities"},
                                            inplace=True)


        # Generating list of possible normal shift
        availabilities_days = []

        for name, availabilities in volunteers_availabilities.items():
            for availability in availabilities:
                availabilities_days.append(availability)

        # Removing duplicates
        availabilities_days = list(set(availabilities_days))

        index = 0
        for day in availabilities_days:
            self.shifts.append(Shift(day, False, index))
            index += 1

        # Merging volunteers infos and availabilities
        vol_infos_availabilities = pd.merge(volunteers_infos, volunteers_availabilities_df, on='full_name')

        # Building the list of volunteers object
        for index, row in vol_infos_availabilities.iterrows():
            vol = Volunteer(index, row.full_name, row.nb_perm, row.nb_surstaff, row.is_referent, row.last_perm)
            vol.setAvailability(row.availabilities)
            self.volunteers.append(vol)

    def extractAvailabilities(self, availiability_df):

        # target days column
        availiability_df.columns = availiability_df.iloc[3]

        # renaming first column
        availiability_df.rename(columns={availiability_df.columns[0]: "name"}, inplace=True)

        # Target space before first name
        availiability_df.drop(availiability_df.index[0:4], inplace=True)
        availiability_df.reset_index(drop=True, inplace=True)
        availiability_df.dropna(subset=['name'], inplace=True)

        dispos_name = availiability_df.iloc[:, 0]
        dispos_dates = availiability_df.loc[:, availiability_df.columns != 'name']

        dates = dispos_dates.columns.tolist()
        dates_cleaned = [s.lstrip("0") for s in dates]

        dispos_dates.columns = dates_cleaned

        dispo_perm_clean = pd.concat([dispos_name, dispos_dates], axis=1)

        # Replace by column header value where TRUE
        dispo_perm_clean = dispo_perm_clean.where(dispo_perm_clean != "FALSE", dispo_perm_clean.columns.to_series(),
                                                  axis=1)
        dispo_perm_clean.reset_index(drop=True, inplace=True)

        volunteers_availiabities_dict = dispo_perm_clean.set_index('name').T.to_dict('list')
        cleaned_availiabilities_dict = {}

        for key, value in volunteers_availiabities_dict.items():
            cleaned_value = list(filter(lambda a: a not in ["TRUE"], value))
            cleaned_value = list(map(int, cleaned_value))
            cleaned_availiabilities_dict[key] = cleaned_value

        return cleaned_availiabilities_dict

    def getVolunteers(self):
        return self.volunteers

    def getShifts(self):
        return self.shifts

    def getTimeBreak(self):
        return self.time_break

    def getMaxDayShift(self):
        return max(self.shifts, key=lambda x: x.getDay())

    def getNextShift(self, index, amount):
        nextShifts = []

        for i in range(index, min(amount, len(self.shifts) - index)):
            nextShifts.append(self.shifts[i])

        return nextShifts
