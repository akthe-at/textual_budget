"""View for categorizing transactions."""

from typing import Self

from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.message import Message
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Button, DataTable, Footer, Header
from textual.widgets.data_table import ColumnKey, RowKey

from views.cat_modal import CategorySelection


class LabelTransactions(Screen):
    """Screen for categorizing transactions."""

    def __init__(self: Self) -> None:
        """Initialize the screen."""
        super().__init__()

    BINDINGS: set[tuple[str, str, str]] = {
        ("a", "accept_transaction()", "Accept Transaction"),
        ("f", "flag_transaction()", "Flag Transaction"),
        ("c", "categorize_transaction()", "Categorize Transaction"),
    }
    transaction_columns: reactive[list[ColumnKey]] = reactive(default=list[ColumnKey])

    class TableMounted(Message):
        """Message to let app know that the datatable was mounted."""

        def __init__(self: Self, table: DataTable) -> None:
            """Initialize the message that the table is mounted."""
            self.table = table
            super().__init__()

    class CategoryAccepted(Message):
        """Message to let app know that a category was accepted."""

        def __init__(
            self: Self,
            category: str,
            row_key: RowKey,
            table: DataTable,
        ) -> None:
            """Initialize the message with the category and row key."""
            self.category = category
            self.row_key = row_key
            self.table = table
            super().__init__()

    class CategorizeTransaction(Message):
        """Message to let app know that the transaction is being categorized."""

        def __init__(
            self: Self,
            row_key: RowKey,
            table: DataTable,
            current_category: str,
        ) -> None:
            """Initialize the message with the current category."""
            self.current_category = current_category
            self.row_key = row_key
            self.table = table
            super().__init__()

    class ProcessingStatusChange(Message):
        """Message to let app know that the processing status is changing to 'Yes'."""

        def __init__(self: Self, row_key: RowKey, table: DataTable, value: str) -> None:
            """Initialize the message with the value and row key."""
            self.value = value
            self.row_key = row_key
            self.table = table
            super().__init__()

    class FlagTransaction(Message):
        """Message to let app know that the transaction is being flagged."""

        def __init__(
            self: Self,
            row_key: RowKey,
            table: DataTable,
            value: str = "Flagged",
        ) -> None:
            """Initialize the message with the value and row key."""
            self.value = value
            self.row_key = row_key
            self.table = table
            super().__init__()

    def compose(self: Self) -> ComposeResult:
        """Compose the screen."""
        yield Header()
        yield Footer()
        with Horizontal(id="categorize_first_block"):
            yield Button(label="Go Back", id="home", classes="categorize")
        yield DataTable(id="transaction_data_table")

    def on_mount(self: Self) -> None:
        """Mount the screen."""
        self.sub_title = "Monitor Income/Expenditure Transactions"
        self.query_one("Header", expect_type=Header).tall = True
        self.table = self.query_one("#transaction_data_table", expect_type=DataTable)
        self.table.cursor_type = "row"
        self.post_message(message=self.TableMounted(table=self.table))
        self.table.focus()

    def change_status_to_processed(self: Self) -> None:
        """Change the status of the selected transaction to processed."""
        self.table.update_cell(
            row_key=self.current_highlighted_row,
            column_key=self.app.transaction_columns[6],
            value="Yes",
        )

    def change_status_to_flagged(self: Self) -> None:
        """Change the status of the selected transaction to flagged."""
        self.table.update_cell(
            row_key=self.current_highlighted_row,
            column_key=self.app.transaction_columns[7],
            value="Flagged",
        )
        self.table.refresh_row(
            row_index=self.table.get_row_index(
                row_key=self.current_highlighted_row,
            ),
        )

    def action_accept_transaction(self: Self) -> None:
        """Accept the selected transaction. Update UI & send message to update DB."""
        self.post_message(
            message=self.ProcessingStatusChange(
                row_key=self.current_highlighted_row,
                table=self.table,
                value="Yes",
            ),
        )
        self.change_status_to_processed()

    def action_categorize_transaction(self: Self) -> None:
        """Categorize the selected transaction via keybind."""
        self.post_message(
            message=DataTable.RowSelected(
                cursor_row=self.table.cursor_row,
                row_key=self.current_highlighted_row,
                data_table=self.table,
            )
        )

    def action_flag_transaction(self: Self) -> None:
        """Flag the selected transaction. Update UI & send message to update DB."""
        self.post_message(
            self.FlagTransaction(
                row_key=self.current_highlighted_row,
                table=self.table,
            ),
        )
        self.change_status_to_flagged()

    def update_data_table(self: Self, result: str) -> None:
        """Send a message to controller to update the category of the selected cell."""
        self.post_message(
            self.CategoryAccepted(
                category=result,
                row_key=self.current_row_key,
                table=self.table,
            ),
        )

    @on(message_type=DataTable.RowHighlighted, selector="#transaction_data_table")
    def store_highlighted_row(self, event: DataTable.RowHighlighted):
        """Store the row key of the highlighted row."""
        self.current_highlighted_row = event.row_key

    @on(message_type=DataTable.RowSelected, selector="#transaction_data_table")
    def on_data_table_row_selected(self: Self, event: DataTable.RowSelected) -> None:
        """Prompt the user to select a category for the selected cell."""
        self.current_row_key = event.row_key
        self.app.push_screen(
            screen=CategorySelection(
                row_values=event.data_table.get_row(
                    row_key=event.row_key,
                ),
            ),
            callback=self.update_data_table,
        )
