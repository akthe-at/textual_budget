from pathlib import Path
from typing import Iterable

from textual import on
from textual.app import ComposeResult
from textual.containers import Center, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, DirectoryTree, Footer, Header, Input


class FilteredDirectoryTree(DirectoryTree):
    """A directory tree that filters out hidden files."""

    def filter_paths(self, paths: Iterable[Path]) -> Iterable[Path]:
        """Filter out hidden files."""
        return [path for path in paths if not path.name.startswith(".")]


class UploadScreen(Screen):
    """A screen for uploading bank statements."""

    def compose(self) -> ComposeResult:
        """Compose the screen."""
        yield Header()
        with Horizontal(id="first_block"):
            yield Button(label="Go Back", id="home")
            yield Button(
                label="Upload a File",
                id="upload_prompt_button",
            )
        with Vertical(id="second_block"):
            yield Input("Select File to Upload", id="file_name")
            yield Button("Submit", id="upload_transactions")
        with Center(id="file_tree_block"):
            yield FilteredDirectoryTree(
                path=str(Path.home()),
                id="tree_view",
            )
        yield Footer()

    def on_mount(self) -> None:
        """Actions to take when the screen is mounted."""
        self.sub_title = "Enter Bank Transcations"
        self.query_one("Header", expect_type=Header).tall = True
        self.query_one("#tree_view").display = False

    def on_directory_tree_file_selected(
        self, event: DirectoryTree.FileSelected
    ) -> None:
        """Actions to take when the user clicks a file in the directory tree."""
        self.query_one("#file_name", expect_type=Input).value = str(event.path)
        self.query_one("#file_name").focus()

    @on(Button.Pressed, "#upload_prompt_button")
    def toggle_file_tree(self):
        tree = self.query_one("#tree_view")
        if tree.display is False:
            tree.display = True
        else:
            tree.display = False
