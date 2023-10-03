from model.model import Model
from views.budget import BudgetCRUD, BudgetProgress
from views.categorize import CategorySelection, LabelTransactions
from views.main_screen import HomeScreen
from views.stats import SpendingStats
from views.upload_screen import UploadScreen

SCREENS = {
    "upload": UploadScreen,
    "home": HomeScreen,
    "categories": LabelTransactions,
    "budget_review": BudgetProgress,
    "budget_crud": BudgetCRUD,
    "stats": SpendingStats,
    "catpicker": CategorySelection,
}

BINDINGS = {
    ("h", "action_push_screen('home')", "Home Page"),
}
