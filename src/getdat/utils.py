import click
import requests
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

    def __init__(self, q: tuple,  ext: str):
        self.q = q
        self.ext = ext
    
    def _source_info(self, key: str) -> str:
        return self._source_dict.get(key)

    def _get_url(self, *args, **kwargs) -> str:
        url = self._source_info("url")
        if not kwargs.get("uri"):
            search = f'/search?q={' '.join(map(str, self.q))}'
            if self.ext:
                search += f'&ext={self.ext}'
            return f"{url}{search}"
        return f"{url}{kwargs.get("uri")}"
    
    def _get(self, *args, **kwargs):
        msg = kwargs.get("msg", "...")
        source_name = self._source_info("name")
        click.echo(f"\nSearching {source_name}{msg}")
        click.echo("")
        return requests.get(self._get_url(*args, **kwargs))
    
    def _scrape(self, scrape_key, response):
        soup = BeautifulSoup(response.content, 'html.parser')
        scrape = self._source_info(key=scrape_key)
        tag = scrape.get("tag")
        tag_class = scrape.get("class")
        search_results = dict()
        match scrape_key:
            case "search_page_scrape":
                title_container = scrape.get("title_container")
                tag_title_container = title_container.get("tag")
                class_title_container = title_container.get("class")
                for idx, el in enumerate(soup.find_all(tag, class_=tag_class)):
                    title = el.find(tag_title_container, class_=class_title_container).string
                    search_results[str(idx + 1)] = {
                        "title": title,
                        "link": el["href"]
                    }
            case "detail_page_scrape":
                for idx, el in enumerate(soup.find_all(tag, class_=tag_class)):
                    click.echo(el["href"])
        search_results["0"] = {
            "title": "Continue In Browser",
            "link": response.url
        }
        return search_results
    
    @staticmethod
    def _echo_formatted_title(key, title):
            title_list = title.split(", ", 3)
            [lang, ext, size, title] = title_list
            return click.echo(f" {key} | {title} | {ext} | {size} | {lang}")
    
    def _echo_results(self, search_results) -> bool:
        are_search_results = True
        if len(search_results.keys()) == 1:
            click.echo("No Search Results Found")
            are_search_results = False
            return are_search_results
        click.echo(click.style("Search Results", fg="magenta"))
        click.echo(click.style("==============", fg="magenta"))
        click.echo("")
        for key in search_results.keys():
            value = search_results.get(key)
            title= value.get("title")
            if key == "0":
                click.echo("")
                click.echo(
                    click.style(f" {key} | {title}", blink=True)
                )
            else:
                self._echo_formatted_title(key, title)
        click.echo("")
        click.echo("")
        return are_search_results

    
    def run(self, *args, **kwargs):
        search_page_response = self._get()
        search_results = self._scrape("search_page_scrape", search_page_response)
        are_search_results = self._echo_results(search_results)
        if are_search_results:
            value = click.prompt("Select Number", type=click.IntRange(min=0, max=(len(search_results) - 1)))
            selected_search_result = search_results.get(str(value))
            value_link = selected_search_result.get("link")
            if value == 0:
                return open_new_tab(value_link)
            click.echo("")
            click.echo(click.style("Selected", fg="magenta"))
            click.echo("")
            title = selected_search_result.get("title")
            self._echo_formatted_title(value, title)
            click.echo(click.style("==============", fg="magenta"))
            kwargs["uri"] = value_link
            kwargs["msg"] = " for download links..."
            detail_page_response = self._get(**kwargs)
            search_results = self._scrape("detail_page_scrape", detail_page_response)
   
            
    
