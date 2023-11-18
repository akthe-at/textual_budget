from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.message import Message
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Button, DataTable, Footer, Header
from textual.widgets.data_table import ColumnKey

from views.cat_modal import CategorySelection


class LabelTransactions(Screen):
    def __init__(self):
        super().__init__()

    BINDINGS = {
        ("a", "accept_transaction()", "Accept Transaction"),
        ("f", "flag_transaction()", "Flag Transaction"),
    }
    transaction_columns: reactive[list[ColumnKey]] = reactive(default=list[ColumnKey])

    class TableMounted(Message):
        """Message to let app know that the datatable was mounted"""

        def __init__(self, table: DataTable):
            self.table = table
            super().__init__()

    class CategoryAccepted(Message):
        """Message to let app know that a category was accepted"""

        def __init__(self, category: str, row_key, table: DataTable):
            self.category = category
            self.row_key = row_key
            self.table = table
            super().__init__()

    class ProcessingStatusChange(Message):
        """Message to let app know that the processing status is changing to 'Yes'"""

        def __init__(self, row_key, table: DataTable, value: str):
            self.value = value
            self.row_key = row_key
            self.table = table
            super().__init__()

    class FlagTransaction(Message):
        """Message to let app know that the transaction is being flagged"""

        def __init__(self, row_key, table: DataTable, value: str = "Flagged"):
            self.value = value
            self.row_key = row_key
            self.table = table
            super().__init__()

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        with Horizontal(id="categorize_first_block"):
            yield Button(label="Go Back", id="home", classes="categorize")
        yield DataTable(id="transaction_data_table")

    def on_mount(self) -> None:
        self.sub_title = "Monitor Income/Expenditure Transactions"
        self.query_one("Header", expect_type=Header).tall = True
        self.table = self.query_one("#transaction_data_table", expect_type=DataTable)
        self.table.cursor_type = "row"
        self.post_message(self.TableMounted(self.table))
        self.table.focus()

    def change_status_to_processed(self):
        """Change the status of the selected transaction to processed."""
        self.table.update_cell(
            row_key=self.current_highlighted_row,
            column_key=self.transaction_columns[6],
            value="Yes",
        )

    def change_status_to_flagged(self):
        """Change the status of the selected transaction to flagged."""
        self.table.update_cell(
            row_key=self.current_highlighted_row,
            column_key=self.transaction_columns[7],
            value="Flagged",
        )
        self.table.refresh_row(self.table.get_row_index(self.current_highlighted_row))

    def action_accept_transaction(self):
        """Accept the selected transaction. Update UI & send message to update DB"""
        self.post_message(
            self.ProcessingStatusChange(
                row_key=self.current_highlighted_row,
                table=self.table,
                value="Yes",
            )
        )
        self.change_status_to_processed()

    def action_flag_transaction(self):
        """Flag the selected transaction. Update UI & send message to update DB"""
        self.post_message(
            self.FlagTransaction(row_key=self.current_highlighted_row, table=self.table)
        )
        self.change_status_to_flagged()

    def update_data_table(self, result: str) -> None:
        """Send a message to controller to update the category of the selected cell."""
        self.post_message(
            self.CategoryAccepted(
                category=result, row_key=self.current_row_key, table=self.table
            )
        )

    @on(DataTable.RowHighlighted, "#transaction_data_table")
    def store_highlighted_row(self, event: DataTable.RowHighlighted):
        """Store the row key of the highlighted row."""
        self.current_highlighted_row = event.row_key

    @on(DataTable.RowSelected, "#transaction_data_table")
    def on_data_table_row_selected(self, event: DataTable.RowSelected):
        """Prompt the user to select a category for the selected cell."""
        self.current_row_key = event.row_key
        self.app.push_screen(
            screen=CategorySelection(
                row_values=event.data_table.get_row(event.row_key)
            ),
            callback=self.update_data_table,
        )

