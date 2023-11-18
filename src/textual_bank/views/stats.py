from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Footer, Header, Placeholder


class SpendingStats(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Placeholder("This is where spendings stats would go")
        yield Footer()

    def on_mount(self) -> None:
        self.sub_title = "Monitor Spending/Savings Habits"
