import sqlite3
from dataclasses import dataclass
from pathlib import Path
from sqlite3 import Connection, Cursor, OperationalError
from typing import Any

import pandas as pd
from pandas.errors import DatabaseError


def tweak_incoming_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Clean up incoming DataFrame.

    Args:
    df (pd.DataFrame): Incoming DataFrame

    >>> df = pd.DataFrame(
    ...     {
    ...         "Posted Date": ["2021-01-01", "2021-01-02", "2021-01-03"],
    ...         "Description": ["desc1", "desc2", "desc3"],
    ...         "Amount": ["$1.00", "$2.00", "$3.00"],
    ...         "Balance": ["$1.00", "$2.00", "$3.00"],
    ...         "Category": ["cat1", "cat2", "cat3"],
    ...         "Labels": ["", "", ""],
    ...         "Note": ["", "", ""],
    ...     }
    ... )

        >>> tweak_incoming_dataframe(df)
        AccountNumber AccountType PostedDate  Amount Description Check Number  \
        0            1    Checking 2021-01-01     1.0       desc1          NaN
        1            1    Checking 2021-01-02     2.0       desc2          NaN
        2            1    Checking 2021-01-03     3.0       desc3          NaN

        Balance Category Labels Note Processed Flagged
        0      1.0     cat1            No
        1      2.0     cat2            No
        2      3.0     cat3            No


    Returns:
    df (pd.DataFrame): Cleaned up DataFrame

    """
    return df.assign(
        Processed="No",
        Category=lambda x: x.Description.case_when(
            caselist=[
                (
                    x.Description.str.contains("dividend paid", case=False),
                    "Money towards savings",
                ),
                (x.Description.str.contains("netflix.com", case=False), "Netflix"),
                (
                    x.Description.str.contains("schnucks", case=False),
                    "Groceries/House Supplies",
                ),
                (x.Description.str.contains("animal hospitals", case=False), "Dog"),
                (
                    x.Description.str.contains("google storage", case=False),
                    "Google Storage",
                ),
                (
                    x.Description.str.contains("tmobile", case=False),
                    "T-Mobile Internet",
                ),
                (x.Description.str.contains("autozone", case=False), "Car Expenses"),
                (
                    x.Description.str.contains("ach:discover -e-payment", case=False),
                    "Discover Card",
                ),
                (
                    x.Description.str.contains(
                        "ach:jpmorgan chase -chase ach",
                        case=False,
                    ),
                    "JPMorgan Chase - Mortgage",
                ),
                (
                    x.Description.str.contains("small wonders", case=False),
                    "Daycare expenses",
                ),
                (
                    x.Description.str.contains("university of wi -dir dep", case=False),
                    "Adam Paycheck",
                ),
                (
                    x.Description.str.contains("ach:black & veatch", case=False),
                    "Nicole Paycheck",
                ),
                (x.Description.str.contains("Gas / Fuel", case=False), "Gas"),
                (
                    x.Description.str.contains("Transfer", case=False),
                    "Money towards savings",
                ),
                (x.Description.str.contains("Dining Out", case=False), "Eating Out"),
                (x.Description.str.contains("Doctor", case=False), "Medical"),
                (x.Description.str.contains("Veterinary", case=False), "Dog"),
                (
                    x.Description.str.contains("Auto Insurance", case=False),
                    "Auto Insurance",
                ),
                (pd.Series(True, index=x.index), x.Description),
            ],
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
    """Data model for the application.

    Attributes:
    db_path (str): The path to the database.
    con (Connection): The connection to the database.
    cursor (Cursor): The cursor to the database.

        >>> model = Model()

    """

    db_path: str = "the_bank.db"
    con: Connection = sqlite3.connect(db_path)
    cursor: Cursor = con.cursor()

    def upload_dataframe(self, filepath: str | Path) -> bool:
        """Upload a csv file to the database."""
        df: pd.DataFrame = pd.read_csv(filepath, parse_dates=["Posted Date"])
        df_refined: pd.DataFrame = (
            df.loc[df["Posted Date"] >= "2024-10-01"]
            .rename(columns={"Posted Date": "PostedDate"})
            .groupby(["Description", "PostedDate"])
            .agg("first")
        )
        df_filtered: pd.DataFrame = self.compare_dataframes(df_new=df_refined)
        df_final: pd.DataFrame = tweak_incoming_dataframe(df_filtered)
        df_final.to_sql("MyAccounts", con=self.con, index=False, if_exists="append")
        return True

    def compare_dataframes(self, df_new: pd.DataFrame) -> pd.DataFrame:
        """Compares the two dataframes to avoid adding duplicate data"""
        try:
            df_old = pd.read_sql("select * from MyAccounts", self.con)
        except DatabaseError:
            return df_new.reset_index()
        df_old = (
            df_old.assign(PostedDate=lambda x: pd.to_datetime(x.PostedDate))
            .groupby(["Description", "PostedDate"])
            .agg("first")
        )
        df_filtered = (df_new.loc[(~df_new.index.isin(df_old.index))]).reset_index()
        return df_filtered[
            [
                "AccountNumber",
                "AccountType",
                "PostedDate",
                "Amount",
                "Description",
                "Check Number",
                "Category",
                "Balance",
                "Labels",
                "Note",
            ]
        ]

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
                """
            UPDATE MyAccounts
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
            """
        UPDATE MyAccounts
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
                """
            UPDATE MyAccounts 
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
        Balance 
            Description, 
            Category, 
            Amount,
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

    def retrieve_active_goals(self) -> list[Any]:
        """Retrieve all active goals from the database."""
        # try to execute the query, if it fails, return none.
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
        except Exception as e:
            print(f"Failed to retrieve active goals: {e}")
            raise DatabaseError("Failed to retrieve active goals") from e

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
            "SELECT name FROM sqlite_master WHERE type='trigger' AND name='deactivate_old_budget_goals'"
        )
        if self.cursor.fetchone() is None:
            self.cursor.execute(
                """
            CREATE TRIGGER deactivate_old_budget_goals
            AFTER INSERT ON `budget_goals` FOR EACH ROW
            BEGIN
            UPDATE budget_goals SET active = FALSE
            WHERE category = NEW.category
            AND NOT (id = NEW.id);
            END
                """
            )
        self.cursor.execute(
            """
        INSERT INTO budget_goals 
        (category, goal, active, date_added)
        VALUES (?, ?, ?, ?)
            """,
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

    ##########################
    ##########################
    ## CATEGORY AGGREGATION ##
    ##########################
    ##########################

    def retrieve_month_bwd_progress(
        self, number_of_months: int
    ) -> list[tuple[int, int, int, str, str]]:
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
            and strftime('%Y-%m', date('now', '-' || ? || ' month')) = strftime('%Y-%m', acct.PostedDate)
        GROUP BY acct.Category, strftime('%Y-%m', acct.PostedDate)
        order by strftime('%y-%m', acct.posteddate) desc, acct.category
        """,
            (str(number_of_months)),
        )
        items = self.cursor.fetchall()
        return items

    def retrieve_month_fwd_progress(
        self, number_of_months: int
    ) -> list[tuple[int, int, int, str, str]]:
        self.cursor.execute(
            """
        select
        bg.goal as "goal",
        sum(acct.amount) as "actual",
        sum(acct.amount) - bg.goal as "difference",
        acct.Category,
        strftime('%Y-%m', acct.PostedDate)
        FROM MyAccounts acct
        INNER JOIN budget_goals bg
            on bg.category = acct.Category
        WHERE bg.active = 1
            and acct.Processed = 'Yes'
            and strftime('%Y-%m', date('now', + ? || 'month')) = strftime('%Y-%m', acct.PostedDate)
        GROUP BY acct.Category, strftime('%Y-%m', acct.PostedDate)
        ORDER BY strftime('%Y-%m', acct.PostedDate) DESC, acct.Category
        """,
            (str(number_of_months)),
        )
        items = self.cursor.fetchall()
        return items

    def retrieve_budget_progress(self) -> list[tuple[int, int, int, str, str]] | None:
        try:
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
                and strftime('%Y-%m', date('now')) = strftime('%Y-%m', acct.PostedDate)
            GROUP BY acct.Category, strftime('%Y-%m', acct.PostedDate)
            ORDER BY strftime('%Y-%m', acct.PostedDate) DESC, acct.Category
    """
            )
            budget_progress = self.cursor.fetchall()
            return budget_progress
        except OperationalError:
            print("FAILED TO RETRIEVE BUDGET PROGRESS TABLE")
            return None

    def retrieve_all_budget_progress(self):
        try:
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
        except OperationalError:
            print("FAILED TO RETRIEVE ALL BUDGET PROGRESS TABLE")
            return False
