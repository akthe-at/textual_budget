from dataclasses import dataclass
from pathlib import Path

from constants import BINDINGS, SCREENS
from model.model import Model
from textual import events, on
from textual.app import App, ComposeResult
from textual.reactive import var
from textual.widgets import Button
from textual_pandas.widgets import DataFrameTable
from views.main_screen import HomeScreen


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

    @on(Button.Pressed, ".main.menu")
    def change_screen(self, event: Button.Pressed):
        self.push_screen(screen=event.button.id)

    @on(Button.Pressed, "#quit")
    def quit_buttons(self):
        self.exit()

    @on(Button.Pressed, "#cancel")
    def cancel_buttons(self):
        self.pop_screen()

    @on(DataFrameTable.RowSelected)
    def on_data_table_row_selected(self):
        self.push_screen("catpicker")

    def on_key(self, event: events.Key) -> None:
        if event.key == "h":
            self.push_screen("home")

    @on(Button.Pressed, "#upload_transactions")
    def on_upload_dataframe(self, event: Button.Pressed):
        filepath = Path(self.query_one("#file_name").value)
        self.data_handler.upload_dataframe(event, filepath)


@dataclass
class DataHandler:
    """An interface between the Model and the Controller"""

    controller: Controller
    model: Model

    def upload_dataframe(self, event, filepath: str):
        success = self.model.upload_dataframe(filepath)
        if success:
            print("success")
        else:
            print("failure")


if __name__ == "__main__":
    model = Model()
    app = Controller(model)
    app.run()
