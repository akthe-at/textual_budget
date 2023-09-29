import sqlite3
from dataclasses import dataclass, field
from sqlite3 import Connection, Cursor

import pandas as pd


@dataclass
class Model:
    db_path: str = (
        "C:/Users/ARK010/Documents/textual_budget/textual_budget/model/dev.db"
    )
    con: Connection = sqlite3.connect(db_path)
    cursor: Cursor = con.cursor()

    # def connect_to_db(self) -> Connection:
    #     self.conn = sqlite3.connect(self.db_path)
    #     self.cursor = self.conn.cursor()

    # upload pandas dataframe to database
    def upload_dataframe(self, filepath):
        df = pd.read_csv(filepath)
        df = df.assign(Processed="No")
        df.to_sql("MyAccounts", con=self.con, if_exists="replace", index=False)

    def get_all_accounts(self, con=con):
        df = pd.read_sql("SELECT * FROM MyAccounts WHERE Processed = 'No'", con=con)
        return df
