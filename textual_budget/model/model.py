import sqlite3
from dataclasses import dataclass
from sqlite3 import Connection, Cursor

import pandas as pd


@dataclass
class Model:
    db_path: str = (
        "C:/Users/ARK010/Documents/textual_budget/textual_budget/model/dev.db"
    )
    conn: Connection = sqlite3.connect(db_path)
    cursor: Cursor = conn.cursor()

    def __post_init__(self):
        ...
        # self.connect_to_db()

    # def connect_to_db(self) -> Connection:
    #     self.conn = sqlite3.connect(self.db_path)
    #     self.cursor = self.conn.cursor()

    # upload pandas dataframe to database
    def upload_dataframe(self, filepath):
        df = pd.read_csv(filepath)
        df.to_sql("MyAccounts", con=self.conn, if_exists="replace", index=False)
        self.conn.close()

    def get_all_accounts(self):
        self.cursor.execute("SELECT * FROM MyAccounts")
        df = pd.read_sql("SELECT * FROM MyAccounts", self.conn)
        self.conn.close()
        return df
