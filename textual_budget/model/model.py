import sqlite3
from dataclasses import dataclass
from sqlite3 import Connection, Cursor

import numpy as np
import pandas as pd


# TODO: Compile a base list of .str.replace() to start to auto"categorize" transactions
def tweak_incoming_dataframe(df: pd.DataFrame):
    """Clean up incoming DataFrame"""
    return df.assign(
        Processed="No",
        Category=lambda x: np.select(
            [
                (x.Description.str.contains("netflix.com", case=False)),
                (x.Description.str.contains("schnucks", case=False)),
                (x.Description.str.contains("animal hospitals", case=False)),
                (x.Description.str.contains("google storage", case=False)),
                (x.Description.str.contains("tmobile", case=False)),
                (x.Description.str.contains("autozone", case=False)),
                (x.Description.str.contains("ach:discover -e-payment", case=False)),
                (
                    x.Description.str.contains(
                        "ach:jpmorgan chase -chase ach", case=False
                    )
                ),
                (x.Description.str.contains("small wonders", case=False)),
                (x.Description.str.contains("university of wi -dir dep", case=False)),
                (x.Description.str.contains("ach:black & veatch", case=False)),
                (x.Category.str.contains("Gas / Fuel", case=False)),
                (x.Category.str.contains("Transfer", case=False)),
                (x.Category.str.contains("Dining Out", case=False)),
                (x.Category.str.contains("Doctor", case=False)),
                (x.Category.str.contains("Veterinary", case=False)),
                (x.Category.str.contains("Auto Insurance", case=False)),
            ],
            [
                "Netflix",
                "Groceries/House Supplies",
                "Dog",
                "Google Storage",
                "T-Mobile Internet",
                "Car Expenses",
                "Discover Card",
                "JPMorgan Chase - Mortgage",
                "Daycare expenses",
                "Adam Paycheck",
                "Nicole Paycheck",
                "Gas",
                "Money towards savings",
                "Eating Out",
                "Medical",
                "Dog",
                "Progressive Insurance",
            ],
            x.Category,
        ),
        Amount=lambda x: x.Amount.str.replace("$", "")
        .str.replace("(", "-")
        .str.replace(")", "")
        .str.replace(",", "")
        .astype("float64"),
    ).rename(
        columns={
            "Posted Date": "PostedDate",
            "Check Number": "CheckNumber",
        }
    )


@dataclass
class Model:
    """Data model for the application."""

    db_path: str = (
        "C:/Users/ARK010/Documents/textual_budget/textual_budget/model/dev.db"
    )
    con: Connection = sqlite3.connect(db_path)
    cursor: Cursor = con.cursor()

    def upload_dataframe(self, filepath: str):
        """Upload a csv file to the database."""
        df = pd.read_csv(filepath)
        df = tweak_incoming_dataframe(df)
        df.to_sql("MyAccounts", con=self.con, index=False, if_exists="replace")
        return True

    def close_database_connection(self):
        """Close the database connection."""
        self.con.close()
        return True

    def update_status(self, category, description, posted_date, amount, balance):
        """Update the processing status of a transaction."""
        self.cursor.execute(
            """UPDATE MyAccounts
            SET Processed = 'Yes'
            WHERE Category = ?
            AND Description = ?
            AND PostedDate = ?
            AND Amount = ?
            AND Balance = ?
            """,
            (category, description, posted_date, amount, balance),
        )
        try:
            self.con.commit()
        except Exception:
            self.con.rollback()
            print("FAILED TO UPDATE CATEGORY")
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
