import os
import click
import pytest
import requests
from click.testing import CliRunner
from requests.exceptions import ConnectionError, ChunkedEncodingError
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

    @pytest.mark.parametrize(
        "msg, error, error_msg, is_download",
        [
            (
                "This is a message echoed to user",
                None,
                "",
                False
            ),
            (
                "",
                None,
                "",
                False
            ),
            (
                "This is a message echoed to user",
                ConnectionError,
                "No connection established",
                False
            ),
            (
                "",
                ChunkedEncodingError,
                "No connection established",
                False
            ),
            (
                "",
                ConnectionError,
                "No connection established",
                True
            ),
            (
                "This is a message echoed to user",
                ChunkedEncodingError,
                "No connection established",
                True
            )
        ]
    )
    def test__get(self, msg, error, error_msg, is_download, mocker):
        ebook = AnnasEbook(q=self.q, ext=self.ext, output_dir=self.output_dir)
        mocked_get = mocker.patch.object(requests, 'get')
        mocker.patch.object(
            ebook,
            '_msg',
            msg
        )
        kwargs = dict()
        spy = mocker.spy(click, "style")
        if error and not is_download:
            mocked_get.side_effect = error
            response = ebook._get(**kwargs)
            spy.assert_has_calls(
                [
                    mocker.call(f"\n{msg}", fg="bright_yellow"),
                    mocker.call("No connection established", fg="bright_red")
                ]
            )
        elif error and is_download:
            with pytest.raises(error) as e:
                mocked_get.side_effect = error
                kwargs["is_download"] = True
                response = ebook._get(**kwargs)
                spy.assert_has_calls(
                    [
                        mocker.call(f"\n{msg}", fg="bright_yellow"),
                        mocker.call("No connection established", fg="bright_red")
                    ]
                )
                assert response == error
        else:
            mocked_get.return_value = "OK"
            response = ebook._get()
            spy.assert_called_once_with(f"\n{msg}", fg="bright_yellow")
            # No error occured and returns response
            assert response ==  "OK"
    
    @pytest.mark.parametrize(
        "_current_source, _scrape_key, html_file_path, expected_results",
        [
            (
                AnnasEbook._SOURCE_ANNAS,
                "search_page_scrape",
                "tests/static/annas_archive_search.html",
                {
                    '1': {'title': 'English [en], mobi, 0.6MB, Treasure Island - Stevenson, Robert Louis.mobi', 'link': '/md5/3ee7cf06b2c2b6aeea846894c4d79ea2', 'value': 1}, 
                    '2': {'title': 'English [en], azw, 0.3MB, Treasure Island - Stevenson, Robert Louis.azw', 'link': '/md5/24546a458458c5ea0e9bea31da25faaa', 'value': 2}, 
                    '3': {'title': 'English [en], epub, 0.3MB, Treasure Island - Stevenson, Robert Louis.epub', 'link': '/md5/4f95158d79dae74e16b5d0567be36fa6', 'value': 3}, 
                    '4': {'title': 'English [en], epub, 3.2MB', 'link': '/md5/e307fa56fab0f201c46fed5a1389a272', 'value': 4}, 
                    '5': {'title': 'English [en], pdf, 14.6MB, treasureisland0000stev_f7z0.pdf', 'link': '/md5/e5f954e12ce182fd530f7c16429a2134', 'value': 5}, 
                    '6': {'title': 'English [en], pdf, 0.9MB, stevenson-treasureisland.pdf', 'link': '/md5/6a861b94014c6adb183efe365c2fda18', 'value': 6}, 
                    '7': {'title': 'English [en], pdf, 1.0MB, Stevenson, Robert Louis - Treasure Island.pdf', 'link': '/md5/1b330f48bec2f9243c4be43a3089072a', 'value': 7}, 
                    '8': {'title': 'English [en], pdf, 0.9MB, Stevenson, Robert Louis - Treasure Island (2013, ).pdf', 'link': '/md5/28218ee8acf73a14dfef83936adc1502', 'value': 8}, 
                    '9': {'title': 'English [en], epub, 3.2MB, Treasure Island - Robert Louis Stevenson_1340.epub', 'link': '/md5/53a0b994062dc73b106144fdcbb8541d', 'value': 9}, 
                    '10': {'title': 'English [en], epub, 0.3MB, Stevenson, Robert Louis - Treasure Island (2012, ).epub', 'link': '/md5/abdb6dfe663b5fb4181123ea3973a38e', 'value': 10}, 
                    '11': {'title': 'English [en], epub, 0.3MB, [english] Stevenson, Robert Louis - Treasure Island.epub', 'link': '/md5/eabed0af49b234fa21c6029248816f25', 'value': 11}, 
                    '0': {'title': 'Continue in Browser', 'link': 'https://url.that-is-launched-in-browser.com', 'value': 0}
                }


            )
        ]
    )
    def test__scrape_results(self, _current_source, _scrape_key, html_file_path, expected_results, mocker):
        ebook = AnnasEbook(q=self.q, ext=self.ext, output_dir=self.output_dir)
        mocker.patch.object(
            ebook,
            '_current_source',
            _current_source
        )
        mocker.patch.object(
            ebook,
            '_scrape_key',
            _scrape_key
        )
        class MockResponse:

            @property
            def url(self):
                return "https://url.that-is-launched-in-browser.com"

            @property
            def content(self):
                with open(html_file_path) as f:
                    return f.read()
        
        response = MockResponse()
        results = ebook._scrape_results(response=response)
        assert results == expected_results


