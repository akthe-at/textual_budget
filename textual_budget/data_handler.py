from dataclasses import dataclass

from model.model import Model


@dataclass
class DataHandler:
    """An interface between the Model and the Controller"""

    model: Model

    def query_transactions_from_db(self):
        """Query all unprocessed transactions from the database."""
        return self.model.get_unprocessed_transactions()

    def upload_dataframe(self, event, filepath: str):
        """Upload a csv file to the database."""
        success = self.model.upload_dataframe(filepath)
        if success:
            return True

    def update_category(self, new_category, row):
        self.old_category = row[4]
        self.description = row[3]
        self.posted_date = row[1]
        amount = row[2]
        balance = row[5]
        """Update the category of a transaction based on user input."""
        success = self.model.update_category(
            new_category,
            self.old_category,
            self.description,
            self.posted_date,
            amount,
            balance,
        )
        if success:
            print("successfully updated the category in the DataBase")
            return True
