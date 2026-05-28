import pandas as pd


class BibleLoader:

    def __init__(self, csv_path: str):
        self.csv_path = csv_path
        self.df = None

    def load(self):

        self.df = pd.read_csv(self.csv_path)

        return self.df