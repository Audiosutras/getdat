import click
import pytest
from click.testing import CliRunner

from src.getdat.utils import print_help, AnnasEbook

class TestPrintHelp:

    def test_print_help(self, mocker):
        spy = mocker.spy(click, "style")
        msg = "Error msg"

        class MockContext:

            def get_help(self):
                return "helped"
            
            def exit(self):
                return "exited"
        
        mock_get_current_context = MockContext()
        ctx = mocker.patch.object(click, "get_current_context", return_value=mock_get_current_context)
        print_help(msg)
        # assert our message is styled with error styling (red).
        # wrapped in click.echo so it will be shown
        spy.assert_called_once_with(msg, fg="red")
        # asserts that the context manager is fetched
        # to show help text for a command
        ctx.assert_called_once()
