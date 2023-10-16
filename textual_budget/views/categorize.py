from textual import on
from textual.app import ComposeResult
from textual.message import Message
from textual.screen import Screen
from textual.widgets import Button, Footer, Header
from textual_pandas.widgets import DataTable

from views.cat_modal import CategorySelection


class LabelTransactions(Screen):
    def __init__(self):
        super().__init__()

    BINDINGS = {
        ("a", "accept_transaction()", "Accept Transaction"),
    }

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

        def __init__(self, row_key, table: DataTable, value: str = "Yes"):
            self.value = value
            self.row_key = row_key
            self.table = table
            super().__init__()

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield Button(label="Go Back", variant="warning", id="home")
        yield DataTable(id="transaction_data_table")

    def on_mount(self) -> None:
        self.sub_title = "Monitor Income/Expenditure Transactions"
        self.table = self.query_one("#transaction_data_table")
        self.table.cursor_type = "row"
        self.post_message(self.TableMounted(self.table))
        self.table.focus()

    @on(DataTable.RowHighlighted, "#transaction_data_table")
    def store_highlighted_row(self, event: DataTable.RowHighlighted):
        """Store the row key of the highlighted row."""
        self.current_highlighted_row = event.row_key

    def change_status_to_processed(self):
        """Change the status of the selected transaction to processed."""
        self.table.update_cell(
            row_key=self.current_highlighted_row,
            column_key=self.app.transaction_columns[6],
            value="Yes",
        )

    def action_accept_transaction(self):
        """Accept the selected transaction. Update UI & send message to update DB"""
        self.post_message(
            self.ProcessingStatusChange(
                row_key=self.current_highlighted_row, table=self.table
            )
        )
        self.change_status_to_processed()

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

    def update_data_table(self, result: str) -> None:
        """Send a message to controller to update the category of the selected cell."""
        self.post_message(
            self.CategoryAccepted(
                category=result, row_key=self.current_row_key, table=self.table
            )
        )
