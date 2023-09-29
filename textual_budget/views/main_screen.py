from textual.app import ComposeResult
from textual.containers import Center, Grid, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Static


class Menu(Static):
    def compose(self) -> ComposeResult:
        yield Grid(
            Vertical(
                Button("Upload Transactions", id="upload", classes="mainmenu"),
                Button("Categorize Transactions", id="categories", classes="mainmenu"),
                Button("Budget Progress", id="budget_review", classes="mainmenu"),
                classes="column",
            ),
            Vertical(
                Button("Budget CRUD", id="budget_crud", classes="mainmenu"),
                Button("Spending Statistics", id="stats", classes="mainmenu"),
                Button("Quit", id="quit"),
                classes="column",
            ),
        )


class HomeScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        with Center():
            yield Menu()

    def on_mount(self) -> None:
        self.sub_title = "Home Screen"
