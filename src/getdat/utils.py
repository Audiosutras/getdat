import click
import os
import requests
from typing import Literal
from requests.exceptions import ConnectionError, ChunkedEncodingError
from requests.models import Response
from bs4 import BeautifulSoup


def print_help(msg: str):
    click.echo(click.style(msg, fg="red"))
    click.echo("")
    ctx = click.get_current_context()
    click.echo(ctx.get_help())
    ctx.exit()


class AnnasEbook:

    _ENTRY_NOT_DISPLAYED = "Entry information could not be displayed"
    _FAST_PARTNER_SERVER = "Fast Partner Server"
    _SLOW_PARTNER_SERVER = "Slow Partner Server"
    _INTERNET_ARCHIVE = "Borrow from the Internet Archive"
    _Z_LIBRARY = "Z-Library"
    _LIBGEN_RS = "Libgen.rs Non-Fiction"
    _LIBGEN_LI = "Libgen.li"
    _LIBGEN_EXTERNAL = (
        _LIBGEN_RS,
        _LIBGEN_LI,
    )
    _MEMBER_LOGIN_REQUIRED = (_FAST_PARTNER_SERVER, _INTERNET_ARCHIVE, _Z_LIBRARY)
    _HTML_CONTENT_TYPE = "text/html"
    _PDF_CONTENT_TYPE = "application/pdf"
    _EPUB_CONTENT_TYPE = "application/epub+zip"
    _EXPECTED_DL_CONTENT_TYPES = (_PDF_CONTENT_TYPE, _EPUB_CONTENT_TYPE)
    _IPFS_URI = "ipfs"

    _SOURCE_ANNAS = "Anna's Archive"

    _ANNAS_ORG_URL = "org"
    _ANNAS_GS_URL = "gs"
    _ANNAS_SE_URL = "se"
    _ANNAS_URLS = {
        _ANNAS_ORG_URL: "https://annas-archive.org",
        _ANNAS_GS_URL: "https://annas-archive.gs",
        _ANNAS_SE_URL: "https://annas-archive.se",
    }

    _SOURCE_DICT = {
        _SOURCE_ANNAS: {
            "name": _SOURCE_ANNAS,
            "url": _ANNAS_URLS.get(_ANNAS_ORG_URL),
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
        _LIBGEN_RS: {"download_page_scrape": {"tag": "a"}},
        _LIBGEN_LI: {"url": "https://libgen.li/", "download_page_scrape": {"tag": "a"}},
    }
    _current_source = _SOURCE_ANNAS
    _browser = "Continue in Browser"
    _scrape_key = "search_page_scrape"
    _selected_result = {}
    _msg = "Searching Anna's Archive..."
    _resource_name = ""

    def __init__(
        self,
        q: tuple,
        ext: str,
        output_dir: str,
        instance: Literal[*_ANNAS_URLS.keys()] = _ANNAS_ORG_URL,
    ):
        self.q = " ".join(map(str, q))
        self.output_dir = output_dir or os.environ.get("GETDAT_BOOK_DIR")
        self.ext = ext
        self.instance = instance

    def _determine_source(self) -> dict:
        source = self._SOURCE_DICT.get(self._current_source)
        if self._current_source == self._SOURCE_ANNAS:
            annas_url = self._ANNAS_URLS.get(self.instance)
            source.update({"url": annas_url})
        return source

    def _determine_link(self) -> str:
        source = self._determine_source()
        url = source.get("url")
        link = self._selected_result.get("link")
        if any(
            protocal in self._selected_result.get("link")
            for protocal in ["https://", "http://"]
        ):
            return link
        return f"{url}{link}"

    def _get_url(self, *args, **kwargs) -> str:
        link = kwargs.get("link")
        if link:
            return link
        source = self._determine_source()
        url = source.get("url")
        match self._scrape_key:
            case "search_page_scrape":
                search = f"/search?q={self.q}"
                if self.ext:
                    search += f"&ext={self.ext}"
                return f"{url}{search}"
            case _:
                return self._determine_link()

    def _get(self, *args, **kwargs):
        click.echo(click.style(f"\n{self._msg}", fg="bright_yellow"))
        click.echo("")
        try:
            response = requests.get(self._get_url(*args, **kwargs))
        except (ConnectionError, ChunkedEncodingError) as e:
            click.echo(click.style("No connection established", fg="bright_red"))
            raise e
        else:
            return response

    def _scrape_results(self, response: Response) -> dict:
        soup = BeautifulSoup(response.content, "html.parser")
        source = self._determine_source()
        scrape = source.get(self._scrape_key, {})
        tag = scrape.get("tag", "")
        tag_class = scrape.get("class", "")
        results = dict()
        match self._scrape_key:
            case "search_page_scrape":
                title_container = scrape.get("title_container")
                tag_title_container = title_container.get("tag")
                class_title_container = title_container.get("class")
                for idx, el in enumerate(soup.find_all(tag, class_=tag_class)):
                    title = el.find(
                        tag_title_container, class_=class_title_container
                    ).string
                    results[str(idx + 1)] = {
                        "title": title,
                        "link": el["href"],
                        "value": idx + 1,
                    }
            case "detail_page_scrape":
                for idx, el in enumerate(soup.find_all(tag, class_=tag_class)):
                    if el.string != "Bulk torrent downloads":
                        results[str(idx + 1)] = {
                            "title": el.string,
                            "link": el["href"],
                            "value": idx + 1,
                        }
            case "download_page_scrape":
                for idx, el in enumerate(soup.find_all(tag)):
                    # libgen pages
                    if el.string == "GET":
                        # should only be 1 entry
                        results[str(idx + 1)] = {
                            "title": el.string,
                            "link": el["href"],
                            "value": idx + 1,
                        }
        results["0"] = {"title": self._browser, "link": response.url, "value": 0}
        return results

    def _echo_formatted_title(self, key, title_str):
        title_list = title_str.split(", ", 3)
        try:
            [lang, ext, size, title] = title_list
        except ValueError:
            return click.echo(
                click.style(f" {key} | {self._ENTRY_NOT_DISPLAYED}", fg="bright_red")
            )
        return click.echo(f" {key} | {title} | {ext} | {size} | {lang}")

    def _echo_results(self, results) -> bool:
        have_results = True
        if len(results.keys()) == 1:
            click.echo("No Search Results Found")
            have_results = False
            return have_results
        if len(results.keys()) == 0:
            have_results = False
            return have_results
        click.echo(click.style("Search Results", fg="bright_cyan"))
        click.echo(click.style("==============", fg="bright_cyan"))
        click.echo("")
        for key in results.keys():
            value = results.get(key)
            title = value.get("title")
            if key == "0":
                click.echo("")
                click.echo(click.style(f" {key} | {title}", blink=True))
            elif self._scrape_key == "detail_page_scrape":
                if any(
                    dl_partner in title for dl_partner in self._MEMBER_LOGIN_REQUIRED
                ):
                    click.echo(
                        f" {key} | {title} - (Requires Member Login / {self._browser})"
                    )
                elif self._SLOW_PARTNER_SERVER in title:
                    click.echo(
                        f" {key} | {title} - (Browser Verification / {self._browser})"
                    )
                else:
                    click.echo(f" {key} | {title}")
            else:
                self._echo_formatted_title(key, title)
        click.echo("")
        return have_results

    def _scrape_page(self, *args, **kwargs) -> int:
        try:
            response = self._get(*args, **kwargs)
        except (ConnectionError, ChunkedEncodingError):
            ctx = click.get_current_context()
            ctx.exit(1)
        else:
            results = self._scrape_results(response)
            have_results = self._echo_results(results)
            if have_results:
                value = click.prompt(
                    "Select Number", type=click.IntRange(min=0, max=(len(results) - 1))
                )
                self._selected_result = results.get(str(value))
                selected_link = self._selected_result.get("link")
                return value

    def _to_filesystem(self, response: Response):
        """Write file to filesystem if it does not already exists

        Throws a FileNotFoundError if self.output_dir is not valid
        """
        resource_name = self._resource_name.split(", ", 3)[-1]
        if self.output_dir:
            resource_path = os.path.join(
                os.path.expanduser(self.output_dir), resource_name
            )
            try:
                with open(resource_path, "wb") as f:
                    f.write(response.content)
            except FileNotFoundError as e:
                click.echo(click.style("Download Unsuccessful", fg="bright_red"))
                click.echo(click.style(f"{e}", fg="bright_red"))
            else:
                click.echo("Done 📚 🎆 🎇")
                click.echo(resource_path)
        else:
            try:
                with open(resource_name, "wb") as f:
                    f.write(response.content)
            except FileNotFoundError as e:
                click.echo(click.style("Download Unsuccessful", fg="bright_red"))
                click.echo(click.style(f"{e}", fg="bright_red"))
            else:
                click.echo("Done 📚 🎆 🎇")
                click.echo(resource_name)

    def _download(self, title, *args, **kwargs):
        try:
            response = self._get(*args, **kwargs)
        except (ConnectionError, ChunkedEncodingError):
            return click.echo(
                click.style(
                    f"Direct Download Not Available from {title}.\n Try Another Download Link",
                    fg="red",
                )
            )
        else:
            self._to_filesystem(response)

    def _dl_or_launch_page(self, *args, **kwargs):
        title = self._selected_result.get("title")
        link = self._determine_link()
        self._msg = f"Talking to {title}..."

        try:
            response = self._get(*args, **kwargs)
        except (ConnectionError, ChunkedEncodingError):
            return click.launch(link)
        else:
            if response.status_code != 200:
                return click.echo(
                    click.style(
                        f"Direct Download Not Available from {title}.\n Try Another Download Link",
                        fg="red",
                    )
                )
            content_type = response.headers.get("Content-Type")
            if content_type in self._EXPECTED_DL_CONTENT_TYPES:  # ipfs
                self._to_filesystem(response)
            elif content_type == self._HTML_CONTENT_TYPE and self._IPFS_URI in link:
                return click.echo(
                    click.style(
                        f"Direct Download Not Available from {title}.\n Try Another Download Link",
                        fg="red",
                    )
                )
            elif any(libgen in title for libgen in self._LIBGEN_EXTERNAL):  # libgen
                for libgen in self._LIBGEN_EXTERNAL:
                    if libgen in title:
                        self._current_source = libgen
                self._scrape_key = "download_page_scrape"
                results = self._scrape_results(response)
                libgen_key = list(results.keys())[0]
                link = results.get(libgen_key).get("link")
                self._msg = ""
                if title == self._LIBGEN_LI:
                    source = self._determine_source()
                    link = f"{source.get('url')}{link}"
                    kwargs["link"] = link
                    self._download(title, *args, **kwargs)
                elif title == self._LIBGEN_RS:
                    kwargs["link"] = link
                    self._download(title, *args, **kwargs)
            else:  # Browser Only Options
                click.launch(link)

    def run(self, *args, **kwargs):
        self._msg = f"Searching Anna's Archive: {self.q}"
        value = self._scrape_page(*args, **kwargs)
        if value == 0:
            return click.launch(self._selected_result.get("link"))
        click.clear()
        self._resource_name = self._selected_result.get("title")
        click.echo("")
        click.echo("")
        click.echo(click.style("Selected", fg="bright_cyan"))
        click.echo("")
        self._echo_formatted_title(
            self._selected_result.get("value"), self._selected_result.get("title")
        )
        self._scrape_key = "detail_page_scrape"
        click.echo(click.style("==============", fg="bright_cyan"))
        self._msg = "Fetching Download Links..."
        value = self._scrape_page(*args, **kwargs)
        if value == 0:
            return click.launch(self._selected_result.get("link"))
        click.clear()
        self._scrape_key = ""
        self._dl_or_launch_page(*args, **kwargs)
