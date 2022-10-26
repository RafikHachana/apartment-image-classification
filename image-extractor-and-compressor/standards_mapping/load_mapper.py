import pandas as pd
import utilities


def get_mapper():
    filename = utilities.get_csv_filename_for_mapper()
    data = pd.read_csv(f'./standards_mapping/{filename}.csv')
    result_mapper = {}
    for index, row in data.iterrows():
        result_mapper[row.word.upper()] = row.standard
    return result_mapper
