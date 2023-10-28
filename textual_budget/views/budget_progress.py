from textual.app import ComposeResult
from textual.message import Message
from textual.screen import Screen
from textual.widgets import Button, DataTable, Footer, Header


class BudgetProgress(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Button(id="month_forward_button")
        yield DataTable(id="budget_progress_table")
        yield Footer()

    class ProgressTableMounted(Message):
        "Message app to indicate that the budget progress table has been mounted"

        def __init__(self, table: DataTable):
            self.table = table
            super().__init__()

    class CycleForward(Message):
        """Message to cycle forward the month/table"""

        ...

    def on_mount(self) -> None:
        self.sub_title = "Monitor Budget"
        self.table = self.query_one("#budget_progress_table")
        self.table.cursor_type = "row"
        self.post_message(self.ProgressTableMounted(table=self.table))
