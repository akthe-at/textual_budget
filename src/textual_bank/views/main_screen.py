from textual.app import ComposeResult
from textual.containers import Center, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header


class HomeScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        with Vertical(id="left_column", classes="mainmenu"):
            with Center(id="left_center_menu"):
                yield Button("Upload Transactions", id="upload", classes="mainmenu")
                yield Button(
                    "Categorize Transactions", id="categories", classes="mainmenu"
                )
                yield Button("Budget Progress", id="budget_review", classes="mainmenu")
        with Vertical(id="right_column", classes="mainmenu"):
            with Center(id="right_center_menu"):
                yield Button("Budget CRUD", id="budget_crud", classes="mainmenu")
                yield Button("Spending Statistics", id="stats", classes="mainmenu")
                yield Button("Quit", id="quit")

    def on_mount(self) -> None:
        self.sub_title = "Home Screen"
        self.query_one("Header", expect_type=Header).tall = True

