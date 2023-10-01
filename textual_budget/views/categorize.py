from constants_cat import SELECT_OPTIONS
from model.model import Model
from textual import on
from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.screen import ModalScreen, Screen
from textual.widgets import Button, Footer, Header, Label, Select
from textual_pandas.widgets import DataFrameTable


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

    @on(
        Select.Changed
    )  #! Move new_category capture to App level to pass to DataHandler?
    def investigate_options(self, event: Select.Changed):
        """When an option is selected, set the current category and focus on the accept button."""  # noqa: E501
        self.new_category = event.value
        self.query_one("#accept").focus()


class LabelTransactions(Screen):
    def __init__(self, model: Model):
        super().__init__()
        self.model = model

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield Button(label="Go Back", variant="warning", id="home")
        yield DataFrameTable()

    def on_mount(self) -> None:
        self.sub_title = "Monitor Income/Expenditure Transactions"
        table = self.query_one(DataFrameTable)
        table.cursor_type = "row"
        df = self.model.get_all_accounts(self)
        table.add_df(df)
        table.focus()
