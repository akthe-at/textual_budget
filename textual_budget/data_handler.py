from dataclasses import dataclass

from model.model import Model


@dataclass
class DataHandler:
    """An interface between the Model and the Controller"""

    model: Model

    def query_transactions_from_db(self):
        """Query all unprocessed transactions from the database."""
        return self.model.get_unprocessed_transactions()

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


