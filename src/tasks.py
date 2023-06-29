import pandas as pd
from pandas import DataFrame


class Analyzer:
    """ A class containing a data analysis method.

    Attributes:
        old_file_path: Old parser data from file.
        df: New parser DataFrame.
        column: Column label for drop duplicates.
        logger: Logger from script.

    Methods:
        get_differents: Compare old and new DataFrame and divides into
            incomming and outgoing partners.
    """

    def __init__(self, old_file_path, df: DataFrame, column, logger):
        """ Initialize the instance.

        Args:
            old_file_path: Old parser data from file.
            df: New parser DataFrame.
            column: Column label for drop duplicates.
            logger: Logger from script.
        """
        self.old_file_path = old_file_path
        self.df = df
        self.column = column
        self.logger = logger

    def get_differents(self):
        """
        Compare old and new DataFrame and divides into incomming and
        outgoing partners.
        """
        self.logger.info('[+] Start analyzer')

        try:
            old_df = pd.read_csv(
                            self.old_file_path,
                            index_col=False,
                            dtype=str
                            )
        except Exception:
            # At the first launch, since there is no <old_df>.
            old_df = self.df
            self.logger.info(
                        '[+] The old file is either empty or does not exist.')
        new_df = self.df

        # Control set - combining sets of old and new data.
        control_df = pd.concat([old_df, new_df], ignore_index=True)
        control_df_no_duplicates = control_df.drop_duplicates(
                                                            subset=self.column,
                                                            keep="first",
                                                            ignore_index=True
                                                            )

        if control_df_no_duplicates is not None:
            # New data set - the difference between the control set and
            # the set of old data.
            new_partners_df = pd.concat(
                                             [
                                                 control_df_no_duplicates,
                                                 old_df
                                             ],
                                             ignore_index=True
                                            )
            new_partners_df_no_duplicates = new_partners_df.drop_duplicates(
                                             subset=self.column,
                                             keep=False,
                                             ignore_index=True
                                            )
            # Left data set - the difference between the control set and
            # the set of new data.
            left_partners_df = pd.concat(
                                         [control_df_no_duplicates, new_df],
                                         ignore_index=True
                                        )
            left_partners_df_no_duplicates = left_partners_df.drop_duplicates(
                                             subset=self.column,
                                             keep=False,
                                             ignore_index=True
                                            )

            new_file_path = self.old_file_path.split('.')[0] + \
                f'_new_{self.column}.csv'

            left_file_path = self.old_file_path.split('.')[0] + \
                f'_left_{self.column}.csv'

            # Create a file if it has not been created before.
            open(new_file_path, 'w').close()
            open(left_file_path, 'w').close()

            if new_partners_df_no_duplicates is not None:
                new_partners_df_no_duplicates.to_csv(
                                            path_or_buf=new_file_path,
                                            index=False
                                                        )
            if left_partners_df_no_duplicates is not None:
                left_partners_df_no_duplicates.to_csv(
                                            path_or_buf=left_file_path,
                                            index=False
                                                    )

        self.logger.info('[+] Stop analyzer')
