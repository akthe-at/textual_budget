from model.model import Model
from textual.widgets import OptionList
from views.budget import BudgetCRUD, BudgetProgress
from views.categorize import CategorySelection, LabelTransactions
from views.main_screen import HomeScreen
from views.stats import SpendingStats
from views.upload_screen import UploadScreen

CATEGORY_OPTIONS = OptionList(
    "Groceries/House Supplies",
    "Gas",
    "Car Expenses",
    "Medical",
    "Mortgage",
    "Gas/Electric",
    "Water/Sewer",
    "Dog",
    "Home Renovation",
    "Daycare",
    "Internet",
    "Phone",
    "Savings",
    "Student Loans",
    "Eating Out",
    id="category_list",
)

SCREENS = {
    "upload": UploadScreen(),
    "home": HomeScreen(),
    "categories": LabelTransactions(model=Model),
    "budget_review": BudgetProgress(),
    "budget_crud": BudgetCRUD(),
    "stats": SpendingStats(),
    "catpicker": CategorySelection(),
}

BINDINGS = {
    ("h", "action_push_screen('home')", "Home Page"),
}
