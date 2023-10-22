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
        df = pd.read_csv(filepath, parse_dates=["Posted Date"])
        df = tweak_incoming_dataframe(df)
        df.to_sql("MyAccounts", con=self.con, index=False, if_exists="replace")
        return True

    def close_database_connection(self):
        """Close the database connection."""
        self.con.close()
        return True

    def update_status(self, category, description, amount, balance, processed, flagged):
        """Update the processing status of a transaction."""
        print(
            f"UPDATE STATUS: {category, description, amount, balance, processed, flagged}"
        )
        try:
            self.cursor.execute(
                """UPDATE MyAccounts
                SET Processed = ?
                WHERE Category = ?
                AND Description = ?
                AND Amount = ?
                AND Balance = ?
                AND Flagged = ?
                """,
                (
                    processed,
                    category,
                    description,
                    amount,
                    balance,
                    flagged,
                ),
            )
            self.con.commit()
        except Exception:
            self.con.rollback()
            print("FAILED TO UPDATE CATEGORY")
        return True

    def flag_transaction(self, category, description, amount, balance):
        """Update the processing status of a transaction."""
        self.cursor.execute(
            """UPDATE MyAccounts
            SET Flagged = 'Flagged'
            WHERE Category = ?
            AND Description = ?
            AND Amount = ?
            AND Balance = ?
            """,
            (category, description, amount, balance),
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
        amount: float,
        balance: float,
    ):
        """Update the category of a transaction."""
        try:
            self.cursor.execute(
                """UPDATE MyAccounts 
                SET Category = ?, Processed = 'Yes'
                WHERE Category = ? 
                AND Description = ?
                AND Amount = ?
                AND Balance = ?
                """,
                (
                    category,
                    old_category,
                    description,
                    amount,
                    balance,
                ),
            )
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
    strftime('%Y-%m-%d', PostedDate), 
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
    def delete_goal(self, id):
        """Delete a goal from the database."""
        try:
            self.cursor.execute(
                """
                DELETE FROM budget_goals
                WHERE id = ?
                """,
                (id,),
            )
        except Exception:
            self.con.rollback()
            print("FAILED TO DELETE GOAL")
        self.con.commit()
        return True

    def retrieve_all_goals(self):
        """Retrieve all goals from the database."""
        self.cursor.execute(
            """
            SELECT
                id,
                category,
                goal,
                active,
                date_added,
                date_modified
            FROM budget_goals
            ORDER BY category, active DESC
            """
        )
        goals = self.cursor.fetchall()
        return goals

    def retrieve_active_goals(self):
        """Retrieve all active goals from the database."""
        # try to execuse the query, if it fails, do nothing
        try:
            self.cursor.execute(
                """
                SELECT
                    id,
                    category,
                    goal,
                    active,
                    date_added,
                    date_modified
                FROM budget_goals
                WHERE active = TRUE
                ORDER BY category, active DESC
                """
            )

            goals = self.cursor.fetchall()
            return goals
        except Exception:
            pass

    def insert_new_goals(
        self, category: str, amount: int, active: bool, timestamp: str
    ):
        """Insert new goals into the database."""
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS budget_goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            goal INTEGER,
            active INTEGER,
            date_added TEXT,
            date_modified TEXT
            )
            """
        )
        self.con.commit()
        self.cursor.execute(
            """
            INSERT INTO budget_goals 
            (category, goal, active, date_added)
            VALUES (?, ?, ?, ?)""",
            (category, amount, active, timestamp),
        )
        self.con.commit()

    def update_existing_goals(
        self, category: str, goal: int, active: bool, timestamp: str, id: int
    ) -> None:
        """Update existing goals"""
        self.cursor.execute(
            """
            UPDATE budget_goals
            SET category = ?,
            goal = ?,
            active = ?,
            date_modified = ?
            WHERE id = ?
            """,
            (category, goal, active, timestamp, id),
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

    def retrieve_budget_progress(self):
        self.cursor.execute(
            """
SELECT
bg.goal as "Goal", 
SUM(acct.Amount) as "Actual",
SUM(acct.Amount) - bg.goal as "Difference",
acct.Category, 
strftime('%Y-%m', acct.PostedDate) 
FROM MyAccounts acct 
INNER JOIN budget_goals bg 
    on bg.category = acct.Category 
WHERE bg.active = 1 
    and acct.Processed = 'Yes' 
    and strftime('%Y-%m', date('now', '-1 month')) = strftime('%Y-%m', acct.PostedDate)
GROUP BY acct.Category, strftime('%Y-%m', acct.PostedDate)
ORDER BY strftime('%Y-%m', acct.PostedDate) DESC, acct.Category
"""
        )
        budget_progress = self.cursor.fetchall()
        return budget_progress

    def retrieve_all_budget_progress(self):
        self.cursor.execute(
            """
    SELECT
    bg.goal as "Goal", 
    SUM(acct.Amount) as "Actual",
    SUM(acct.Amount) - bg.goal as "Difference",
    acct.Category, 
    strftime('%Y-%m', acct.PostedDate) 
    FROM MyAccounts acct 
    INNER JOIN budget_goals bg 
        on bg.category = acct.Category 
    WHERE bg.active = 1 
        and acct.Processed = 'Yes' 
    GROUP BY acct.Category, strftime('%Y-%m', acct.PostedDate)
    ORDER BY strftime('%Y-%m', acct.PostedDate) DESC, acct.Category
    """
        )
        budget_progress = self.cursor.fetchall()
        return budget_progress