import sqlite3
from dataclasses import dataclass
from sqlite3 import Connection, Cursor

import pandas as pd


@dataclass
class Model:
    db_path: str = (
        "C:/Users/ARK010/Documents/textual_budget/textual_budget/model/dev.db"
    )
    con: Connection = sqlite3.connect(db_path)
    cursor: Cursor = con.cursor()

    def upload_dataframe(self, filepath):
        df = pd.read_csv(filepath)
        df = (
            df.assign(Processed="No")
            .rename(
                columns={
                    "Posted Date": "PostedDate",
                    "Check Number": "CheckNumber",
                }
            )
            .drop(columns="Unnamed: 10")
        )
        df.to_sql("MyAccounts", con=self.con, if_exists="replace", index=False)
        return True

    def update_category(self, category: str, row: str):
        ### Update the Category column with the new category value
        self.cursor.execute(
            "UPDATE MyAccounts SET Category = ? WHERE rowid = ?", (category, row)
        )
        self.con.commit()
        return True

    def get_all_accounts(self, con=con):
        df = pd.read_sql(
            """
            SELECT 
                AccountType, 
                PostedDate, 
                Amount, 
                Description, 
                Category, 
                Balance, 
                Processed
            FROM MyAccounts 
            WHERE Processed = 'No'
            ORDER BY PostedDate DESC
            """,
            con=con,
        )
        return df
