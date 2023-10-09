from constants_cat import SELECT_OPTIONS
from textual import on
from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Label, Select


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
