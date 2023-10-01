import sqlite3
from dataclasses import dataclass
from sqlite3 import Connection, Cursor

import pandas as pd


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
        self.con.close()
        return True

    def get_unprocessed_transactions(self, con=con):
        """Get all accounts from the database."""
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
