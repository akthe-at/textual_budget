from dataclasses import dataclass
from datetime import datetime
from types import CellType
from typing import Any, Optional
from model.model import Model
from pathlib import Path


@dataclass
class DataHandler:
    """An interface between the Model and the Controller"""

    model: Model

    def query_transactions_from_db(self):
        """Query all unprocessed transactions from the database."""
        return self.model.get_unprocessed_transactions()

    def query_budget_items_from_db(self) -> list:
        """Query all budget items from the database."""
        return self.model.retrieve_all_goals()

    def query_active_budget_items_from_db(self) -> list[Any]:
        """Query all active budget items from the database."""
        return self.model.retrieve_active_goals()

    def query_budget_progress_from_db(self):
        """Query all budget progress from the database."""
        return self.model.retrieve_budget_progress()

    def delete_item_from_db(self, db_id: int) -> Optional[bool]:
        """Delete a budget item from the database.

        Args:
        db_id (int): The id of the budget item to be deleted.

        Returns:
        True if the deletion was successful, None otherwise.

        """
        success = self.model.delete_goal(db_id)
        if success:
            return True
        else:
            print("Failed to delete category from datahandler)")

    def upload_dataframe(self, filepath: str | Path):
        """Upload a csv file to the database."""
        success = self.model.upload_dataframe(filepath)
        if success:
            return True

    def update_category(self, new_category: str, row: list[Any]):
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

    def update_processing_status(self, row: list[CellType], value: str) -> bool | None:
        category = row[4]
        description = row[3]
        amount = row[2]
        balance = row[5]
        processed = value
        flagged = row[7]
        success = self.model.update_status(
            category, description, amount, balance, processed, flagged
        )
        if success:
            return True
        else:
            print("failed to update - from DataHandler")

    def update_budget_item(self, row: list) -> bool | None:
        """Update a budget item in the database.
        Args:
            row: A list containing the data to be updated.

        Returns:
        True if the update was successful, None otherwise.
        """
        timestamp = datetime.strftime(datetime.now(), "%Y-%m-%d")
        db_id = row[0]
        category = row[1]
        goal = row[2]
        active: bool = row[3]
        success = self.model.update_existing_goals(
            category=category,
            goal=goal,
            active=active,
            timestamp=timestamp,
            db_id=db_id,
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

    def save_new_budget_item(self, category: str, amount: int, active: bool) -> bool:
        timestamp: str = datetime.strftime(datetime.now(), "%Y-%m-%d")
        success = self.model.insert_new_goals(category, amount, active, timestamp)
        if success:
            return True
        print("Failed to Save new Budget Item to DB- From DataHandler")
        return False

    def cycle_months(
        self, number_of_months: int
    ) -> list[tuple[int, int, int, str, str]] | None:
        """Cycle the progress table x months backward"""
        if number_of_months < 0:
            return self.model.retrieve_month_bwd_progress(
                number_of_months=abs(number_of_months)
            )
        elif number_of_months == 0:
            return self.model.retrieve_budget_progress()
        return self.model.retrieve_month_fwd_progress(number_of_months=number_of_months)
