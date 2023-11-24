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
        ctx = mocker.patch.object(
            click, "get_current_context", return_value=mock_get_current_context
        )
        print_help(msg)
        # assert our message is styled with error styling (red).
        # Its wrapped in click.echo so it will be shown
        spy.assert_called_once_with(msg, fg="red")
        # asserts that the context manager is fetched
        # to show help text for a command
        ctx.assert_called_once()


SEARCH = "Treasure Island Stevenson"

PDF_CONTENT_TYPE = "application/pdf"
EPUB_CONTENT_TYPE = "application/epub+zip"


class TestAnnasEbook:

    env = {"GETDAT_BOOK_DIR": "~/books"}

    q = (SEARCH,)
    ext = "epub"
    lang = "en"
    content = ""
    output_dir = "~/books/epub"

    @pytest.mark.parametrize(
        "test_q_args, expected_q",
        [
            (("Treasure Island Stevenson",), "Treasure Island Stevenson"),
            (
                (
                    "Treasure",
                    "Island",
                    "Stevenson",
                ),
                "Treasure Island Stevenson",
            ),
        ],
    )
    def test_q_1_arg_and_many_args(self, test_q_args, expected_q):
        ebook = AnnasEbook(
            q=test_q_args,
            ext=self.ext,
            lang=self.lang,
            content=self.content,
            output_dir=self.output_dir,
        )
        assert ebook.q == expected_q

    def test_output_dir(self, mocker):
        patched_env = mocker.patch.dict("os.environ", clear=True)
        # Neither option_output_dir or GETDAT_BOOK_DIR is set
        ebook = AnnasEbook(
            q=self.q, ext=self.ext, lang=self.lang, content=self.content, output_dir=""
        )
        assert ebook.output_dir is None
        # GETDAT_BOOK_DIR loaded into environment
        mocker.patch.dict("os.environ", self.env, clear=True)
        ebook_1 = AnnasEbook(
            q=self.q,
            ext=self.ext,
            lang=self.lang,
            content=self.content,
            output_dir=self.output_dir,
        )
        # option_output_dir overrides GETDAT_BOOK_DIR
        assert ebook_1.output_dir == self.output_dir
        # GETDAT_BOOK_DIR determines output_dir
        ebook_2 = AnnasEbook(
            q=self.q, ext=self.ext, lang=self.lang, content=self.content, output_dir=""
        )
        assert ebook_2.output_dir == self.env.get("GETDAT_BOOK_DIR")

    @pytest.mark.parametrize(
        "ext, expected_ext",
        [
            (AnnasEbook._EPUB, AnnasEbook._EPUB),
            (AnnasEbook._PDF, AnnasEbook._PDF),
            (AnnasEbook._MOBI, AnnasEbook._MOBI),
            (AnnasEbook._CBR, AnnasEbook._CBR),
            (AnnasEbook._CBZ, AnnasEbook._CBZ),
            (AnnasEbook._FB2, AnnasEbook._FB2),
            (AnnasEbook._FB2_ZIP, AnnasEbook._FB2_ZIP),
            (AnnasEbook._AZW3, AnnasEbook._AZW3),
            (AnnasEbook._DJVU, AnnasEbook._DJVU),
            (
                f"{AnnasEbook._EPUB},{AnnasEbook._PDF}, {AnnasEbook._CBR}",
                f"{AnnasEbook._EPUB},{AnnasEbook._PDF}, {AnnasEbook._CBR}",
            ),
        ],
    )
    def test_ext(self, ext, expected_ext):
        ebook = AnnasEbook(
            q=self.q,
            ext=ext,
            lang=self.lang,
            content=self.content,
            output_dir=self.output_dir,
        )
        assert ebook._search_params["ext"] == expected_ext

    @pytest.mark.parametrize(
        "lang, expected_lang",
        [
            ("en", "en"),
            ("es,en", "es,en"),
            ("zh-Hans", "zh-Hans"),
            ("zh,es,zh-Hans", "zh,es,zh-Hans"),
        ],
    )
    def test_lang(self, lang, expected_lang):
        ebook = AnnasEbook(
            q=self.q,
            ext=self.ext,
            lang=lang,
            content=self.content,
            output_dir=self.output_dir,
        )
        assert ebook._search_params["lang"] == expected_lang

    @pytest.mark.parametrize(
        "instance",
        [
            (AnnasEbook._ANNAS_ORG_URL),
            (AnnasEbook._ANNAS_GS_URL),
            (AnnasEbook._ANNAS_SE_URL),
            (""),
            ("rs"),
        ],
    )
    def test_instance(self, instance):
        if instance in AnnasEbook._ANNAS_URLS.keys():
            ebook = AnnasEbook(
                q=self.q,
                ext=self.ext,
                lang=self.lang,
                content=self.content,
                output_dir=self.output_dir,
                instance=instance,
            )
            assert ebook.instance == instance
        else:
            ebook = AnnasEbook(
                q=self.q,
                ext=self.ext,
                lang=self.lang,
                content=self.content,
                output_dir=self.output_dir,
            )
            assert ebook.instance == AnnasEbook._ANNAS_ORG_URL

    @pytest.mark.parametrize(
        "source, instance, expected_dict",
        [
            (
                AnnasEbook._SOURCE_ANNAS,
                "",
                {
                    "name": AnnasEbook._SOURCE_ANNAS,
                    "url": AnnasEbook._ANNAS_URLS.get(AnnasEbook._ANNAS_ORG_URL),
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
                            ),
                        },
                    },
                    "detail_page_scrape": {"tag": "a", "class": "js-download-link"},
                },
            ),
            (
                AnnasEbook._SOURCE_ANNAS,
                AnnasEbook._ANNAS_GS_URL,
                {
                    "name": AnnasEbook._SOURCE_ANNAS,
                    "url": AnnasEbook._ANNAS_URLS.get(AnnasEbook._ANNAS_GS_URL),
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
                            ),
                        },
                    },
                    "detail_page_scrape": {"tag": "a", "class": "js-download-link"},
                },
            ),
            (
                AnnasEbook._SOURCE_ANNAS,
                AnnasEbook._ANNAS_SE_URL,
                {
                    "name": AnnasEbook._SOURCE_ANNAS,
                    "url": AnnasEbook._ANNAS_URLS.get(AnnasEbook._ANNAS_SE_URL),
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
                            ),
                        },
                    },
                    "detail_page_scrape": {"tag": "a", "class": "js-download-link"},
                },
            ),
            (AnnasEbook._LIBGEN_RS, "", {"download_page_scrape": {"tag": "a"}}),
            (
                AnnasEbook._LIBGEN_LI,
                AnnasEbook._ANNAS_GS_URL,
                {"url": "https://libgen.li/", "download_page_scrape": {"tag": "a"}},
            ),
            ("Not part of _SOURCE_DICT", "", None),
        ],
    )
    def test_determine_source(self, source, instance, expected_dict, mocker):
        if instance:
            ebook = AnnasEbook(
                q=self.q,
                ext=self.ext,
                lang=self.lang,
                content=self.content,
                output_dir=self.output_dir,
                instance=instance,
            )
            mocker.patch.object(ebook, "_current_source", source)
            assert ebook._determine_source() == expected_dict
        else:
            ebook = AnnasEbook(
                q=self.q,
                ext=self.ext,
                lang=self.lang,
                content=self.content,
                output_dir=self.output_dir,
            )
            mocker.patch.object(ebook, "_current_source", source)
            assert ebook._determine_source() == expected_dict

    @pytest.mark.parametrize(
        "selected_result, expected_link",
        [
            ({"link": "https://books.google.com"}, "https://books.google.com"),
            (
                {"link": "http://shady-books.google.com"},
                "http://shady-books.google.com",
            ),
            (
                {"link": "/md5/234890238402380423"},
                f"{AnnasEbook._SOURCE_DICT[AnnasEbook._SOURCE_ANNAS].get('url')}/md5/234890238402380423",
            ),
        ],
    )
    def test__determine_link(self, selected_result, expected_link, mocker):
        ebook = AnnasEbook(
            q=self.q,
            ext=self.ext,
            lang=self.lang,
            content=self.content,
            output_dir=self.output_dir,
        )
        mocker.patch.object(
            ebook, "_current_source", AnnasEbook._current_source  # _SOURCE_ANNAS
        )
        mocker.patch.object(ebook, "_selected_result", selected_result)
        assert ebook._determine_link() == expected_link

    @pytest.mark.parametrize(
        "ext, lang, content, link, _current_source, _selected_result, _scrape_key, expected_url",
        [
            (
                "err.ext",
                "",
                "",
                None,
                AnnasEbook._SOURCE_ANNAS,
                {},
                "search_page_scrape",
                f"{AnnasEbook._SOURCE_DICT[AnnasEbook._SOURCE_ANNAS].get('url')}/search?q={SEARCH}",
            ),
            (
                "epub",
                "",
                "",
                None,
                AnnasEbook._SOURCE_ANNAS,
                {},
                "search_page_scrape",
                f"{AnnasEbook._SOURCE_DICT[AnnasEbook._SOURCE_ANNAS].get('url')}/search?q={SEARCH}&ext=epub",
            ),
            (
                "epub,pdf",
                "",
                "",
                None,
                AnnasEbook._SOURCE_ANNAS,
                {},
                "search_page_scrape",
                f"{AnnasEbook._SOURCE_DICT[AnnasEbook._SOURCE_ANNAS].get('url')}/search?q={SEARCH}&ext=epub&ext=pdf",
            ),
            (
                "epub",
                "en",
                "",
                None,
                AnnasEbook._SOURCE_ANNAS,
                {},
                "search_page_scrape",
                f"{AnnasEbook._SOURCE_DICT[AnnasEbook._SOURCE_ANNAS].get('url')}/search?q={SEARCH}&ext=epub&lang=en",
            ),
            (
                "epub,mobi",
                "en",
                "nf,f",
                None,
                AnnasEbook._SOURCE_ANNAS,
                {},
                "search_page_scrape",
                f"{AnnasEbook._SOURCE_DICT[AnnasEbook._SOURCE_ANNAS].get('url')}/search?q={SEARCH}&ext=epub&ext=mobi&lang=en&content=book_nonfiction&content=book_fiction",
            ),
            (
                "pdf",
                "",
                "",
                None,
                AnnasEbook._SOURCE_ANNAS,
                {},
                "search_page_scrape",
                f"{AnnasEbook._SOURCE_DICT[AnnasEbook._SOURCE_ANNAS].get('url')}/search?q={SEARCH}&ext=pdf",
            ),
            (
                "pdf",
                "en,es,zh-Hant",
                "m",
                None,
                AnnasEbook._SOURCE_ANNAS,
                {},
                "search_page_scrape",
                f"{AnnasEbook._SOURCE_DICT[AnnasEbook._SOURCE_ANNAS].get('url')}/search?q={SEARCH}&ext=pdf&lang=en&lang=es&lang=zh-Hant&content=magazine",
            ),
            (
                "xox",
                "en,es,zh-Hant",
                "m",
                None,
                AnnasEbook._SOURCE_ANNAS,
                {},
                "search_page_scrape",
                f"{AnnasEbook._SOURCE_DICT[AnnasEbook._SOURCE_ANNAS].get('url')}/search?q={SEARCH}&lang=en&lang=es&lang=zh-Hant&content=magazine",
            ),
            (
                "xox,epub",
                "en,es,zh-Hant",
                "m",
                None,
                AnnasEbook._SOURCE_ANNAS,
                {},
                "search_page_scrape",
                f"{AnnasEbook._SOURCE_DICT[AnnasEbook._SOURCE_ANNAS].get('url')}/search?q={SEARCH}&ext=epub&lang=en&lang=es&lang=zh-Hant&content=magazine",
            ),
            (
                "pdf,cbr",
                "en,es,zh-Hant",
                "xoxo",
                None,
                AnnasEbook._SOURCE_ANNAS,
                {},
                "search_page_scrape",
                f"{AnnasEbook._SOURCE_DICT[AnnasEbook._SOURCE_ANNAS].get('url')}/search?q={SEARCH}&ext=pdf&ext=cbr&lang=en&lang=es&lang=zh-Hant",
            ),
            (
                "",
                "",
                "",
                None,
                AnnasEbook._SOURCE_ANNAS,
                {},
                "search_page_scrape",
                f"{AnnasEbook._SOURCE_DICT[AnnasEbook._SOURCE_ANNAS].get('url')}/search?q={SEARCH}",
            ),
            (
                "",
                "en,es",
                "",
                None,
                AnnasEbook._SOURCE_ANNAS,
                {},
                "search_page_scrape",
                f"{AnnasEbook._SOURCE_DICT[AnnasEbook._SOURCE_ANNAS].get('url')}/search?q={SEARCH}&lang=en&lang=es",
            ),
            (
                "",
                "",
                "cb,u",
                None,
                AnnasEbook._SOURCE_ANNAS,
                {},
                "search_page_scrape",
                f"{AnnasEbook._SOURCE_DICT[AnnasEbook._SOURCE_ANNAS].get('url')}/search?q={SEARCH}&content=book_comic&content=book_unknown",
            ),
            (
                "",
                "",
                "cb,xoxo",
                None,
                AnnasEbook._SOURCE_ANNAS,
                {},
                "search_page_scrape",
                f"{AnnasEbook._SOURCE_DICT[AnnasEbook._SOURCE_ANNAS].get('url')}/search?q={SEARCH}&content=book_comic",
            ),
            (
                "",
                "",
                "xoxo",
                None,
                AnnasEbook._SOURCE_ANNAS,
                {},
                "search_page_scrape",
                f"{AnnasEbook._SOURCE_DICT[AnnasEbook._SOURCE_ANNAS].get('url')}/search?q={SEARCH}",
            ),
            (
                "pdf",
                "en,es",
                "sd",
                None,
                AnnasEbook._SOURCE_ANNAS,
                {"link": "https://books.google.com"},
                None,
                "https://books.google.com",
            ),
            (
                "",
                "",
                "",
                None,
                AnnasEbook._SOURCE_ANNAS,
                {"link": "https://books.google.com"},
                "download_page",
                "https://books.google.com",
            ),
            (
                "epub",
                "",
                "",
                None,
                AnnasEbook._SOURCE_ANNAS,
                {"link": "https://books.google.com"},
                "another_random_scrape_key",
                "https://books.google.com",
            ),
            (
                "",
                "",
                "nf,u,f",
                None,
                AnnasEbook._SOURCE_ANNAS,
                {"link": "http://shady-books.google.com"},
                None,
                "http://shady-books.google.com",
            ),
            (
                "pdf",
                "",
                "",
                None,
                AnnasEbook._SOURCE_ANNAS,
                {"link": "http://shady-books.google.com"},
                None,
                "http://shady-books.google.com",
            ),
            (
                "",
                "en,es",
                "",
                None,
                AnnasEbook._SOURCE_ANNAS,
                {"link": "/md5/234890238402380423"},
                None,
                f"{AnnasEbook._SOURCE_DICT[AnnasEbook._SOURCE_ANNAS].get('url')}/md5/234890238402380423",
            ),
            (
                "epub",
                "en,es",
                "nf",
                "https://solid-books.google.com",
                AnnasEbook._LIBGEN_LI,
                {"link": "/md5/234890238402380423"},
                None,
                "https://solid-books.google.com",
            ),
            (
                "epub",
                "",
                "",
                None,
                AnnasEbook._LIBGEN_LI,
                {"link": "/md5/234890238402380423"},
                None,
                f"{AnnasEbook._SOURCE_DICT[AnnasEbook._LIBGEN_LI].get('url')}/md5/234890238402380423",
            ),
            (
                "",
                "en,es",
                "",
                "http://big-solid-books.google.com/?md5=32480238402384023",
                AnnasEbook._LIBGEN_RS,
                {},
                "download_page",
                "http://big-solid-books.google.com/?md5=32480238402384023",
            ),
            (
                "",
                "",
                "",
                "http://big-solid-books.google.com/?md5=32480238402384023",
                AnnasEbook._LIBGEN_RS,
                {"link": "/md5/234890238402380423"},
                "",
                "http://big-solid-books.google.com/?md5=32480238402384023",
            ),
        ],
    )
    def test__get_url(
        self,
        ext,
        lang,
        content,
        link,
        _current_source,
        _selected_result,
        _scrape_key,
        expected_url,
        mocker,
    ):
        ebook = AnnasEbook(
            q=self.q, ext=ext, lang=lang, content=content, output_dir=self.output_dir
        )
        mocker.patch.object(ebook, "_current_source", _current_source)
        mocker.patch.object(ebook, "_selected_result", _selected_result)
        mocker.patch.object(ebook, "_scrape_key", _scrape_key)
        kwargs = {"link": link}
        assert ebook._get_url(**kwargs) == expected_url

    @pytest.mark.parametrize(
        "msg, error",
        [
            ("This is a message echoed to user", None),
            ("", None),
            (
                "This is a message echoed to user",
                ConnectionError,
            ),
            ("", ChunkedEncodingError),
        ],
    )
    def test__get(self, msg, error, mocker):
        ebook = AnnasEbook(
            q=self.q,
            ext=self.ext,
            lang=self.lang,
            content=self.content,
            output_dir=self.output_dir,
        )
        mocked_get = mocker.patch.object(requests, "get")
        mocker.patch.object(ebook, "_msg", msg)
        kwargs = dict()
        spy = mocker.spy(click, "style")
        if error:
            mocked_get.side_effect = error
            with pytest.raises(error):
                response = ebook._get(**kwargs)
                spy.assert_has_calls(
                    [
                        mocker.call(f"\n{msg}", fg="bright_yellow"),
                        mocker.call("No connection established", fg="bright_red"),
                    ]
                )
        else:
            mocked_get.return_value = "OK"
            response = ebook._get()
            if msg:
                spy.assert_called_once_with(f"\n{msg}", fg="bright_yellow")
            # No error occured and returns response
            assert response == "OK"

    @pytest.mark.parametrize(
        "_current_source, _scrape_key, html_file_path, expected_results",
        [
            (
                AnnasEbook._SOURCE_ANNAS,
                "search_page_scrape",
                "tests/static/annas_archive_search.html",
                {
                    "1": {
                        "title": "English [en], mobi, 0.6MB, Treasure Island - Stevenson, Robert Louis.mobi",
                        "link": "/md5/3ee7cf06b2c2b6aeea846894c4d79ea2",
                        "value": 1,
                    },
                    "2": {
                        "title": "English [en], azw, 0.3MB, Treasure Island - Stevenson, Robert Louis.azw",
                        "link": "/md5/24546a458458c5ea0e9bea31da25faaa",
                        "value": 2,
                    },
                    "3": {
                        "title": "English [en], epub, 0.3MB, Treasure Island - Stevenson, Robert Louis.epub",
                        "link": "/md5/4f95158d79dae74e16b5d0567be36fa6",
                        "value": 3,
                    },
                    "4": {
                        "title": "English [en], epub, 3.2MB",
                        "link": "/md5/e307fa56fab0f201c46fed5a1389a272",
                        "value": 4,
                    },
                    "5": {
                        "title": "English [en], pdf, 14.6MB, treasureisland0000stev_f7z0.pdf",
                        "link": "/md5/e5f954e12ce182fd530f7c16429a2134",
                        "value": 5,
                    },
                    "6": {
                        "title": "English [en], pdf, 0.9MB, stevenson-treasureisland.pdf",
                        "link": "/md5/6a861b94014c6adb183efe365c2fda18",
                        "value": 6,
                    },
                    "7": {
                        "title": "English [en], pdf, 1.0MB, Stevenson, Robert Louis - Treasure Island.pdf",
                        "link": "/md5/1b330f48bec2f9243c4be43a3089072a",
                        "value": 7,
                    },
                    "8": {
                        "title": "English [en], pdf, 0.9MB, Stevenson, Robert Louis - Treasure Island (2013, ).pdf",
                        "link": "/md5/28218ee8acf73a14dfef83936adc1502",
                        "value": 8,
                    },
                    "9": {
                        "title": "English [en], epub, 3.2MB, Treasure Island - Robert Louis Stevenson_1340.epub",
                        "link": "/md5/53a0b994062dc73b106144fdcbb8541d",
                        "value": 9,
                    },
                    "10": {
                        "title": "English [en], epub, 0.3MB, Stevenson, Robert Louis - Treasure Island (2012, ).epub",
                        "link": "/md5/abdb6dfe663b5fb4181123ea3973a38e",
                        "value": 10,
                    },
                    "11": {
                        "title": "English [en], epub, 0.3MB, [english] Stevenson, Robert Louis - Treasure Island.epub",
                        "link": "/md5/eabed0af49b234fa21c6029248816f25",
                        "value": 11,
                    },
                    "0": {
                        "title": "Continue in Browser",
                        "link": "https://url.that-is-launched-in-browser.com",
                        "value": 0,
                    },
                },
            ),
            (
                AnnasEbook._SOURCE_ANNAS,
                "detail_page_scrape",
                "tests/static/annas_archive_detail.html",
                {
                    "1": {
                        "title": "Fast Partner Server #1",
                        "link": "/fast_download/4f95158d79dae74e16b5d0567be36fa6/0/0",
                        "value": 1,
                    },
                    "2": {
                        "title": "Fast Partner Server #2",
                        "link": "/fast_download/4f95158d79dae74e16b5d0567be36fa6/0/1",
                        "value": 2,
                    },
                    "3": {
                        "title": "Slow Partner Server #1",
                        "link": "/slow_download/4f95158d79dae74e16b5d0567be36fa6/0/0",
                        "value": 3,
                    },
                    "4": {
                        "title": "Slow Partner Server #2",
                        "link": "/slow_download/4f95158d79dae74e16b5d0567be36fa6/0/1",
                        "value": 4,
                    },
                    "5": {
                        "title": "Slow Partner Server #3",
                        "link": "/slow_download/4f95158d79dae74e16b5d0567be36fa6/0/2",
                        "value": 5,
                    },
                    "6": {
                        "title": "Libgen.li",
                        "link": "http://libgen.li/ads.php?md5=4f95158d79dae74e16b5d0567be36fa6",
                        "value": 6,
                    },
                    "7": {
                        "title": "Z-Library",
                        "link": "https://1lib.sk/md5/4f95158d79dae74e16b5d0567be36fa6",
                        "value": 7,
                    },
                    "0": {
                        "title": "Continue in Browser",
                        "link": "https://url.that-is-launched-in-browser.com",
                        "value": 0,
                    },
                },
            ),
            (
                AnnasEbook._LIBGEN_LI,
                "download_page_scrape",
                "tests/static/libgen_li_detail.html",
                {
                    "61": {
                        "title": "GET",
                        "link": "get.php?md5=4f95158d79dae74e16b5d0567be36fa6&key=8ETFRGFWBSSQMDRV",
                        "value": 61,
                    },
                    "0": {
                        "title": "Continue in Browser",
                        "link": "https://url.that-is-launched-in-browser.com",
                        "value": 0,
                    },
                },
            ),
            (
                AnnasEbook._LIBGEN_RS,
                "download_page_scrape",
                "tests/static/libgen_rs_detail.html",
                {
                    "1": {
                        "title": "GET",
                        "link": "https://download.library.lol/fiction/1511000/eabed0af49b234fa21c6029248816f25.epub/Stevenson%2C%20Robert%20Louis%20-%20Treasure%20Island.epub",
                        "value": 1,
                    },
                    "0": {
                        "title": "Continue in Browser",
                        "link": "https://url.that-is-launched-in-browser.com",
                        "value": 0,
                    },
                },
            ),
        ],
    )
    def test__scrape_results(
        self, _current_source, _scrape_key, html_file_path, expected_results, mocker
    ):
        ebook = AnnasEbook(
            q=self.q,
            ext=self.ext,
            lang=self.lang,
            content=self.content,
            output_dir=self.output_dir,
        )
        mocker.patch.object(ebook, "_current_source", _current_source)
        mocker.patch.object(ebook, "_scrape_key", _scrape_key)

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

    @pytest.mark.parametrize(
        "key, title_str, expected_str",
        [
            (
                "1",
                "English [en], epub, 0.3MB, Treasure Island - Stevenson, Robert Louis.epub",
                " 1 | Treasure Island - Stevenson, Robert Louis.epub | epub | 0.3MB | English [en]",
            ),
            (
                2,
                "English [en], epub, 0.3MB, Treasure Island - Stevenson, Robert Louis.epub",
                " 2 | Treasure Island - Stevenson, Robert Louis.epub | epub | 0.3MB | English [en]",
            ),
            (
                3,
                "English [en], epub, Treasure Island - Stevenson Robert Louis.epub",
                f" 3 | {AnnasEbook._ENTRY_NOT_DISPLAYED}",
            ),
            (
                "4",
                "Treasure Island - Stevenson, Robert Louis.epub",
                f" 4 | {AnnasEbook._ENTRY_NOT_DISPLAYED}",
            ),
        ],
    )
    def test__echo_formatted_title(self, key, title_str, expected_str, mocker):
        ebook = AnnasEbook(
            q=self.q,
            ext=self.ext,
            lang=self.lang,
            content=self.content,
            output_dir=self.output_dir,
        )
        if AnnasEbook._ENTRY_NOT_DISPLAYED in expected_str:
            spy = mocker.spy(click, "style")
            ebook._echo_formatted_title(key, title_str)
            spy.assert_called_once_with(expected_str, fg="bright_red")
        else:
            spy = mocker.spy(click, "echo")
            ebook._echo_formatted_title(key, title_str)
            spy.assert_called_once_with(expected_str)

    @pytest.mark.parametrize(
        "_scrape_key, results, expected_to_have_results",
        [
            ("search_page_scrape", {}, False),
            (
                "",
                {
                    "0": {
                        "title": "Continue in Browser",
                        "link": "https://url.that-is-launched-in-browser.com",
                        "value": 0,
                    },
                },
                False,
            ),
            (
                "detail_page_scrape",
                {
                    "0": {
                        "title": "Continue in Browser",
                        "link": "https://url.that-is-launched-in-browser.com",
                        "value": 0,
                    },
                },
                False,
            ),
            (
                "search_page_scrape",
                {
                    "1": {
                        "title": "English [en], mobi, 0.6MB, Treasure Island - Stevenson, Robert Louis.mobi",
                        "link": "/md5/3ee7cf06b2c2b6aeea846894c4d79ea2",
                        "value": 1,
                    },
                    "2": {
                        "title": "English [en], azw, 0.3MB, Treasure Island - Stevenson, Robert Louis.azw",
                        "link": "/md5/24546a458458c5ea0e9bea31da25faaa",
                        "value": 2,
                    },
                    "3": {
                        "title": "English [en], epub, 0.3MB, Treasure Island - Stevenson, Robert Louis.epub",
                        "link": "/md5/4f95158d79dae74e16b5d0567be36fa6",
                        "value": 3,
                    },
                    "4": {
                        "title": "English [en], epub, 3.2MB",
                        "link": "/md5/e307fa56fab0f201c46fed5a1389a272",
                        "value": 4,
                    },
                    "5": {
                        "title": "English [en], pdf, 14.6MB, treasureisland0000stev_f7z0.pdf",
                        "link": "/md5/e5f954e12ce182fd530f7c16429a2134",
                        "value": 5,
                    },
                    "6": {
                        "title": "English [en], pdf, 0.9MB, stevenson-treasureisland.pdf",
                        "link": "/md5/6a861b94014c6adb183efe365c2fda18",
                        "value": 6,
                    },
                    "7": {
                        "title": "English [en], pdf, 1.0MB, Stevenson, Robert Louis - Treasure Island.pdf",
                        "link": "/md5/1b330f48bec2f9243c4be43a3089072a",
                        "value": 7,
                    },
                    "8": {
                        "title": "English [en], pdf, 0.9MB, Stevenson, Robert Louis - Treasure Island (2013, ).pdf",
                        "link": "/md5/28218ee8acf73a14dfef83936adc1502",
                        "value": 8,
                    },
                    "9": {
                        "title": "English [en], epub, 3.2MB, Treasure Island - Robert Louis Stevenson_1340.epub",
                        "link": "/md5/53a0b994062dc73b106144fdcbb8541d",
                        "value": 9,
                    },
                    "10": {
                        "title": "English [en], epub, 0.3MB, Stevenson, Robert Louis - Treasure Island (2012, ).epub",
                        "link": "/md5/abdb6dfe663b5fb4181123ea3973a38e",
                        "value": 10,
                    },
                    "11": {
                        "title": "English [en], epub, 0.3MB, [english] Stevenson, Robert Louis - Treasure Island.epub",
                        "link": "/md5/eabed0af49b234fa21c6029248816f25",
                        "value": 11,
                    },
                    "0": {
                        "title": "Continue in Browser",
                        "link": "https://url.that-is-launched-in-browser.com",
                        "value": 0,
                    },
                },
                True,
            ),
            (
                "detail_page_scrape",
                {
                    "1": {
                        "title": "Fast Partner Server #1",
                        "link": "/fast_download/4f95158d79dae74e16b5d0567be36fa6/0/0",
                        "value": 1,
                    },
                    "2": {
                        "title": "Fast Partner Server #2",
                        "link": "/fast_download/4f95158d79dae74e16b5d0567be36fa6/0/1",
                        "value": 2,
                    },
                    "3": {
                        "title": "Slow Partner Server #1",
                        "link": "/slow_download/4f95158d79dae74e16b5d0567be36fa6/0/0",
                        "value": 3,
                    },
                    "4": {
                        "title": "Slow Partner Server #2",
                        "link": "/slow_download/4f95158d79dae74e16b5d0567be36fa6/0/1",
                        "value": 4,
                    },
                    "5": {
                        "title": "Slow Partner Server #3",
                        "link": "/slow_download/4f95158d79dae74e16b5d0567be36fa6/0/2",
                        "value": 5,
                    },
                    "6": {
                        "title": "Libgen.li",
                        "link": "http://libgen.li/ads.php?md5=4f95158d79dae74e16b5d0567be36fa6",
                        "value": 6,
                    },
                    "7": {
                        "title": "Z-Library",
                        "link": "https://1lib.sk/md5/4f95158d79dae74e16b5d0567be36fa6",
                        "value": 7,
                    },
                    "0": {
                        "title": "Continue in Browser",
                        "link": "https://url.that-is-launched-in-browser.com",
                        "value": 0,
                    },
                },
                True,
            ),
        ],
    )
    def test__echo_results(
        self, _scrape_key, results, expected_to_have_results, mocker
    ):
        ebook = AnnasEbook(
            q=self.q,
            ext=self.ext,
            lang=self.lang,
            content=self.content,
            output_dir=self.output_dir,
        )
        mocker.patch.object(ebook, "_scrape_key", _scrape_key)
        match len(results.keys()):
            case 0:
                have_results = ebook._echo_results(results)
                assert have_results == expected_to_have_results
            case 1:
                spy = mocker.spy(click, "echo")
                have_results = ebook._echo_results(results)
                spy.assert_called_once_with("No Search Results Found")
                assert have_results == expected_to_have_results
            case _:
                spy_style = mocker.spy(click, "style")
                spy_echo = mocker.spy(click, "echo")
                spy_echo_formatted_title = mocker.spy(ebook, "_echo_formatted_title")
                have_results = ebook._echo_results(results)
                echo_calls = [
                    mocker.call(click.style("Search Results", fg="bright_cyan")),
                    mocker.call(click.style("==============", fg="bright_cyan")),
                    mocker.call(""),
                ]
                for key in results.keys():
                    value = results.get(key)
                    title = value.get("title", "")
                    if key == "0":
                        echo_calls.append(mocker.call(""))
                        echo_calls.append(
                            mocker.call(click.style(f" {key} | {title}", blink=True))
                        )
                    elif _scrape_key == "detail_page_scrape":
                        if any(
                            dl_partner in title
                            for dl_partner in AnnasEbook._MEMBER_LOGIN_REQUIRED
                        ):
                            echo_calls.append(
                                mocker.call(
                                    f" {key} | {title} - (Requires Member Login / {AnnasEbook._browser})"
                                )
                            )
                        elif AnnasEbook._SLOW_PARTNER_SERVER in title:
                            echo_calls.append(
                                mocker.call(
                                    f" {key} | {title} - (Browser Verification / {AnnasEbook._browser})"
                                )
                            )
                        else:
                            echo_calls.append(mocker.call(f" {key} | {title}"))
                    else:
                        title_list = title.split(", ", 3)
                        try:
                            [lang, ext, size, title_str] = title_list
                        except ValueError:
                            return echo_calls.append(
                                mocker.call(
                                    click.style(
                                        f" {key} | {AnnasEbook._ENTRY_NOT_DISPLAYED}",
                                        fg="bright_red",
                                    )
                                )
                            )
                        return echo_calls.append(
                            mocker.call(
                                f" {key} | {title_str} | {ext} | {size} | {lang}"
                            )
                        )
                echo_calls.append(mocker.call(""))
                spy_echo.assert_has_calls(echo_calls)
                assert have_results == expected_to_have_results

    @pytest.mark.parametrize(
        "_current_source, _scrape_key, html_file_path, expected_value, expected_selected_result",
        [
            (
                AnnasEbook._SOURCE_ANNAS,
                "search_page_scrape",
                "tests/static/annas_archive_search.html",
                5,
                {
                    "title": "English [en], pdf, 14.6MB, treasureisland0000stev_f7z0.pdf",
                    "link": "/md5/e5f954e12ce182fd530f7c16429a2134",
                    "value": 5,
                },
            ),
            (
                AnnasEbook._SOURCE_ANNAS,
                "detail_page_scrape",
                "tests/static/annas_archive_detail.html",
                3,
                {
                    "title": "Slow Partner Server #1",
                    "link": "/slow_download/4f95158d79dae74e16b5d0567be36fa6/0/0",
                    "value": 3,
                },
            ),
        ],
    )
    def test__scrape_page(
        self,
        _current_source,
        _scrape_key,
        html_file_path,
        expected_value,
        expected_selected_result,
        mocker,
    ):
        ebook = AnnasEbook(
            q=self.q,
            ext=self.ext,
            lang=self.lang,
            content=self.content,
            output_dir=self.output_dir,
        )
        mocker.patch.object(ebook, "_current_source", _current_source)
        mocker.patch.object(ebook, "_scrape_key", _scrape_key)
        mocker.patch.object(click, "prompt", return_value=expected_value)
        mock_get = mocker.patch.object(ebook, "_get")

        class MockResponse:
            @property
            def url(self):
                return AnnasEbook._SOURCE_DICT[AnnasEbook._SOURCE_ANNAS].get("url")

            @property
            def content(self):
                with open(html_file_path) as f:
                    return f.read()

        mock_get.return_value = MockResponse()
        value = ebook._scrape_page()
        assert value == expected_value
        assert ebook._selected_result == expected_selected_result

    @pytest.mark.parametrize(
        "_resource_name, html_file_path, output_dir, error",
        [
            (
                "English [en], epub, 0.3MB, Treasure Island - Stevenson, Robert Louis.epub",
                "tests/static/annas_archive_detail.html",
                "~/books/epub/dir",
                None,
            ),
            (
                "English [en], epub, 0.3MB, Treasure Island - Stevenson, Robert Louis.epub",
                "tests/static/annas_archive_detail.html",
                "~/books/epub/dir",
                FileNotFoundError,
            ),
            (
                "English [en], epub, 0.3MB, Treasure Island - Stevenson, Robert Louis.epub",
                "tests/static/annas_archive_detail.html",
                "",
                None,
            ),
            (
                "English [en], epub, 0.3MB, Treasure Island - Stevenson, Robert Louis.epub",
                "tests/static/annas_archive_detail.html",
                "",
                FileNotFoundError,
            ),
        ],
    )
    def test__to_filesystem(
        self, _resource_name, html_file_path, output_dir, error, mocker
    ):
        class MockResponse:
            @property
            def url(self):
                return AnnasEbook._SOURCE_DICT[AnnasEbook._SOURCE_ANNAS].get("url")

            @property
            def content(self):
                with open(html_file_path) as f:
                    return f.read()

        ebook = AnnasEbook(
            q=self.q,
            ext=self.ext,
            lang=self.lang,
            content=self.content,
            output_dir=self.output_dir,
        )
        spy_echo = mocker.spy(click, "echo")
        mocker.patch.object(ebook, "_resource_name", _resource_name)
        mocker.patch.object(ebook, "output_dir", output_dir)
        mock_open = mocker.mock_open()
        mocker.patch("src.getdat.utils.open", mock_open)
        error_msg = "Error found here"
        if error:
            mock_open.side_effect = error(error_msg)
            ebook._to_filesystem(response=MockResponse())
        else:
            ebook._to_filesystem(response=MockResponse())
        resource_name = _resource_name.split(", ", 3)[-1]
        if output_dir:
            resource_path = os.path.join(os.path.expanduser(output_dir), resource_name)
            mock_open.assert_called_once_with(resource_path, "wb")
            if error:
                spy_echo.assert_has_calls(
                    [
                        mocker.call(
                            click.style("Download Unsuccessful", fg="bright_red")
                        ),
                        mocker.call(click.style(f"{error_msg}", fg="bright_red")),
                    ]
                )
            else:
                spy_echo.assert_has_calls(
                    [mocker.call("Done 📚 🎆 🎇"), mocker.call(resource_path)]
                )
        else:
            mock_open.assert_called_once_with(resource_name, "wb")
            if error:
                spy_echo.assert_has_calls(
                    [
                        mocker.call(
                            click.style("Download Unsuccessful", fg="bright_red")
                        ),
                        mocker.call(click.style(f"{error_msg}", fg="bright_red")),
                    ]
                )
            else:
                spy_echo.assert_has_calls(
                    [mocker.call("Done 📚 🎆 🎇"), mocker.call(resource_name)]
                )

    @pytest.mark.parametrize(
        "title, error",
        [
            ("Success", None),
            ("Error Title", ConnectionError),
            ("Error Title", ChunkedEncodingError),
        ],
    )
    def test__download(self, title, error, mocker):
        ebook = AnnasEbook(
            q=self.q,
            ext=self.ext,
            lang=self.lang,
            content=self.content,
            output_dir=self.output_dir,
        )
        mocked__to_filesystem = mocker.patch.object(ebook, "_to_filesystem")
        mocked_get = mocker.patch.object(ebook, "_get")
        echo_spy = mocker.spy(click, "echo")
        if error:
            mocked_get.side_effect = error
            ebook._download(title)
            echo_spy.assert_called_once_with(
                click.style(
                    f"Direct Download Not Available from {title}.\n Try Another Download Link",
                    fg="red",
                )
            )
        else:

            class MockResponse:
                def __init__(self):
                    self._status_code = 200
                    self._content_type = EPUB_CONTENT_TYPE

                @property
                def headers(self):
                    headers = dict()
                    headers["Content-Type"] = self._content_type
                    return headers

                @property
                def status_code(self):
                    return self._status_code

            response = MockResponse()
            mocked_get.return_value = response
            ebook._download(title)
            mocked__to_filesystem.assert_called_once_with(response)

    @pytest.mark.parametrize(
        (
            "_selected_result, response_status_code, "
            "error, response_content_type, is_ipfs, "
            "is_libgen, page_results"
        ),
        [
            (
                {
                    "title": "Fast Partner Server #1",
                    "link": "/fast_download/4f95158d79dae74e16b5d0567be36fa6/0/0",
                    "value": 1,
                },
                200,
                None,
                PDF_CONTENT_TYPE,
                False,
                False,
                None,
            ),
            (
                {
                    "title": "Fast Partner Server #1 Continue in Browser",
                    "link": "/fast_download/4f95158d79dae74e16b5d0567be36fa6/0/0",
                    "value": 1,
                },
                200,
                None,
                AnnasEbook._HTML_CONTENT_TYPE,
                False,
                False,
                None,
            ),
            (
                {
                    "title": "Fast Partner Server #1 IPFS",
                    "link": "/ipfs/fast_download/4f95158d79dae74e16b5d0567be36fa6/0/0",
                    "value": 1,
                },
                200,
                None,
                AnnasEbook._HTML_CONTENT_TYPE,
                True,
                False,
                None,
            ),
            (
                {
                    "title": "Slow Partner Server #1",
                    "link": "/slow_download/4f95158d79dae74e16b5d0567be36fa6/0/0",
                    "value": 3,
                },
                500,
                ConnectionError,
                PDF_CONTENT_TYPE,
                False,
                False,
                None,
            ),
            (
                {
                    "title": "IPFS Gateway #1",
                    "link": "https://cloudflare-ipfs/ipfs/md5=4f95158d79dae74e16b5d0567be36fa6",
                    "value": 6,
                },
                200,
                None,
                AnnasEbook._HTML_CONTENT_TYPE,
                True,
                False,
                None,
            ),
            (
                {
                    "title": "Slow Partner Server #1",
                    "link": "/slow_download/4f95158d79dae74e16b5d0567be36fa6/0/0",
                    "value": 3,
                },
                500,
                ChunkedEncodingError,
                EPUB_CONTENT_TYPE,
                False,
                False,
                None,
            ),
            (
                {
                    "title": AnnasEbook._LIBGEN_LI,
                    "link": "app.php?md5=4f95158d79dae74e16b5d0567be36fa6",
                    "value": 6,
                },
                200,
                None,
                AnnasEbook._HTML_CONTENT_TYPE,
                False,
                True,
                {
                    "61": {
                        "title": "GET",
                        "link": "get.php?md5=4f95158d79dae74e16b5d0567be36fa6&key=8ETFRGFWBSSQMDRV",
                        "value": 61,
                    },
                    "0": {
                        "title": "Continue in Browser",
                        "link": "https://url.that-is-launched-in-browser.com",
                        "value": 0,
                    },
                },
            ),
            (
                {
                    "title": AnnasEbook._LIBGEN_RS,
                    "link": "app.php?md5=4f95158d79dae74e16b5d0567be36fa6",
                    "value": 6,
                },
                200,
                None,
                AnnasEbook._HTML_CONTENT_TYPE,
                False,
                True,
                {
                    "1": {
                        "title": "GET",
                        "link": "https://download.library.lol/fiction/1511000/eabed0af49b234fa21c6029248816f25.epub/Stevenson%2C%20Robert%20Louis%20-%20Treasure%20Island.epub",
                        "value": 1,
                    },
                    "0": {
                        "title": "Continue in Browser",
                        "link": "https://url.that-is-launched-in-browser.com",
                        "value": 0,
                    },
                },
            ),
        ],
    )
    def test__dl_or_launch_page(
        self,
        _selected_result,
        response_status_code,
        error,
        response_content_type,
        is_ipfs,
        is_libgen,
        page_results,
        mocker,
    ):
        title = _selected_result.get("title")

        class MockResponse:
            def __init__(self, status_code, content_type):
                self._status_code = status_code
                self._content_type = content_type

            @property
            def headers(self):
                headers = dict()
                headers["Content-Type"] = self._content_type
                return headers

            @property
            def status_code(self):
                return self._status_code

            @property
            def url(self):
                return AnnasEbook._SOURCE_DICT[AnnasEbook._SOURCE_ANNAS].get("url")

            @property
            def content(self):
                with open("tests/static/libgen_rs_detail.html") as f:
                    return f.read()

        ebook = AnnasEbook(
            q=self.q,
            ext=self.ext,
            lang=self.lang,
            content=self.content,
            output_dir=self.output_dir,
        )
        mocked_get = mocker.patch.object(requests, "get")
        mocker.patch.object(ebook, "_current_source", AnnasEbook._SOURCE_ANNAS)
        mocker.patch.object(ebook, "_selected_result", _selected_result)
        msg = f"\nTalking to {title}..."
        mocker.patch.object(ebook, "_msg", msg)
        launch_browser = mocker.patch.object(click, "launch")
        echo_spy = mocker.spy(click, "echo")
        echo_calls = [mocker.call(click.style(msg, fg="bright_yellow"))]

        if error:
            mocked_get.side_effect = error
            ebook._dl_or_launch_page()
            echo_calls = [
                *echo_calls,
                mocker.call(""),
                mocker.call(click.style("No connection established", fg="bright_red")),
            ]
            echo_spy.assert_has_calls(echo_calls)
            link = ebook._determine_link()
            launch_browser.assert_called_once_with(link)

        elif response_status_code != 200:
            mocked_get.return_value = MockResponse()
            ebook._dl_or_launch_page()
            echo_calls.append(
                mocker.call(
                    click.style(
                        f"Direct Download Not Available from {title}.\n Try Another Download Link",
                        fg="red",
                    )
                )
            )
            echo_spy.assert_has_calls(echo_calls)

        elif response_content_type != AnnasEbook._HTML_CONTENT_TYPE:
            response = MockResponse(
                status_code=response_status_code, content_type=response_content_type
            )
            mocked_get.return_value = response
            mock_to_fs = mocker.patch.object(ebook, "_to_filesystem")
            ebook._dl_or_launch_page()
            mock_to_fs.assert_called_once_with(response)
            echo_spy.assert_has_calls(echo_calls)

        elif response_content_type == AnnasEbook._HTML_CONTENT_TYPE and is_ipfs:
            mocked_get.return_value = MockResponse(
                status_code=response_status_code, content_type=response_content_type
            )
            ebook._dl_or_launch_page()
            link = ebook._determine_link()
            if AnnasEbook._IPFS_URI in link:
                echo_calls = [
                    *echo_calls,
                    mocker.call(""),
                    mocker.call(
                        click.style(
                            f"Direct Download Not Available from {title}.\n Try Another Download Link",
                            fg="red",
                        )
                    ),
                ]
                echo_spy.assert_has_calls(echo_calls)

        elif response_content_type == AnnasEbook._HTML_CONTENT_TYPE and is_libgen:
            mock_scrape_results = mocker.patch.object(
                ebook,
                "_scrape_results",
            )
            mock_download = mocker.patch.object(ebook, "_download")
            mock_scrape_results.return_value = page_results
            mocked_get.return_value = MockResponse(
                status_code=response_status_code, content_type=response_content_type
            )
            ebook._dl_or_launch_page()

            if title == AnnasEbook._LIBGEN_LI:
                link = page_results["61"].get("link")
                url = AnnasEbook._SOURCE_DICT[AnnasEbook._LIBGEN_LI].get("url")
                mock_download.assert_called_once_with(title, link=f"{url}{link}")
            elif title == AnnasEbook._LIBGEN_RS:
                mock_download.assert_called_once_with(
                    title, link=page_results["1"].get("link")
                )
        else:
            launch_browser = mocker.patch.object(click, "launch")
            mocked_get.return_value = MockResponse(
                status_code=response_status_code, content_type=response_content_type
            )
            ebook._dl_or_launch_page()
            link = ebook._determine_link()
            launch_browser.assert_called_once_with(link)

    @pytest.mark.parametrize(
        "value_1, value_2",
        [(0, None), (1, 0), (1, 1)],
    )
    def test_run(self, value_1, value_2, mocker):
        selected_result_1 = {
            "title": "Z-Library",
            "link": "https://1lib.sk/md5/4f95158d79dae74e16b5d0567be36fa6",
            "value": 7,
        }
        selected_result_2 = {
            "title": "IPFS Gateway #1",
            "link": "https://cloudflare-ipfs/ipfs/md5=4f95158d79dae74e16b5d0567be36fa6",
            "value": 6,
        }
        link_1 = selected_result_1.get("link")
        link_2 = selected_result_2.get("link")
        ebook = AnnasEbook(
            q=self.q,
            ext=self.ext,
            lang=self.lang,
            content=self.content,
            output_dir=self.output_dir,
        )
        mocked_launch_browser = mocker.patch.object(click, "launch")
        mocked__scrape_page = mocker.patch.object(
            ebook,
            "_scrape_page",
        )
        mocker.patch.object(
            ebook,
            "_selected_result",
            return_value=[selected_result_1, selected_result_2],
        )
        mocked__dl_or_launch_page = mocker.patch.object(ebook, "_dl_or_launch_page")
        mocked__scrape_page.side_effect = [value_1, value_2]
        spy_clear = mocker.spy(click, "clear")
        if value_1 == 0 and value_2 is None:
            ebook.run()
            mocked_launch_browser.assert_called_once()
            mocked__dl_or_launch_page.assert_not_called()
            spy_clear.assert_not_called()
        elif value_1 == 1 and value_2 == 0:
            ebook.run()
            mocked_launch_browser.assert_called_once()
            mocked__dl_or_launch_page.assert_not_called()
            spy_clear.assert_called_once()
        else:
            ebook.run()
            mocked_launch_browser.assert_not_called()
            mocked__dl_or_launch_page.assert_called_once()
            assert spy_clear.call_count == 2
