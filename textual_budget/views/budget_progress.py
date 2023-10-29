from textual import on
from textual.app import ComposeResult
from textual.message import Message
from textual.screen import Screen
from textual.widgets import Button, DataTable, Footer, Header
from datetime import datetime


class BudgetProgress(Screen):
    def __init__(self):
        self.current_month = datetime.now().month
        self.derived_month = datetime.now().month
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Header()
        yield Button(label="Cycle Forward 1 Month", id="month_fwd_button")
        yield Button(label="Cycle Backward 1 Mon", id="month_bwd_button")
        yield DataTable(id="budget_progress_table")
        yield Footer()

    class ProgressTableMounted(Message):
        "Message app to indicate that the budget progress table has been mounted"

        def __init__(self, table: DataTable):
            self.table = table
            super().__init__()

    class CycleForward(Message):
        """Message to cycle forward the month/table"""

        def __init__(self, table: DataTable, number_of_months: int):
            self.table = table
            self.number_of_months: int = number_of_months
            super().__init__()

    class CycleBackward(Message):
        """Message to cycle backward the month/table"""

        def __init__(self, table: DataTable, number_of_months: int):
            self.table = table
            self.number_of_months: int = number_of_months
            super().__init__()

    def on_mount(self) -> None:
        self.sub_title = "Monitor Budget"
        self.table = self.query_one("#budget_progress_table")
        self.table.cursor_type = "row"
        self.post_message(self.ProgressTableMounted(table=self.table))

    @property
    def number_of_months(self):
        return self.derived_month - self.current_month

    @on(Button.Pressed, "#month_fwd_button")
    def cycle_forward(self):
        self.derived_month += 1
        self.post_message(
            self.CycleForward(table=self.table, number_of_months=self.number_of_months)
        )

    @on(Button.Pressed, "#month_bwd_button")
    def cycle_backward(self):
        self.derived_month -= 1
        self.post_message(
            self.CycleBackward(table=self.table, number_of_months=self.number_of_months)
        )
