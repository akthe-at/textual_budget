import constants
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Label
from textual_pandas.widgets import DataFrameTable

# Example Data, not meant to be here forever.
ROWS = [
    ("lane", "swimmer", "country", "time"),
    (4, "Joseph Schooling", "Singapore", 50.39),
    (2, "Michael Phelps", "United States", 51.14),
    (5, "Chad le Clos", "South Africa", 51.14),
    (6, "László Cseh", "Hungary", 51.14),
    (3, "Li Zhuhao", "China", 51.26),
    (8, "Mehdy Metella", "France", 51.58),
    (7, "Tom Shields", "United States", 51.73),
    (1, "Aleksandr Sadovnikov", "Russia", 51.84),
    (10, "Darren Burns", "Scotland", 51.84),
]


class CategorySelection(Screen):
    """Modal Screen for selecting transaction categories."""

    def compose(self) -> ComposeResult:
        yield Vertical(
            Label("How would you categorize this transaction?", id="question"),
            constants.CATEGORY_OPTIONS,
            Button("Accept", variant="success", id="accept"),
            Button("Cancel", variant="primary", id="cancel"),
            id="dialog",
        )


class LabelTransactions(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield Button(label="Go Back", id="home")
        yield DataFrameTable()

    def on_mount(self) -> None:
        self.sub_title = "Monitor Income/Expenditure Transactions"
        table = self.query_one(DataFrameTable)
        table.cursor_type = "row"
        table.add_columns(*ROWS[0])
        table.add_rows(ROWS[1:])
