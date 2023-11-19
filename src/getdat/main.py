import click
from .utils import AnnasEbook, print_help
from .constants import EBOOK_ERROR_MSG, MOVIE_WEB, TOTALSPORTK


@click.group(
    epilog="Check out our docs at https://audiosutras.github.io/getdat/ for more details"
)
def cli():
    """A command line utility for getting resources available online"""
    pass


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
    type=click.Choice(["epub", "pdf"]),
    default="epub",
    help=("Preferred ebook extension for search results " "- Default: epub"),
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
def ebook(q, ext, output_dir, instance):
    """Search and download an ebook available through Anna's Archive

    ex: getdat ebook <Search>
    """
    if not q:
        print_help(EBOOK_ERROR_MSG)
    ebook = AnnasEbook(q=q, ext=ext, output_dir=output_dir, instance=instance)
    ebook.run()
