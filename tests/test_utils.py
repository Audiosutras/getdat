import click
import pytest
from click.testing import CliRunner

from src.getdat.utils import print_help, AnnasEbook

class TestPrintHelp:

    def test_print_help(self, mocker):
        class MockContext:

            def get_help(self):
                return "helped"
            
            def exit(self):
                return "exited"
        
        mock_get_current_context = MockContext()
        ctx = mocker.patch.object(click, "get_current_context", return_value=mock_get_current_context)
        print_help("Yo")
        ctx.assert_called_once()
