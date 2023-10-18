from datetime import datetime

from constants_cat import SELECT_OPTIONS
from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.message import Message
from textual.screen import Screen
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Input,
    RadioButton,
    Select,
)


class UpdateBudgetItem(Screen):
    """Screen for updating a budget item"""

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical():
            yield Input(id="update_item_id", disabled=True)
            yield Select(
                options=SELECT_OPTIONS,
                prompt="Select a Category",
                id="update_item_category",
            )
            yield Input(id="update_item_month")
            yield Input(id="update_item_year")
            yield Input(id="update_item_goal")
            yield RadioButton(
                value=False, label="Active Goal?", id="update_item_status"
            )
            yield Button("Accept", id="accept_budget_update")
        yield Footer()

    def on_mount(self) -> None:
        self.sub_title = "Update a Budget Item"

    @on(Button.Pressed, "#accept_budget_update")
    def on_accept(self):
        """Accept new budget item"""
        self.dismiss(
            result=[
                self.query_one("#update_item_id").value,
                self.query_one("#update_item_category").value,
                self.query_one("#update_item_month").value,
                self.query_one("#update_item_year").value,
                self.query_one("#update_item_goal").value,
                self.query_one("#update_item_status").value,
            ]
        )
        self.query_one("#update_item_status").value = False


class CreateBudgetItem(Screen):
    """Screen for creating a budget item."""

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
            yield RadioButton(
                value=True,
                label="Active Goal?",
                id="active_status_switch",
            )
            yield Button("Accept", id="create_item")
        yield Footer()

    def on_mount(self) -> None:
        self.sub_title = "Create a Budget Item"

    @on(Button.Pressed, "#create_item")
    def on_accept(self):
        """Accept new budget item"""
        self.dismiss(
            result=[
                self.query_one("#budget_item_category").value,
                self.query_one("#budget_item_amount").value,
                self.query_one("#budget_item_month").value,
                self.query_one("#budget_item_year").value,
                self.query_one("#active_status_switch").value,
            ]
        )


class BudgetCRUD(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Button(label="Go Back", variant="warning", id="home")
        with Horizontal():
            yield Button(
                "Retrieve Current Budget Goals", id="retrieve_active_budget_items"
            )
            yield Button("Retrieve All Budget Goals", id="retrieve_all_budget_items")
            yield Button("Create New Budget Goal", id="create_budget_item")
            yield Button("Update Existing Budget Goal", id="update_budget_item")
        yield DataTable(id="budget_data_table")
        yield Footer()

    class BudgetTableMounted(Message):
        """Message to let app know that the datatable was mounted"""

        def __init__(self, table: DataTable):
            self.table = table
            super().__init__()

    class FilterBudgetTable(Message):
        """Message App to filter Budget Item Table"""

        def __init__(self, table: DataTable, Active: bool):
            self.table: DataTable = table
            self.active: bool = Active
            super().__init__()

    def on_mount(self) -> None:
        self.sub_title = "Establish Budget"
        self.table = self.query_one("#budget_data_table")
        self.table.cursor_type = "row"
        self.post_message(self.BudgetTableMounted(table=self.table))

    def save_budget_item(self, result: list):
        """Send message to app to save the budget item to the database"""
        self.post_message(self.SaveBudgetItem(row_data=result))

    def update_budget_item(self, result: list):
        """Send message to app to save updated budget items"""
        self.post_message(self.SaveBudgetItemUpdate(result=result, table=self.table))

    @on(Button.Pressed, "#retrieve_active_budget_items")
    def retrieve_active_budget_items(self, event: Button.Pressed):
        """Retrieve all active budget items"""
        self.post_message(self.FilterBudgetTable(table=self.table, Active=True))

    @on(Button.Pressed, "#retrieve_all_budget_items")
    def retrieve_all_budget_items(self, event: Button.Pressed):
        """Retrieve all budget items"""
        self.post_message(self.FilterBudgetTable(table=self.table, Active=False))

    class SaveBudgetItem(Message):
        """Message to let app know that a category was accepted"""

        def __init__(self, row_data: list):
            self.item_category = row_data[0]
            self.item_amount = row_data[1]
            self.item_month = row_data[2]
            self.item_year = row_data[3]
            self.active_status = row_data[4]

            super().__init__()

    class StartBudgetItemUpdate(Message):
        """Message to let app know that a category was accepted"""

        def __init__(self, row_data: list):
            self.row_data: list = row_data

            super().__init__()

    class SaveBudgetItemUpdate(Message):
        """Message to let app know that a category was accepted"""

        def __init__(self, result: list, table: DataTable):
            self.result: list = result
            self.table: DataTable = table
            super().__init__()

    @on(Button.Pressed, "#create_budget_item")
    def budget_creation_screen(self):
        self.app.push_screen(screen=CreateBudgetItem(), callback=self.save_budget_item)

    @on(DataTable.RowHighlighted, "#budget_data_table")
    def store_highlighted_row(self, event: DataTable.RowHighlighted):
        """Store the row key of the highlighted row."""
        self.current_row_selected = event.row_key
        self.row_data = event.data_table.get_row(event.row_key)

    @on(Button.Pressed, "#update_budget_item")
    def budget_update_screen(self, event: Button.Pressed):
        """Push the update budget item screen to the app."""
        self.post_message(self.StartBudgetItemUpdate(row_data=self.row_data))
        self.app.push_screen(
            screen=UpdateBudgetItem(), callback=self.update_budget_item
        )
