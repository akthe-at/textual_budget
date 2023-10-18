import sqlite3
from dataclasses import dataclass
from sqlite3 import Connection, Cursor

import numpy as np
import pandas as pd


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
        Balance=lambda x: x.Balance.str.replace("$", "")
        .str.replace("(", "-")
        .str.replace(")", "")
        .str.replace(",", "")
        .astype("float64"),
        Flagged="",
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

    def flag_transaction(self, category, description, posted_date, amount, balance):
        """Update the processing status of a transaction."""
        self.cursor.execute(
            """UPDATE MyAccounts
            SET Flagged = 'Flagged'
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
            print("FAILED TO UPDATE FLAG STATUS")
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
    Processed,
    Flagged
FROM MyAccounts 
WHERE Processed = 'No'
ORDER BY PostedDate DESC
"""
        )
        unprocessed_data = self.cursor.fetchall()
        return unprocessed_data

    ####################
    ####################
    # BUDGET GOAL CRUD #
    ####################
    ####################

    # BudgetGoals Schema = id, Category, Month, Year, Goal, Active
    # cursor.execute('CREATE TABLE budget_goals (id INTEGER PRIMARY KEY AUTOINCREMENT, category TEXT NOT NULL, month TEXT NOT NULL, year INTEGER NOT NULL, goal DECIMAL(10,2) NOT NULL, active BOOLEAN NOT NULL);')

    def retrieve_all_goals(self):
        """Retrieve all goals from the database."""
        self.cursor.execute(
            """
            SELECT
                id,
                category,
                month,
                year,
                goal,
                active
            FROM budget_goals
            """
        )
        goals = self.cursor.fetchall()
        return goals

    def retrieve_active_goals(self):
        """Retrieve all active goals from the database."""
        self.cursor.execute(
            """
            SELECT
                id,
                category,
                month,
                year,
                goal,
                active
            FROM budget_goals
            WHERE active = TRUE
            """
        )
        goals = self.cursor.fetchall()
        return goals

    def insert_new_goals(
        self, category: str, month: str, year: int, amount: int, active: bool
    ):
        """Insert new goals into the database."""
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS budget_goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            month TEXT,
            year INTEGER,
            goal INTEGER,
            active INTEGER
            )
            """
        )
        self.cursor.execute(
            """
            INSERT INTO budget_goals 
            (category, month, year, goal, active)
            VALUES (?, ?, ?, ?, ?)""",
            (category, month, year, amount, active),
        )
        self.con.commit()

    def update_existing_goals(
        self, category: str, month: str, year: int, goal: int, active: bool, id: int
    ) -> None:
        """Update existing goals"""
        print(category, month, year, goal, active, id)
        self.cursor.execute(
            """
            UPDATE budget_goals
            SET category = ?,
            month = ?,
            year = ?,
            goal = ?,
            active = ?
            WHERE id = ?
            """,
            (category, month, year, goal, active, id),
        )
        self.con.commit()

        # !!! UPDATE OLD GOALS TRIGGER - this isn't actually suppposed to be a function, just run once
        """
        CREATE TRIGGER deactivate_old_budget_goals
        AFTER INSERT ON `budget_goals` FOR EACH ROW
        BEGIN
        UPDATE budget_goals SET active = FALSE
        WHERE category = NEW.category
        AND NOT (id = NEW.id);
        END
        """


##########################
##########################
## CATEGORY AGGREGATION ##
##########################
##########################
