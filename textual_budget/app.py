from pathlib import Path

from textual import events, on
from textual.app import App, ComposeResult
from textual.reactive import var
from textual.widgets import Button, Select

from constants_app import BINDINGS, SCREENS
from data_handler import DataHandler
from model.model import Model
from views.budget import BudgetCRUD
from views.budget_progress import BudgetProgress
from views.categorize import LabelTransactions
from views.main_screen import HomeScreen

# create a function that adds two numbers


class Controller(App):
    def __init__(self, model: Model, data_handler: DataHandler):
        super().__init__()
        self.model = model
        self.data_handler = data_handler

    CSS_PATH = "tcss/buttons.tcss"
    SCREENS = SCREENS
    BINDINGS = BINDINGS
    SHOW_TREE = var(True)

    def compose(self) -> ComposeResult:
        yield HomeScreen(id="home_screen")

    def on_mount(self) -> None:
        self.title = "Textual Bank"
        self.sub_title = "Home Screen"

    def on_key(self, event: events.Key) -> None:
        if event.key == "h":
            self.push_screen("home")

    ####################################################################################
    ############### Event Handlers Below, Class Definitions above ######################
    ####################################################################################

    @on(Select.Changed, "#category_list")
    def select_new_category(self, event: Select.Changed):
        """When an option is selected, set category & set focus on the accept button."""
        self.new_category = event.value
        self.query_one("#accept").focus()

    @on(LabelTransactions.ProcessingStatusChange)
    def update_processing_status_in_db(
        self, event: LabelTransactions.ProcessingStatusChange
    ):
        """Inform DataHandler of changes needed in the DB for processing status."""
        self.data_handler.update_processing_status(
            row=event.table.get_row(event.row_key),
            value=event.value,
        )

    @on(LabelTransactions.FlagTransaction)
    def flag_transaction(self, event: LabelTransactions.FlagTransaction):
        """Inform DataHandler of changes needed in the DB for flagged status."""
        self.data_handler.flag_transaction(row=event.table.get_row(event.row_key))

    @on(BudgetProgress.ProgressTableMounted)
    def get_aggregate_table_data(self, event: BudgetProgress.ProgressTableMounted):
        """Query the DB for all unprocessed transactions and add them to the table."""
        progress_data = self.data_handler.query_budget_progress_from_db()
        if progress_data:
            event.table.add_columns(
                "Goal", "Actual", "Difference", "Category", "Month/Year"
            )
            event.table.add_rows(progress_data[0:])

    @on(LabelTransactions.TableMounted)
    def get_data_for_table(self, event: LabelTransactions.TableMounted):
        """Query the DB for all unprocessed transactions and add them to the table."""
        unprocessed_data = self.data_handler.query_transactions_from_db()
        self.transaction_columns = event.table.add_columns(
            "AccountType",
            "PostedDate",
            "Amount",
            "Description",
            "Category",
            "Balance",
            "Processed",
            "Flagged",
        )
        event.table.add_rows(unprocessed_data[0:])

    @on(LabelTransactions.CategoryAccepted)
    def update_data_table(self, event: LabelTransactions.CategoryAccepted):
        """Update the category of the selected row in the database."""
        self.data_handler.update_category(
            new_category=event.category,
            row=event.table.get_row(event.row_key),
        )
        event.table.update_cell(
            row_key=event.row_key,
            column_key=self.transaction_columns[4],
            value=event.category,
        )
        event.table.update_cell(
            row_key=event.row_key,
            column_key=self.transaction_columns[6],
            value="Yes",
        )

    @on(BudgetProgress.ProgressTableMounted)
    def get_budget_progress_data(self, event: BudgetProgress.ProgressTableMounted):
        """Query the DB for all budget items and add them to the table."""

    @on(BudgetCRUD.BudgetTableMounted)
    def get_all_budget_items(self, event: BudgetCRUD.BudgetTableMounted):
        """Query the DB for all budget items and add them to the table."""
        budget_items = self.data_handler.query_active_budget_items_from_db()
        if budget_items:
            self.budget_columns = event.table.add_columns(
                "ID",
                "Category",
                "Amount",
                "Active",
                "Date Added",
                "Last Modified",
            )
            event.table.add_rows(budget_items[0:])

    @on(BudgetCRUD.StartBudgetItemUpdate)
    def items_to_update(self, event: BudgetCRUD.StartBudgetItemUpdate):
        """Send the row data to the BudgetCRUD screen to be updated."""
        self.query_one("#update_item_id").value = str(event.row_data[0])
        self.query_one("#update_item_category").value = str(event.row_data[1])
        self.query_one("#update_item_goal").value = str(event.row_data[2])

    @on(BudgetCRUD.SaveBudgetItemUpdate)
    def budget_items_to_update(self, event: BudgetCRUD.SaveBudgetItemUpdate):
        self.data_handler.update_budget_item(row=event.result)
        budget_items = self.data_handler.query_active_budget_items_from_db()
        event.table.clear()
        event.table.add_rows(budget_items[0:])

    @on(BudgetCRUD.FilterBudgetTable)
    def filter_budget_table(self, event: BudgetCRUD.FilterBudgetTable):
        """Filter the budget table based on the active status of the budget items."""
        if event.active:
            budget_items = self.data_handler.query_active_budget_items_from_db()
        else:
            budget_items = self.data_handler.query_budget_items_from_db()
        event.table.clear()
        event.table.add_rows(budget_items[0:])

    @on(BudgetCRUD.SaveBudgetItem)
    def items_to_save(self, event: BudgetCRUD.SaveBudgetItem):
        """Save the new budget item to the database."""
        self.data_handler.save_new_budget_item(
            category=event.item_category,
            amount=event.item_amount,
            active=event.active_status,
        )
        table = self.query_one("#budget_data_table")
        table.clear()
        table.add_rows(self.data_handler.query_active_budget_items_from_db()[0:])

    @on(BudgetCRUD.DeleteBudgetItem)
    def delete_budget_item(self, event: BudgetCRUD.DeleteBudgetItem):
        """Delete a budget item from the database."""
        self.data_handler.delete_item_from_db(id=event.id)
        event.table.remove_row(event.row_key)

    @on(BudgetProgress.CycleBackward)
    def handle_backward_cycle(self, event: BudgetProgress.CycleBackward):
        """Tell DataHandler/DB to move data by x months backwards in time"""
        event.table.clear()
        event.table.add_rows(
            self.data_handler.cycle_months(number_of_months=event.number_of_months)
        )

    @on(BudgetProgress.CycleForward)
    def handle_forward_cycle(self, event: BudgetProgress.CycleForward):
        """Tell DataHandler/DB to move data by x months forward in time"""
        event.table.clear()
        event.table.add_rows(
            self.data_handler.cycle_months(number_of_months=event.number_of_months)
        )

    #############################################
    ############# Button Events #################
    #############################################
    @on(Button.Pressed, "#upload_transactions")
    def on_upload_dataframe(self):
        """Send filepath to DataHandler for uploading to database."""
        filepath = Path(self.query_one("#file_name").value)
        self.data_handler.upload_dataframe(filepath)

    @on(Button.Pressed, "#cancel")
    def cancel_buttons(self):
        self.pop_screen()

    @on(Button.Pressed, "#categories")
    def on_categories(self):
        self.push_screen("categories")

    @on(Button.Pressed, ".mainmenu")
    def change_screen(self, event: Button.Pressed):
        """Pushes a new screen based on button pressed while on the main menu only."""
        self.push_screen(screen=event.button.id)

    @on(Button.Pressed, "#quit")
    def quit_buttons(self):
        """Closes the application for any buttons with the id of quit."""
        self.data_handler.close_database_connection()
        self.exit()

    @on(Button.Pressed, "#home")
    def go_to_main_menu(self, event: Button.Pressed):
        """Return to the main menu."""
        self.app.push_screen("home")


if __name__ == "__main__":
    model = Model()
    data_handler = DataHandler(model)
    app = Controller(model, data_handler)
    app.run()
