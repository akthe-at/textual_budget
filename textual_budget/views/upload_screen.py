from pathlib import Path
from typing import Iterable

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Button, DirectoryTree, Footer, Header, Input


class FilteredDirectoryTree(DirectoryTree):
    def filter_paths(self, paths: Iterable[Path]) -> Iterable[Path]:
        return [path for path in paths if not path.name.startswith(".")]


class UploadScreen(Screen):
    """A screen for uploading bank statements"""

    def compose(self) -> ComposeResult:
        yield Header()
        yield Input("Select File to Upload", id="file_name")
        yield Button("Upload Transactions", id="upload_transactions")
        yield Footer()
        yield FilteredDirectoryTree("C:/Users/ARK010/", id="tree-view")

    def on_mount(self) -> None:
        self.sub_title = "Enter Bank Transcations"
        self.query_one(FilteredDirectoryTree).focus()

    def on_directory_tree_file_selected(
        self, event: DirectoryTree.FileSelected
    ) -> None:
        """Called when the user clicks a file in the directory tree."""
        self.query_one("#file_name").value = str(event.path)
        self.query_one("#file_name").focus()
