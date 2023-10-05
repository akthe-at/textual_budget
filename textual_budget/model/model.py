import sqlite3
from dataclasses import dataclass
from sqlite3 import Connection, Cursor

import pandas as pd


# TODO: Add Message from App to Model to close DataBase connection on App exit.
@dataclass
class Model:
    """Data model for the application."""

    db_path: str = (
        "C:/Users/ARK010/Documents/textual_budget/textual_budget/model/dev.db"
    )
    con: Connection = sqlite3.connect(db_path)
    cursor: Cursor = con.cursor()

    def upload_dataframe(self, filepath):
        """Upload a csv file to the database."""
        df = pd.read_csv(filepath)
        df = df.assign(Processed="No").rename(
            columns={
                "Posted Date": "PostedDate",
                "Check Number": "CheckNumber",
            }
        )
        df.to_sql("MyAccounts", con=self.con, index=False, if_exists="replace")
        return True

    def update_category(
        self,
        category: str,
        old_category: str,
        description: str,
        posted_date: str,
        amount: float,
        balance: float,
    ):
        """Update the category of a transaction."""
        self.cursor.execute(
            """UPDATE MyAccounts 
            SET Category = ?, Processed = 'Yes'
            WHERE Category = ? 
            AND Description = ?
            AND PostedDate = ?
            AND Amount = ?
            AND Balance = ?
            """,
            (
                category,
                old_category,
                description,
                posted_date,
                amount,
                balance,
            ),
        )
        try:
            self.con.commit()
        except Exception:
            self.con.rollback()
            print("FAILED TO UPDATE CATEGORY")
        return True

    def get_unprocessed_transactions(self):
        """Retrieve all unprocessed records from database."""
        self.cursor.execute(
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
"""
        )
        unprocessed_data = self.cursor.fetchall()
        return unprocessed_data
