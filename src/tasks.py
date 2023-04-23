import pandas as pd
from pandas import DataFrame


def analyzer(old_file_path: str, df: DataFrame, logger):
    """
    Compare old and new DataFrame and divides into incomming and outgoing
    partners
    """

    logger.info('[+] Start analyzer')

    try:
        old_df = pd.read_csv(old_file_path, index_col=False, dtype=str)
    except Exception:
        old_df = df
    new_df = df

    print('(1) ===> ', old_df)
    print('(2) ===> ', new_df)

    control_df = pd.concat([old_df, new_df], ignore_index=True)
    print('(6) ===> ', control_df)
    control_df_no_duplicates = control_df.drop_duplicates(
                                                          subset='PARK_ID',
                                                          keep="first",
                                                          ignore_index=True
                                                         )

    print('(3) ===> ', control_df_no_duplicates)

    if control_df_no_duplicates is not None:
        arrivals_partners_df = pd.concat(
                                         [control_df_no_duplicates, old_df],
                                         ignore_index=True
                                        )
        arrivals_partners_df_no_duplicates = arrivals_partners_df.drop_duplicates(
                                         subset='PARK_ID',
                                         keep=False,
                                         ignore_index=True
                                        )
        left_partners_df = pd.concat(
                                     [control_df_no_duplicates, new_df],
                                     ignore_index=True
                                    )
        left_partners_df_no_duplicates = left_partners_df.drop_duplicates(
                                         subset='PARK_ID',
                                         keep=False,
                                         ignore_index=True
                                        )

        print('(4) ===> ', arrivals_partners_df_no_duplicates)
        print('(5) ===> ', left_partners_df_no_duplicates)

        arrivals_file_path = old_file_path.split('.')[0] + '_arrivals.csv'
        left_file_path = old_file_path.split('.')[0] + '_left.csv'

        open(arrivals_file_path, 'w').close()
        open(left_file_path, 'w').close()

        logger.debug('[+] Arrivals and left analizator')

        if arrivals_partners_df_no_duplicates is not None:
            arrivals_partners_df_no_duplicates.to_csv(
                                                path_or_buf=arrivals_file_path
                                                    )
        if left_partners_df_no_duplicates is not None:
            left_partners_df_no_duplicates.to_csv(
                                                path_or_buf=left_file_path
                                                )
