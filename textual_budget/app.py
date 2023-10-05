from dataclasses import dataclass
from pathlib import Path

from constants_app import BINDINGS, SCREENS
from data_handler import DataHandler
from model.model import Model
from textual import events, on
from textual.app import App, ComposeResult
from textual.reactive import var
from textual.widgets import Button, Select
from views.categorize import CategorySelection, LabelTransactions
from views.main_screen import HomeScreen


class Controller(App):
    def __init__(self, model: Model, data_handler: DataHandler):
        super().__init__()
        self.model = model
        self.data_handler = data_handler

    CSS_PATH = "tcss/buttons.tcss"
    SCREENS = SCREENS
    BINDINGS = BINDINGS
    SHOW_TREE = var(True)

    def compose(self) -> ComposeResult:
        yield HomeScreen(id="home_screen")

    def on_mount(self) -> None:
        self.title = "Textual Bank"
        self.sub_title = "Home Screen"

    def on_key(self, event: events.Key) -> None:
        if event.key == "h":
            self.push_screen("home")

    @on(LabelTransactions.TableMounted)
    def get_data_for_table(self, event: LabelTransactions.TableMounted):
        """Query the database for all unprocessed transactions and add them to the table."""
        unprocessed_data = self.data_handler.query_transactions_from_db()
        event.table.add_columns(
            "AccountType",
            "PostedDate",
            "Amount",
            "Description",
            "Category",
            "Balance",
            "Processed",
        )
        event.table.add_rows(unprocessed_data[0:])

    @on(Select.Changed)
    def investigate_options(self, event: Select.Changed):
        """When an option is selected, set the current category
        and set focus on the accept button."""  # noqa: E501
        self.new_category = event.value
        self.query_one("#accept").focus()

    @on(Button.Pressed, "#upload_transactions")
    def on_upload_dataframe(self, event: Button.Pressed):
        """Send filepath to DataHandler for uploading to database."""
        filepath = Path(self.query_one("#file_name").value)
        self.data_handler.upload_dataframe(event, filepath)

    @on(Button.Pressed, "#cancel")
    def cancel_buttons(self):
        self.pop_screen()

    @on(Button.Pressed, "#categories")
    def on_categories(self):
        self.push_screen("categories")

    @on(Button.Pressed, ".mainmenu")
    def change_screen(self, event: Button.Pressed):
        """Pushes a new screen based on button pressed while on the main menu only."""
        self.push_screen(screen=event.button.id)

    @on(Button.Pressed, "#quit")
    def quit_buttons(self):
        """Closes the application for any buttons with the id of quit."""
        self.exit()

    @on(LabelTransactions.CategoryAccepted)
    def update_data_table(self, event: LabelTransactions.CategoryAccepted):
        """Update the category of the selected row in the database."""
        self.data_handler.update_category(
            new_category=event.category,
            row=event.table.get_row(event.row_key),
        )
        event.table.update_cell(
            row_key=event.row_key,
            column_key="Category",
            value=event.category,
        )
        event.table.update_cell(
            row_key=event.row_key,
            column_key="Processed",
            value="Yes",
        )
        event.table.remove_row(event.row_key)


if __name__ == "__main__":
    model = Model()
    data_handler = DataHandler(model)
    app = Controller(model, data_handler)
    app.run()
