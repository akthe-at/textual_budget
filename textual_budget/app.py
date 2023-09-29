from collections import defaultdict

import pandas as pd
from textual.app import App, ComposeResult
from textual.reactive import var
from textual.widgets import Button
from textual_pandas.widgets import DataFrameTable

from kelly_bank.views.budget import BudgetCRUD, BudgetProgress
from kelly_bank.views.main_screen import HomeScreen
from kelly_bank.views.stats import SpendingStats
from kelly_bank.views.upload_screen import (
    CategorySelection,
    LabelTransactions,
    UploadScreen,
)


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
    SCREEN_BUTTON_MAP = defaultdict(
        None,
        {
            "upload": App.push_screen,
            "categories": App.push_screen,
            "budget_review": App.push_screen,
            "budget_crud": App.push_screen,
            "stats": App.push_screen,
        },
    )

    QUIT_BUTTON_MAP = defaultdict(
        None,
        {
            "cancel": App.action_pop_screen,
            "quit": App.exit,
        },
    )

    BINDINGS = {
        ("h", "push_screen('home')", "Home Page"),
    }

    SHOW_TREE = var(True)

    def compose(self) -> ComposeResult:
        yield HomeScreen(id="home_screen")
        yield CategorySelection(id="cat")

    def on_mount(self) -> None:
        self.title = "Kelly Bank"
        self.sub_title = "Home Screen"

    def upload_dataframe(self, mode):
        filename = self.query_one("#file_name").value
        df = pd.read_csv(filename)
        table = self.query_one(DataFrameTable)
        table.update_df(df)
        table.cursor_type = next("row")

    def on_button_pressed(
        self,
        event: Button.Pressed,
        SCREEN_BUTTON_MAP: defaultdict[str, callable] = SCREEN_BUTTON_MAP,
        QUIT_BUTTON_MAP: defaultdict[str, callable] = QUIT_BUTTON_MAP,
    ) -> None:
        # write a match case statement
        match event.button.id:
            case id_ if id_ in SCREEN_BUTTON_MAP:
                SCREEN_BUTTON_MAP[id_](self, screen=id_)
            case id_ if id_ in QUIT_BUTTON_MAP:
                QUIT_BUTTON_MAP[id_](self)

## !! BROKEN
    def on_key_enter(self):
        if DataFrameTable.RowHighlighted:
            self.action_push_screen(screen="catpicker")


if __name__ == "__main__":
    app = ModesApp()
    app.run()
