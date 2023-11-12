import pytest
import webbrowser
from unittest.mock import Mock
from click.testing import CliRunner
from src import getdat
from src.getdat.main import cinema, ebook
from src.getdat.utils import AnnasEbook

class TestCinema:
    runner = CliRunner()

    def test_cinema_launches_browser(self, mocker):
        browser_launch = mocker.patch('webbrowser.open_new_tab')
        result = self.runner.invoke(cinema)
        assert result.exit_code == 0
        browser_launch.assert_called_once()
    

class TestEbook:
    runner = CliRunner()

    def test_ebook_no_args_print_help(self, mocker):
        print_help = mocker.patch('getdat.utils.print_help')
        ebook_run_method = mocker.patch.object(AnnasEbook, 'run')
        self.runner.invoke(ebook, " ")
        # print_help.assert_called_once()
        ebook_run_method.assert_not_called()

    def test_ebook_with_1_search_arg(self, mocker):
        ebook_run_method = mocker.patch.object(AnnasEbook, 'run')
        self.runner.invoke(
            ebook, "Commentary on the Explanation of the Beautiful Names of Allah"
        )
        ebook_run_method.assert_called_once()
    
    def test_ebook_with_many_search_arg(self, mocker):
        ebook_run_method = mocker.patch.object(AnnasEbook, 'run')
        self.runner.invoke(
            ebook, [
                "Commentary",
                "on",
                "the",
                "Explanation",
                "of",
                "the",
                "Beautiful",
                "Names",
                "of",
                "Allah"
            ]
        )
        ebook_run_method.assert_called_once()
    


        

