import os

import pandas as pd


def analizator(parks_list, csv_res_path):
    df = pd.read_csv(csv_res_path, usecols = ['PARK_ID'], low_memory = True)

