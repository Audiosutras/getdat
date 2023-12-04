import click
from .utils import AnnasEbook, print_help
from .constants import EBOOK_ERROR_MSG, MOVIE_WEB, TOTALSPORTK, BRAINTRUST


@click.group(
    epilog="Check out our docs at https://getdat.chrisdixononcode.dev for help and contributing."
)
def cli():
    """A command line utility for getting resources available online"""
    pass


@cli.command()
def job():
    """Launches braintrust, the job board powered by blockchain, in your default browser"""
    click.launch(BRAINTRUST)


@cli.command()
def sport():
    """Launches totalsportk in your default browser"""
    click.launch(TOTALSPORTK)


@cli.command()
def cinema():
    """Launches movie-web.app in your default browser"""
    click.launch(MOVIE_WEB)


@cli.command()
@click.option(
    "-o",
    "--output_dir",
    help=(
        "Path to ebook's output directory from home directory. "
        "Path must be prefixed by '~' on Unix or '~user' on Windows. "
        "This argument overrides GETDAT_BOOK_DIR env var if set. "
        "Outputs book to working directory if neither are set."
    ),
)
@click.option(
    "-e",
    "--ext",
    help=(
        "Preferred ebook extension for ebooks in search results. "
        f"Options: {', '.join(AnnasEbook._FILE_EXT)}. "
        "Filter by multiple file extensions supported. Example: "
        "pdf,epub,mobi"
    ),
)
@click.option(
    "-l",
    "--lang",
    help=(
        "Preferred language of ebooks in search results. "
        "Provided Language must be ISO 639-1 format. "
        "Language region extension supported. "
        "Filtering by multiple languages supported. "
        "Examples: English - en, Spanish - es, Traditional "
        "Chinese - zh-Hant, Multiple Langauges - en,es,zh-Hant "
    ),
)
@click.option(
    "-c",
    "--content",
    help=(
        "The type of content you want as ebook search results. "
        f"{AnnasEbook._CONTENT_OPTIONS_EBOOK_HELP}. "
        "Supports filtering by multiple content types. "
        " Example: nf,f,cb"
    ),
)
@click.option(
    "-s",
    "--sort",
    type=click.Choice(AnnasEbook._SORT_ENTRIES),
    help=(
        "Preferred sorting of search results for ebooks. By "
        "default search results are sorted by most relevant results. "
        "Sort by: Newest entries, oldest entries, entries with the "
        "smallest size, entries with the largest size."
    ),
)
@click.option(
    "-i",
    "--instance",
    type=click.Choice(AnnasEbook._ANNAS_URLS.keys()),
    default=AnnasEbook._ANNAS_ORG_URL,
    help=(
        "The instance of Anna's Archive you would like to "
        "use for your search:\n "
        f"{', '.join(AnnasEbook._ANNAS_URLS.values())}\n"
        f"- Default: {AnnasEbook._ANNAS_ORG_URL}"
    ),
)
@click.argument("q", nargs=-1)
def ebook(q, ext, lang, content, sort, output_dir, instance):
    """Search and download an ebook available through Anna's Archive

    ex: getdat ebook <Search>
    """
    if not q:
        print_help(EBOOK_ERROR_MSG)
    ebook = AnnasEbook(
        q=q,
        ext=ext,
        lang=lang,
        content=content,
        sort=sort,
        output_dir=output_dir,
        instance=instance,
    )
    ebook.run()
