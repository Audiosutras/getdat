import click
from requests import get
from requests.exceptions import ConnectionError
from requests.models import Response
from webbrowser import open_new_tab
from bs4 import BeautifulSoup


class AnnasEbook:
    
    _source_dict = {
        "name": "Anna's Archive",
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
    }
    _scrape_key = "search_page_scrape"    
    _selected_result = {}
    _msg = "for search results..."

    def __init__(self, q: tuple,  ext: str):
        self.q = q
        self.ext = ext
    
    def _source_info(self, key: str) -> str:
        return self._source_dict.get(key)

    def _get_url(self, *args, **kwargs) -> str:
        url = self._source_info("url")
        match self._scrape_key:
            case "search_page_scrape":
                search = f'/search?q={' '.join(map(str, self.q))}'
                if self.ext:
                    search += f'&ext={self.ext}'
                return f"{url}{search}"
            case _:
                if any(protocal in self._selected_result.get("link") for protocal in ['https://', 'http://']):
                    return self._selected_result.get("link")
                return f"{url}{self._selected_result.get("link")}"
    
    def _get(self, *args, **kwargs):
        source_name = self._source_info("name")
        click.echo(f"\nSearching {source_name} {self._msg}")
        click.echo("")
        try:
            response = get(self._get_url(*args, **kwargs))
        except ConnectionError:
            click.echo("No connection established to Anna's Archive")
            click.echo("")
        else:
            return response

    def _scrape(self, response: Response) -> dict:
        soup = BeautifulSoup(response.content, 'html.parser')
        scrape = self._source_info(key=self._scrape_key)
        tag = scrape.get("tag")
        tag_class = scrape.get("class")
        results = dict()
        match self._scrape_key:
            case "search_page_scrape":
                title_container = scrape.get("title_container")
                tag_title_container = title_container.get("tag")
                class_title_container = title_container.get("class")
                for idx, el in enumerate(soup.find_all(tag, class_=tag_class)):
                    title = el.find(tag_title_container, class_=class_title_container).string
                    results[str(idx + 1)] = {
                        "title": title,
                        "link": el["href"],
                        "value": idx + 1
                    }
            case "detail_page_scrape":
                for idx, el in enumerate(soup.find_all(tag, class_=tag_class)):
                    if el.string != 'Bulk torrent downloads':
                        results[str(idx + 1)] = {
                            "title": el.string,
                            "link": el["href"],
                            "value": idx + 1
                        }
        results["0"] = {
            "title": "Continue In Browser",
            "link": response.url,
            "value": 0
        }
        return results
    
    @staticmethod
    def _echo_formatted_title(key, title_str):
            title_list = title_str.split(", ", 3)
            try:
                [lang, ext, size, title] = title_list
            except ValueError:
                return click.echo(click.style(f" {key} | Entry could not be parsed", fg="red"))
            return click.echo(f" {key} | {title} | {ext} | {size} | {lang}")
    
    def _echo_results(self, results) -> bool:
        have_results = True
        if len(results.keys()) == 1:
            click.echo("No Search Results Found")
            have_results = False
            return have_results
        click.echo(click.style("Search Results", fg="magenta"))
        click.echo(click.style("==============", fg="magenta"))
        click.echo("")
        for key in results.keys():
            value = results.get(key)
            title= value.get("title")
            if key == "0":
                click.echo("")
                click.echo(
                    click.style(f" {key} | {title}", blink=True)
                )
            elif self._scrape_key == "detail_page_scrape":
                if 'Fast Partner Server' in title:
                    click.echo(f" {key} | {title} - (Continue in Browser / Requires Member Login)")
                elif 'Slow Partner Server' in title:
                    click.echo(f" {key} | {title} - (Continue in Browser / Browser Verification)")
                else:
                    click.echo(f" {key} | {title}")
            else:
                self._echo_formatted_title(key, title)
        click.echo("")
        click.echo("")
        return have_results
    
    def _scrape_page(self, *args, **kwargs) -> int:
        response = self._get(*args, **kwargs)
        results = self._scrape(response)
        have_results = self._echo_results(results)
        if have_results:
            value = click.prompt("Select Number", type=click.IntRange(min=0, max=(len(results) - 1)))
            self._selected_result = results.get(str(value))
            selected_link = self._selected_result.get("link")
            return value
    
    def _download_selected_result(self, *args, **kwargs):
        response = self._get(*args, **kwargs)
        click.echo(response)

    def run(self, *args, **kwargs):
        value = self._scrape_page(*args, **kwargs)
        if value == 0:
            return open_new_tab(self._selected_result.get("link"))
        click.echo("")
        click.echo(click.style("Selected", fg="magenta"))
        click.echo("")
        self._echo_formatted_title(self._selected_result.get("value"), self._selected_result.get("title"))
        self._scrape_key = "detail_page_scrape"
        click.echo(click.style("==============", fg="magenta"))
        self._msg = "for download links..."
        value = self._scrape_page(*args, **kwargs)
        if value == 0:
            return open_new_tab(self._selected_result.get("link"))
        self._download_selected_result(*args, **kwargs)
        
    
