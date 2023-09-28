from pathlib import Path
from typing import Iterable

import constants
import pandas as pd
from textual.app import ComposeResult
from textual.containers import Center, Grid
from textual.screen import Screen
from textual.widgets import Button, DirectoryTree, Footer, Header, Input, Label
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


class FilteredDirectoryTree(DirectoryTree):
    def filter_paths(self, paths: Iterable[Path]) -> Iterable[Path]:
        return [path for path in paths if not path.name.startswith(".")]


class UploadScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Input("Select File to Upload", id="file_name")
        yield Button("Upload Transactions", id="upload_transactions")
        yield Footer()
        yield FilteredDirectoryTree("../../../../", id="tree-view")

    def on_mount(self) -> None:
        self.title = "Kelly Bank"
        self.sub_title = "Enter Bank Transcations"
        self.query_one(FilteredDirectoryTree).focus()

    def on_directory_tree_file_selected(
        self, event: DirectoryTree.FileSelected
    ) -> None:
        """Called when the user clicks a file in the directory tree."""
        event.stop()
        self.query_one("#file_name").value = str(event.path)
        self.query_one("#file_name").focus()


class CategorySelection(Screen):
    """Screen with a dialog to quit."""

    def compose(self) -> ComposeResult:
        with Center():
            yield constants.CATEGORY_OPTIONS
            yield Grid(
                Label("How would you categorize this transaction?", id="question"),
                Button("Quit", variant="error", id="quit"),
                Button("Cancel", variant="primary", id="cancel"),
                id="dialog",
            )


class LabelTransactions(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()

        yield Button(label="Quit", id="quit")
        yield DataFrameTable()

    def on_mount(self) -> None:
        self.sub_title = "Monitor Income/Expenditure Transactions"
        table = self.query_one(DataFrameTable)
        table.cursor_type = "row"
        table.add_columns(*ROWS[0])
        table.add_rows(ROWS[1:])
