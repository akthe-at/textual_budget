from dataclasses import dataclass
from pathlib import Path

from model.model import Model
from textual import events, on
from textual.app import App, ComposeResult
from textual.reactive import var
from textual.widgets import Button, OptionList
from textual_pandas.widgets import DataFrameTable
from views.categorize import CategorySelection
from views.main_screen import HomeScreen

from constants_app import BINDINGS, SCREENS


class Controller(App):
    def __init__(self, model: Model):
        super().__init__()
        self.model = model
        self.data_handler = DataHandler(self, model)

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

    @on(Button.Pressed, ".mainmenu")
    def change_screen(self, event: Button.Pressed):
        """Pushes a new screen based on button pressed while on the main menu only."""
        self.push_screen(screen=event.button.id)
        # self.query_one("#category_list")

    @on(Button.Pressed, "#quit")
    def quit_buttons(self):
        """Closes the application for any buttons with the id of quit."""
        self.exit()

    @on(DataFrameTable.RowSelected)
    def on_data_table_row_selected(self, event: DataFrameTable.RowSelected):
        """Prompt the user to select a category for the selected cell."""
        self.push_screen(CategorySelection(event.data_table.get_row(event.row_key)))

    @on(Button.Pressed, "#upload_transactions")
    def on_upload_dataframe(self, event: Button.Pressed):
        """Send filepath to DataHandler for uploading to database."""
        filepath = Path(self.query_one("#file_name").value)
        self.data_handler.upload_dataframe(event, filepath)

    @on(Button.Pressed, "#accept")
    def on_accept(self, event: Button.Pressed):
        """Send category and row to DataHandler for updating the database."""
        # self.data_handler.update_category( # ! Method Not Implemented Yet
        #     category=self.current_category, row=self.current_row_selected
        # )
        self.pop_screen()

    @on(Button.Pressed, "#cancel")
    def cancel_buttons(self):
        self.pop_screen()

    def on_option_list_option_selected(self, event: OptionList.OptionSelected):
        self.current_category = event.option
        self.query_one("#accept").focus()


@dataclass
class DataHandler:
    """An interface between the Model and the Controller"""

    controller: Controller
    model: Model

    def upload_dataframe(self, event, filepath: str):
        success = self.model.upload_dataframe(filepath)
        if success:
            print("success!")

    # def update_category(self, category: OptionList.OptionSelected, row):
    #     print(category)
    #     success = self.model.update_category(category, row=row)
    #     if success:
    #         print("successfully updated the category")


if __name__ == "__main__":
    model = Model()
    app = Controller(model)
    app.run()
