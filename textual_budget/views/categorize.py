from constants_cat import SELECT_OPTIONS
from textual import events, on
from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.message import Message
from textual.screen import ModalScreen, Screen
from textual.widgets import Button, Footer, Header, Label, Select
from textual_pandas.widgets import DataTable


class CategorySelection(ModalScreen):
    """Modal Screen for selecting transaction categories."""

    def __init__(self, row_values: list):
        super().__init__(row_values)
        self.row_values = row_values
        self.transaction_description = self.row_values[3]
        self.current_category = self.row_values[4]

    def compose(self) -> ComposeResult:
        yield Vertical(
            Label(
                f"How would you categorize {self.transaction_description}?",
                id="question",
            ),
            Select(
                options=SELECT_OPTIONS,
                id="category_list",
                prompt="Select Category",
            ),
            Container(
                Button("Accept", variant="success", id="accept"),
                Button("Cancel", variant="primary", id="cancel"),
                classes="cat_buttons",
            ),
            id="dialog",
            classes="modal",
        )

    def on_mount(self) -> None:
        self.sub_title = "Select Category"
        self.query_one("#category_list").expanded = True

    @on(Button.Pressed, "#accept")
    def on_accept(self):
        """Send category and row to DataHandler for updating the database."""
        self.dismiss(result=self.query_one(Select).value)


class LabelTransactions(Screen):
    def __init__(self):
        super().__init__()

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

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield Button(label="Go Back", variant="warning", id="home")
        yield DataTable(id="data_table")

    def on_mount(self) -> None:
        self.sub_title = "Monitor Income/Expenditure Transactions"
        self.table = self.query_one(DataTable)
        self.table.cursor_type = "row"
        self.post_message(self.TableMounted(self.table))
        self.table.focus()

    @on(DataTable.RowSelected)
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
        self.result = result
        self.post_message(
            self.CategoryAccepted(
                category=result, row_key=self.current_row_key, table=self.table
            )
        )

        # .refresh_row(
        #     self.query_one(DataTable).get_row_index(self.current_row_key)
        # )
