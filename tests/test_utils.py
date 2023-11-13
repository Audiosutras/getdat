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


SEARCH = "Treasure Island Stevenson"

class TestAnnasEbook:

    env = {
        "GETDAT_BOOK_DIR": "~/books"
    }

    q = (SEARCH,)
    ext = "epub"
    output_dir = "~/books/epub"

    @pytest.mark.parametrize("test_q_args, expected_q", [
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
        "ext, expected_ext",
        [("epub", "epub"), ("pdf", "pdf"), ("", "")]
    )
    def test_ext(self, ext, expected_ext):
        ebook = AnnasEbook(q=self.q, ext=ext, output_dir=self.output_dir)
        ebook.ext = expected_ext
    
    @pytest.mark.parametrize(
        "source, expected_dict",
        [
            (AnnasEbook._SOURCE_ANNAS, {
                "name": AnnasEbook._SOURCE_ANNAS,
                "url": "https://annas-archive.org",
                "search_page_scrape": {
                    "tag": "a",
                    "class": (
                        "js-vim-focus custom-a flex items-center "
                        "relative left-[-10px] w-[calc(100%+20px)] px-[10px] "
                        "outline-offset-[-2px] outline-2 rounded-[3px] hover:bg-[#00000011] "
                        "focus:outline"
                    ),
                    "title_container": {
                        "tag": "div",
                        "class": (
                            "line-clamp-[2] leading-[1.2] text-[10px] lg:text-xs text-gray-500"
                        )
                    }
                },
                "detail_page_scrape": {
                    "tag": "a",
                    "class": "js-download-link"
                }
            }),
            (AnnasEbook._LIBGEN_RS, {
                "download_page": {
                    "tag": "a"
                }
            }),
            (AnnasEbook._LIBGEN_LI, {
                "url": "https://libgen.li/",
                "download_page": {
                    "tag": "a"
                }
            }),
            ("Not part of _SOURCE_DICT", None)
        ]
    )
    def test_determine_source(self, source, expected_dict, mocker):
        ebook = AnnasEbook(q=self.q, ext=self.ext, output_dir=self.output_dir)
        mocker.patch.object(
            ebook, 
            '_current_source', 
            source
        )
        assert ebook._determine_source() == expected_dict
    
    @pytest.mark.parametrize(
        "selected_result, expected_link",
        [
            ({"link": "https://books.google.com"}, "https://books.google.com"),
            ({"link": "http://shady-books.google.com"}, "http://shady-books.google.com"),
            (
                {"link": "/md5/234890238402380423"}, 
                f"{AnnasEbook._SOURCE_DICT[AnnasEbook._SOURCE_ANNAS].get("url")}/md5/234890238402380423"
            )
        ]
    )
    def test__determine_link(self, selected_result, expected_link, mocker):
        ebook = AnnasEbook(q=self.q, ext=self.ext, output_dir=self.output_dir)
        mocker.patch.object(
            ebook, 
            '_current_source', 
            AnnasEbook._current_source # _SOURCE_ANNAS
        )
        mocker.patch.object(
            ebook, 
            '_selected_result', 
            selected_result
        )
        assert ebook._determine_link() == expected_link
    
    @pytest.mark.parametrize(
        "ext, link, _current_source, _selected_result, _scrape_key, expected_url",
        [
            (
                "epub",
                None, 
                AnnasEbook._SOURCE_ANNAS, 
                {},
                "search_page_scrape",
                f"{AnnasEbook._SOURCE_DICT[AnnasEbook._SOURCE_ANNAS].get("url")}/search?q={SEARCH}&ext=epub",
            ),
            (
                "pdf",
                None, 
                AnnasEbook._SOURCE_ANNAS, 
                {},
                "search_page_scrape",
                f"{AnnasEbook._SOURCE_DICT[AnnasEbook._SOURCE_ANNAS].get("url")}/search?q={SEARCH}&ext=pdf",
            ),
            (
                "",
                None, 
                AnnasEbook._SOURCE_ANNAS, 
                {},
                "search_page_scrape",
                f"{AnnasEbook._SOURCE_DICT[AnnasEbook._SOURCE_ANNAS].get("url")}/search?q={SEARCH}",
            ),
            (
                "pdf",
                None,
                AnnasEbook._SOURCE_ANNAS,
                {"link": "https://books.google.com"},
                None,
                "https://books.google.com"
            ),
            (
                "",
                None,
                AnnasEbook._SOURCE_ANNAS,
                {"link": "https://books.google.com"},
                "download_page",
                "https://books.google.com"
            ),
            (
                "epub",
                None,
                AnnasEbook._SOURCE_ANNAS,
                {"link": "https://books.google.com"},
                "another_random_scrape_key",
                "https://books.google.com"
            ),
            (
                "",
                None,
                AnnasEbook._SOURCE_ANNAS,
                {"link": "http://shady-books.google.com"},
                None,
                "http://shady-books.google.com"
            ),
            (
                "pdf",
                None,
                AnnasEbook._SOURCE_ANNAS,
                {"link": "http://shady-books.google.com"},
                None,
                "http://shady-books.google.com"
            ),
            (
                "",
                None,
                AnnasEbook._SOURCE_ANNAS,
                {"link": "/md5/234890238402380423"},
                None,
                f"{AnnasEbook._SOURCE_DICT[AnnasEbook._SOURCE_ANNAS].get("url")}/md5/234890238402380423"
            ),
            (
                "epub",
                "https://solid-books.google.com",
                AnnasEbook._LIBGEN_LI,
                {"link": "/md5/234890238402380423"},
                None,
                "https://solid-books.google.com"
            ),
            (
                "epub",
                None,
                AnnasEbook._LIBGEN_LI,
                {"link": "/md5/234890238402380423"},
                None,
                f"{AnnasEbook._SOURCE_DICT[AnnasEbook._LIBGEN_LI].get("url")}/md5/234890238402380423"
            ),
            (
                "",
                "http://big-solid-books.google.com/?md5=32480238402384023",
                AnnasEbook._LIBGEN_RS,
                {},
                "download_page",
                "http://big-solid-books.google.com/?md5=32480238402384023"
            ),
            (
                "",
                "http://big-solid-books.google.com/?md5=32480238402384023",
                AnnasEbook._LIBGEN_RS,
                {"link": "/md5/234890238402380423"},
                "",
                "http://big-solid-books.google.com/?md5=32480238402384023"
            )
        ]
    )
    def test__get_url(
        self,
        ext,
        link, 
        _current_source, 
        _selected_result, 
        _scrape_key, 
        expected_url,
        mocker
    ):
        ebook = AnnasEbook(q=self.q, ext=ext, output_dir=self.output_dir)
        mocker.patch.object(
            ebook,
            '_current_source',
            _current_source
        )
        mocker.patch.object(
            ebook,
            '_selected_result',
            _selected_result
        )
        mocker.patch.object(
            ebook,
            '_scrape_key',
            _scrape_key
        )
        kwargs = {"link": link}
        assert ebook._get_url(**kwargs) == expected_url 