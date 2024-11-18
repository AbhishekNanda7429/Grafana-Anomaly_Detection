import pandas as pd

class DataCleaner:
    def __init__(self, df):
        """
        Initializes the DataCleaner with a DataFrame.

        Parameters:
        df (pd.DataFrame): The input DataFrame to clean.
        """
        self.df = df

    def clean_data(self):
        """
        Cleans the DataFrame by dropping rows and columns with NaN values.

        Returns:
        pd.DataFrame: The cleaned DataFrame with no rows or columns containing NaN values.
        """
        # Drop rows and columns with NaN values
        cleaned_df = self.df.dropna(axis=0, how='any')  # Removes rows with NaN
        cleaned_df = cleaned_df.dropna(axis=1, how='any')  # Removes columns with NaN
        
        return cleaned_df
