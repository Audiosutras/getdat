import os
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
        # Its wrapped in click.echo so it will be shown
        spy.assert_called_once_with(msg, fg="red")
        # asserts that the context manager is fetched
        # to show help text for a command
        ctx.assert_called_once()


class TestAnnasEbook:

    env = {
        "GETDAT_BOOK_DIR": "~/books"
    }

    q = "Treasure Island Stevenson"
    ext = "epub"
    output_dir = "~/books/epub"

    @pytest.mark.parametrize("test_q_args,expected_q", [
        (("Treasure Island Stevenson",), "Treasure Island Stevenson"), 
        (("Treasure", "Island", "Stevenson",), "Treasure Island Stevenson")
    ])
    def test_q_1_arg_and_many_args(self, test_q_args, expected_q):
        ebook = AnnasEbook(q=test_q_args, ext='pdf', output_dir="")
        assert ebook.q == expected_q
    
    def test_output_dir(self, mocker):
        patched_env = mocker.patch.dict('os.environ', clear=True)
        # Neither option_output_dir or GETDAT_BOOK_DIR is set
        ebook = AnnasEbook(q=self.q, ext="epub", output_dir="")
        assert ebook.output_dir is None
        # GETDAT_BOOK_DIR loaded into environment
        mocker.patch.dict('os.environ', self.env, clear=True)
        ebook_1 = AnnasEbook(q=self.q, ext="epub", output_dir=self.output_dir)
        # option_output_dir overrides GETDAT_BOOK_DIR
        assert ebook_1.output_dir == self.output_dir
        # GETDAT_BOOK_DIR determines output_dir
        ebook_2 = AnnasEbook(q=self.q, ext="epub", output_dir="")
        assert ebook_2.output_dir == self.env.get("GETDAT_BOOK_DIR")
    
    @pytest.mark.parametrize(
        "ext,expected_ext",
        [("epub", "epub"), ("pdf", "pdf"), ("", "")]
    )
    def test_ext(self, ext, expected_ext):
        ebook = AnnasEbook(q=self.q, ext=ext, output_dir=self.output_dir)
        ebook.ext = expected_ext
    
    # def test_determine_source(self):

    

