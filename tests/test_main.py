import pytest
import webbrowser
from unittest.mock import Mock
from click.testing import CliRunner
from src import getdat
from src.getdat.main import cinema, ebook
from src.getdat.utils import AnnasEbook
from src.getdat.constants import EBOOK_ERROR_MSG

class TestCinema:
    runner = CliRunner()

    def test_cinema_launches_browser(self, mocker):
        browser_launch = mocker.patch('webbrowser.open_new_tab')
        result = self.runner.invoke(cinema)
        assert result.exit_code == 0
        browser_launch.assert_called_once()
    

class TestEbook:
    runner = CliRunner()

    def get_help_text(self):
        help_text = self.runner.invoke(ebook, "--help")
        return help_text.output

    def test_no_args_print_help(self, mocker):
        ebook_run_method = mocker.patch.object(AnnasEbook, 'run')
        results = self.runner.invoke(ebook)
        # assert error message echoed
        assert EBOOK_ERROR_MSG in results.output
        # assert help text prompt shown
        assert self.get_help_text() in results.output
        ebook_run_method.assert_not_called()

    def test_no_args_only_ext_option_print_help(self, mocker):
        ebook_run_method = mocker.patch.object(AnnasEbook, 'run')
        results = self.runner.invoke(ebook, "--ext=epub")
        # assert error message echoed
        assert EBOOK_ERROR_MSG in results.output
        # assert help text prompt shown
        assert self.get_help_text() in results.output
        ebook_run_method.assert_not_called()
    
    def test_no_args_only_output_dir_option_print_help(self, mocker):
        ebook_run_method = mocker.patch.object(AnnasEbook, 'run')
        results = self.runner.invoke(ebook, "--output_dir=~/books")
        # assert error message echoed
        assert EBOOK_ERROR_MSG in results.output
        # assert help text prompt shown
        assert self.get_help_text() in results.output
        ebook_run_method.assert_not_called()

    def test_no_args_only_options_print_help(self, mocker):
        ebook_run_method = mocker.patch.object(AnnasEbook, 'run')
        results = self.runner.invoke(ebook, "--ext=pdf --output_dir=~/books")
        # assert error message echoed
        assert EBOOK_ERROR_MSG in results.output
        # assert help text prompt shown
        assert self.get_help_text() in results.output
        ebook_run_method.assert_not_called()

    def test_1_search_arg_ebook_run(self, mocker):
        ebook_run_method = mocker.patch.object(AnnasEbook, 'run')
        self.runner.invoke(
            ebook, "Commentary on the Explanation of the Beautiful Names of Allah"
        )
        ebook_run_method.assert_called_once()
    
    def test_many_search_arg_ebook_run(self, mocker):
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

    def test_search_arg_ext_option_ebook_run(self, mocker):
        ebook_run_method = mocker.patch.object(AnnasEbook, 'run')
        self.runner.invoke(
            ebook, 
            "Commentary on the Explanation of the Beautiful Names of Allah --ext=epub"
        )
        ebook_run_method.assert_called_once()

    def test_search_arg_output_dir_option_ebook_run(self, mocker):
        ebook_run_method = mocker.patch.object(AnnasEbook, 'run')
        self.runner.invoke(
            ebook, 
            "Commentary on the Explanation of the Beautiful Names of Allah --output_dir=~/books/"
        )
        ebook_run_method.assert_called_once()

    def test_search_arg_options_ebook_run(self, mocker):
        ebook_run_method = mocker.patch.object(AnnasEbook, 'run')
        self.runner.invoke(
            ebook, 
            "Commentary on the Explanation of the Beautiful Names of Allah --ext=epub --output_dir=~/books/"
        )
        ebook_run_method.assert_called_once()
