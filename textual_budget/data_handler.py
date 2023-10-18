from dataclasses import dataclass

from model.model import Model


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

    def upload_dataframe(self, filepath: str):
        """Upload a csv file to the database."""
        success = self.model.upload_dataframe(filepath)
        if success:
            return True

    def update_category(self, new_category, row):
        """Update the category of a transaction based on user input."""
        old_category = row[4]
        description = row[3]
        posted_date = row[1]
        amount = row[2]
        balance = row[5]
        success = self.model.update_category(
            new_category,
            old_category,
            description,
            posted_date,
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

    def update_processing_status(self, row):
        category = row[4]
        description = row[3]
        posted_date = row[1]
        amount = row[2]
        balance = row[5]
        success = self.model.update_status(
            category, description, posted_date, amount, balance
        )
        if success:
            return True
        else:
            print("failed to update - from DataHandler")

    def update_budget_item(self, row: list) -> bool | str:
        id = row[0]
        category = row[1]
        month = row[2]
        year = row[3]
        goal = row[4]
        active = row[5]
        success = self.model.update_existing_goals(
            category=category,
            month=month,
            year=year,
            goal=goal,
            active=active,
            id=id,
        )
        if success:
            return True
        else:
            print("Failed to update category from datahandler)")

    def flag_transaction(self, row):
        category = row[4]
        description = row[3]
        posted_date = row[1]
        amount = row[2]
        balance = row[5]
        success = self.model.flag_transaction(
            category, description, posted_date, amount, balance
        )
        if success:
            return True
        else:
            print("failed to update - from DataHandler")

    def save_new_budget_item(self, category, amount, month, year, active):
        success = self.model.insert_new_goals(category, amount, month, year, active)
        if success:
            return True
        else:
            print("Failed to Save new Budget Item to DB- From DataHandler")
