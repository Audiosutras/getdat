import pytest
import webbrowser
from click.testing import CliRunner
from src.getdat.main import cinema

class TestCinema:
    runner = CliRunner()

    def test_launches_browser(self, mocker):
        mocker.patch('webbrowser.open_new_tab')
        result = self.runner.invoke(cinema)
        assert result.exit_code == 0
        webbrowser.open_new_tab.assert_called_once()
