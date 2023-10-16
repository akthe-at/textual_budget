from datetime import datetime

from constants_cat import SELECT_OPTIONS
from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen, Screen
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Input,
    Placeholder,
    Select,
)

ROWS = [
    ("Category", "Amount", "Month", "Year", "Active"),
    ("Phone", -150, "March", 2023, False),
    ("Home Renovation", -400, "March", 2023, True),
    ("Groceries", -1000, "March", 2023, True),
    ("Dog", -500, "February", 2023, False),
    ("Medical", -100, "March", 2023, True),
    ("Gas", -400, "March", 2023, True),
    ("Mortgage", -1300, "March", 2023, True),
]


class CreateBudgetItem(Screen):
    """Modal Screen for creating a budget item."""

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical():
            yield Select(
                options=SELECT_OPTIONS, id="budget_item_category", prompt="Category"
            )
            yield Input(id="budget_item_amount", placeholder="Amount")
            yield Input(
                id="budget_item_month", placeholder=datetime.now().strftime("%B")
            )
            yield Input(
                id="budget_item_year", placeholder=datetime.now().strftime("%Y")
            )
            yield Button("Accept", id="accept_item")
        yield Footer()

    def on_mount(self) -> None:
        self.sub_title = "Create a Budget Item"

    @on(Button.Pressed, "#accept_item")
    def on_accept(self):
        """Accept new budget item"""
        self.dismiss()


class BudgetProgress(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Placeholder("This is where Budget Stuff would go")
        yield Footer()

    def on_mount(self) -> None:
        self.sub_title = "Monitor Budget"


class BudgetCRUD(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Button(label="Go Back", variant="warning", id="home")
        with Horizontal():
            yield Button(
                "Retrieve Current Budget Goals", id="retrieve_budget_items"
            )  #! Filter Data Table by Active == True
            yield Button(
                "Retrieve All Budget Goals", id="retrieve_all_budget_items"
            )  #! No Active Filter
            yield Button("Create New Budget Goal", id="create_budget_item")
            yield Button(
                "Update Existing Budget Goal", id="update_budget_item"
            )  #! Modal with ability to update the fields
        yield DataTable(id="budget_data_table")
        yield Footer()

    def on_mount(self) -> None:
        self.sub_title = "Establish Budget"
        table = self.query_one("#budget_data_table")
        table.cursor_type = "row"
        table.add_columns(
            "Category",
            "Amount",
            "Month",
            "Year",
            "Active",
        )
        table.add_rows(ROWS[1:])

    @on(Button.Pressed, "#create_budget_item")
    def budget_creation_modal(self):
        self.app.push_screen(screen=CreateBudgetItem())
