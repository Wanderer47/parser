import pandas as pd
from pandas import DataFrame


def analizator(old_file_path: str, df: DataFrame, logger):
    """
    Compare old and new DataFrame and divides into incomming and outgoing
    partners
    """
    old_df = pd.read_csv(old_file_path, low_memory=True)
    new_df = df

    control_df = pd.concat([old_df, new_df])
    control_df.drop_duplicates()

    arrivals_partners_df = pd.concat([control_df, old_df])
    arrivals_partners_df.drop_duplicates()
    left_partners_df = pd.concat([control_df, new_df])
    left_partners_df.drop_duplicates()

    arrivals_file_path = old_file_path.split('.')[0] + '_arrivals.csv'
    left_file_path = old_file_path.split('.')[0] + '_left.csv'

    open(arrivals_file_path, 'w').close()
    open(left_file_path, 'w').close()

    logger.debug('arrivals and left analizator')

    arrivals_partners_df.to_csv(path_or_buf=arrivals_file_path)
    left_partners_df.to_csv(path_or_buf=left_file_path)
