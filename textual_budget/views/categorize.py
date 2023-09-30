import constants
from model.model import Model
from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Label
from textual_pandas.widgets import DataFrameTable


class CategorySelection(Screen):
    """Modal Screen for selecting transaction categories."""

    def compose(self) -> ComposeResult:
        yield Vertical(
            Label("How would you categorize this transaction?", id="question"),
            constants.CATEGORY_OPTIONS,
            Container(
                Button("Accept", variant="success", id="accept"),
                Button("Cancel", variant="primary", id="cancel"),
                classes="cat_buttons",
            ),
            id="dialog",
            classes="modal",
        )


class LabelTransactions(Screen):
    def __init__(self, model: Model):
        super().__init__()
        self.model = model

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield Button(label="Go Back", id="home")
        yield DataFrameTable()

    def on_mount(self) -> None:
        self.sub_title = "Monitor Income/Expenditure Transactions"
        table = self.query_one(DataFrameTable)
        table.cursor_type = "row"
        df = self.model.get_all_accounts(self)
        table.add_df(df)
