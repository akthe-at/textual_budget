"""Modal Screen for selecting transaction categories."""

from typing import Self

from constants_cat import SELECT_OPTIONS
from textual import on
from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Label, Select


class CategorySelection(ModalScreen):
    """Modal Screen for selecting transaction categories."""

    def __init__(self: Self, row_values: str) -> None:
        """Initialize the modal screen."""
        super().__init__(row_values)
        self.row_values = row_values
        self.transaction_description = self.row_values[3]
        self.current_category = self.row_values[4]

    def compose(self: Self) -> ComposeResult:
        """Render the modal screen."""
        yield Vertical(
            Label(
                renderable=f"How would you categorize {self.transaction_description}?",
                id="question",
            ),
            Select(
                options=SELECT_OPTIONS,
                id="category_list",
                prompt="Select Category",
            ),
            Container(
                Button(label="Accept", id="accept"),
                Button(label="Cancel", id="cancel"),
                classes="cat_buttons",
            ),
            id="dialog",
            classes="modal",
        )

    def on_mount(self: Self) -> None:
        """Set the title and expand the category list."""
        self.sub_title = "Select Category"
        self.query_one("#category_list", expect_type=Select).expanded = True

    @on(message_type=Button.Pressed, selector="#accept")
    def on_accept(self: Self) -> None:
        """Send category and row to DataHandler for updating the database."""
        self.dismiss(result=self.query_one(Select).value)
