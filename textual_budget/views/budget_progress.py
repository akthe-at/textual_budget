from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Footer, Header, Placeholder


class BudgetProgress(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Placeholder("This is where Budget Stuff would go")
        yield Footer()

    def on_mount(self) -> None:
        self.sub_title = "Monitor Budget"
