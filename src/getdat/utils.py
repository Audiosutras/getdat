import click
import requests
from webbrowser import open_new_tab
from bs4 import BeautifulSoup
from tqdm import tqdm


class Ebook:
    
    source_options = {
        "annas_archive": {
            "name": "Anna's Archive",
            "url": "https://annas-archive.org/search?q=",
            "search-1-scrape": {
                "tag": "a",
                "tag_is_link": True,
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
            }
        }
    }

    def __init__(self, q: tuple, source: str, ext: str, browser: bool):
        self.q = q
        self.source = source
        self.ext = ext
        self.browser = browser
    
    def _source_info(self, key: str) -> str:
        source_dict = self.source_options.get(self.source)
        return source_dict.get(key)

    def _get_url(self) -> str:
        match self.source:
            case "annas_archive":
                search = ' '.join(map(str, self.q))
                if self.ext:
                     search += f'&ext={self.ext}'
                url = self._source_info("url")
                return f"{url}{search}"
    
    def _get(self):
        source_name = self._source_info("name")
        click.echo(f"\nSearching {source_name}...")
        click.echo("")
        return requests.get(self._get_url())
    
    def _scrape(self, scrape_key, response):
        soup = BeautifulSoup(response.content, 'html.parser')
        scrape = self._source_info(key=scrape_key)
        tag = scrape.get("tag")
        tag_class = scrape.get("class")
        title_container = scrape.get("title_container")
        tag_title_container = title_container.get("tag")
        class_title_container = title_container.get("class")
        tag_is_link = scrape.get("tag_is_link", False)
        search_results = dict()
        for idx, el in enumerate(soup.find_all(tag, class_=tag_class)):
            title = el.find(tag_title_container, class_=class_title_container).string
            if tag_is_link:
                search_results[idx + 1] = {
                    "title": title,
                    "link": el["href"]
                }
        return search_results



    
    def run(self):
        if self.browser:
            return open_new_tab(self._get_url())
        response = self._get()
        search_results = self._scrape("search-1-scrape", response)
        if len(search_results.keys()) == 0:
            return click.echo("No Search Results Found")
        
        click.echo("Search Results")
        for key in search_results.keys():
            value = search_results.get(key)
            title = value.get("title")
            click.echo(f"{key}. {title}")
        click.echo("")
            
    
