from typing import Any, Iterable
from dataclasses import dataclass
from datetime import datetime
from model.model import Model
from pathlib import Path


@dataclass
class DataHandler:
    """An interface between the Model and the Controller"""

    model: Model

    def query_transactions_from_db(self):
        """Query all unprocessed transactions from the database."""
        return self.model.get_unprocessed_transactions()

    def query_budget_items_from_db(self) -> list[str, str, int, int, bool]:
        """Query all budget items from the database."""
        return self.model.retrieve_all_goals()

    def query_active_budget_items_from_db(self) -> list[str, str, int, int, bool]:
        """Query all active budget items from the database."""
        return self.model.retrieve_active_goals()

    def query_budget_progress_from_db(self):
        """Query all budget progress from the database."""
        return self.model.retrieve_budget_progress()

    def delete_item_from_db(self, id):
        """Delete a budget item from the database."""
        success = self.model.delete_goal(id)
        if success:
            return True
        else:
            print("Failed to delete category from datahandler)")

    def upload_dataframe(self, filepath: str | Path):
        """Upload a csv file to the database."""
        success = self.model.upload_dataframe(filepath)
        if success:
            return True

    def update_category(self, new_category, row):
        """Update the category of a transaction based on user input."""
        old_category = row[4]
        description = row[3]
        amount = row[2]
        balance = row[5]
        success = self.model.update_category(
            new_category,
            old_category,
            description,
            amount,
            balance,
        )
        if success:
            return True

    def close_database_connection(self):
        """Close the database connection."""
        success = self.model.close_database_connection()
        if success:
            return True
        else:
            print("Failed to close the database connection properly")

    def update_processing_status(self, row, value):
        category = row[4]
        description = row[3]
        amount = row[2]
        balance = row[5]
        status = value
        flagged = row[7]
        success = self.model.update_status(
            category, description, amount, balance, status, flagged
        )
        if success:
            return True
        else:
            print("failed to update - from DataHandler")

    def update_budget_item(self, row: list) -> bool | str:
        timestamp = datetime.strftime(datetime.now(), "%Y-%m-%d")
        id = row[0]
        category = row[1]
        goal = row[2]
        active = row[3]
        success = self.model.update_existing_goals(
            category=category,
            goal=goal,
            active=active,
            timestamp=timestamp,
            id=id,
        )
        if success:
            return True
        else:
            print("Failed to update category from datahandler)")

    def flag_transaction(self, row):
        category = row[4]
        description = row[3]
        amount = row[2]
        balance = row[5]
        success = self.model.flag_transaction(category, description, amount, balance)
        if success:
            return True
        else:
            print("failed to update - from DataHandler")

    def save_new_budget_item(self, category, amount, active):
        timestamp = datetime.strftime(datetime.now(), "%Y-%m-%d")
        success = self.model.insert_new_goals(category, amount, active, timestamp)
        if success:
            return True
        else:
            print("Failed to Save new Budget Item to DB- From DataHandler")

    def cycle_months(self, number_of_months: int) -> Iterable[Iterable[Any]]:
        """Cycle the progress table x months backward"""
        if number_of_months < 0:
            return self.model.retrieve_month_bwd_progress(
                number_of_months=abs(number_of_months)
            )
        elif number_of_months == 0:
            return self.model.retrieve_budget_progress()
        return self.model.retrieve_month_fwd_progress(number_of_months=number_of_months)

