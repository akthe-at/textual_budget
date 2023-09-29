import pandas as pd
from textual import events, on
from textual.app import App, ComposeResult
from textual.reactive import var
from textual.widgets import Button
from textual_pandas.widgets import DataFrameTable
from views.budget import BudgetCRUD, BudgetProgress
from views.categorize import CategorySelection, LabelTransactions
from views.main_screen import HomeScreen
from views.stats import SpendingStats
from views.upload_screen import UploadScreen


class ModesApp(App):
    CSS_PATH = "tcss/buttons.tcss"
    SCREENS = {
        "upload": UploadScreen(),
        "home": HomeScreen(),
        "categories": LabelTransactions(),
        "budget_review": BudgetProgress(),
        "budget_crud": BudgetCRUD(),
        "stats": SpendingStats(),
        "catpicker": CategorySelection(),
    }

    BINDINGS = {
        ("h", "action_push_screen('home')", "Home Page"),
    }

    SHOW_TREE = var(True)

    def compose(self) -> ComposeResult:
        yield HomeScreen(id="home_screen")

    def on_mount(self) -> None:
        self.title = "Textual Bank"
        self.sub_title = "Home Screen"

    def upload_dataframe(self, mode):
        filename = self.query_one("#file_name").value
        df = pd.read_csv(filename)
        table = self.query_one(DataFrameTable)
        table.update_df(df)
        table.cursor_type = next("row")

    @on(Button.Pressed, ".main.menu")
    def change_screen(self, event: Button.Pressed):
        self.push_screen(screen=event.button.id)

    @on(Button.Pressed, "#quit")
    def quit_buttons(self):
        self.exit()

    @on(Button.Pressed, "#cancel")
    def cancel_buttons(self):
        self.pop_screen()

    def on_data_table_row_selected(self, event: DataFrameTable.RowSelected):
        self.push_screen("catpicker")

    def on_key(self, event: events.Key) -> None:
        if event.key == "h":
            self.push_screen("home")


if __name__ == "__main__":
    app = ModesApp()
    app.run()
