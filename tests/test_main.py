import pytest
import click
from unittest.mock import Mock
from click.testing import CliRunner
from src import getdat
from src.getdat.main import cli, sport, cinema, ebook
from src.getdat.utils import AnnasEbook
from src.getdat.constants import EBOOK_ERROR_MSG, MOVIE_WEB, TOTALSPORTK


class TestCLI:
    runner = CliRunner()

    def test_getdat_homepage_in_epilog(self):
        result = self.runner.invoke(cli)
        homepage = "https://audiosutras.github.io/getdat/"
        assert homepage in result.output


class TestSport:
    runner = CliRunner()

    def test_sport_launches_browser(self, mocker):
        browser_launch = mocker.patch.object(click, "launch")
        result = self.runner.invoke(sport)
        assert result.exit_code == 0
        browser_launch.assert_called_once_with(TOTALSPORTK)


class TestCinema:
    runner = CliRunner()

    def test_cinema_launches_browser(self, mocker):
        browser_launch = mocker.patch.object(click, "launch")
        result = self.runner.invoke(cinema)
        assert result.exit_code == 0
        browser_launch.assert_called_once_with(MOVIE_WEB)


class TestEbook:
    runner = CliRunner()

    def get_help_text(self):
        help_text = self.runner.invoke(ebook, "--help")
        return help_text.output

    def test_no_args_print_help(self, mocker):
        ebook_run_method = mocker.patch.object(AnnasEbook, "run")
        results = self.runner.invoke(ebook)
        # assert error message echoed
        assert EBOOK_ERROR_MSG in results.output
        # assert help text prompt shown
        assert self.get_help_text() in results.output
        ebook_run_method.assert_not_called()

    def test_no_args_only_ext_option_print_help(self, mocker):
        ebook_run_method = mocker.patch.object(AnnasEbook, "run")
        results = self.runner.invoke(ebook, "--ext=epub")
        # assert error message echoed
        assert EBOOK_ERROR_MSG in results.output
        # assert help text prompt shown
        assert self.get_help_text() in results.output
        ebook_run_method.assert_not_called()

    def test_no_args_only_output_dir_option_print_help(self, mocker):
        ebook_run_method = mocker.patch.object(AnnasEbook, "run")
        results = self.runner.invoke(ebook, "--output_dir=~/books")
        # assert error message echoed
        assert EBOOK_ERROR_MSG in results.output
        # assert help text prompt shown
        assert self.get_help_text() in results.output
        ebook_run_method.assert_not_called()

    def test_no_args_only_instance_option_print_help(self, mocker):
        ebook_run_method = mocker.patch.object(AnnasEbook, "run")
        results = self.runner.invoke(ebook, "--instance=gs")
        # assert error message echoed
        assert EBOOK_ERROR_MSG in results.output
        # assert help text prompt shown
        assert self.get_help_text() in results.output
        ebook_run_method.assert_not_called()

    def test_no_args_only_options_print_help(self, mocker):
        ebook_run_method = mocker.patch.object(AnnasEbook, "run")
        results = self.runner.invoke(
            ebook, "--ext=pdf --output_dir=~/books --instance=gs"
        )
        # assert error message echoed
        assert EBOOK_ERROR_MSG in results.output
        # assert help text prompt shown
        assert self.get_help_text() in results.output
        ebook_run_method.assert_not_called()

    def test_1_search_arg_ebook_run(self, mocker):
        ebook_run_method = mocker.patch.object(AnnasEbook, "run")
        self.runner.invoke(ebook, "Treasure Island Stevenson")
        ebook_run_method.assert_called_once()

    def test_many_search_arg_ebook_run(self, mocker):
        ebook_run_method = mocker.patch.object(AnnasEbook, "run")
        self.runner.invoke(ebook, ["Treasure", "Island", "Stevenson"])
        ebook_run_method.assert_called_once()

    @pytest.mark.parametrize(
        "ext_type, expect_error", [("pdf", False), ("epub", False), ("er", True)]
    )
    def test_search_arg_ext_option_ebook_run(self, ext_type, expect_error, mocker):
        ebook_run_method = mocker.patch.object(AnnasEbook, "run")
        self.runner.invoke(ebook, f"Treasure Island Stevenson --ext={ext_type}")
        if expect_error:
            ebook_run_method.assert_not_called()
        else:
            ebook_run_method.assert_called_once()

    def test_search_arg_output_dir_option_ebook_run(self, mocker):
        ebook_run_method = mocker.patch.object(AnnasEbook, "run")
        self.runner.invoke(ebook, "Treasure Island Stevenson --output_dir=~/books/")
        ebook_run_method.assert_called_once()

    @pytest.mark.parametrize(
        "instance_type, expect_error",
        [
            (AnnasEbook._ANNAS_ORG_URL, False),
            (AnnasEbook._ANNAS_GS_URL, False),
            (AnnasEbook._ANNAS_SE_URL, False),
            ("er", True),
        ],
    )
    def test_search_arg_instance_option_ebook_run(
        self, instance_type, expect_error, mocker
    ):
        ebook_run_method = mocker.patch.object(AnnasEbook, "run")
        result = self.runner.invoke(
            ebook, f"Treasure Island Stevenson --instance={instance_type}"
        )
        if expect_error:
            ebook_run_method.assert_not_called()
        else:
            ebook_run_method.assert_called_once()

    def test_search_arg_options_ebook_run(self, mocker):
        ebook_run_method = mocker.patch.object(AnnasEbook, "run")
        self.runner.invoke(
            ebook,
            "Treasure Island Stevenson --ext=epub --output_dir=~/books/ --instance=gs",
        )
        ebook_run_method.assert_called_once()
