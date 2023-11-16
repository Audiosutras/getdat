import click
import webbrowser
from .utils import AnnasEbook, print_help
from .constants import EBOOK_ERROR_MSG, MOVIE_WEB


@click.group(
    epilog="Check out our docs at https://audiosutras.github.io/getdat/ for more details"
)
def cli():
    """A command line utility for getting resources available online"""
    pass


@cli.command()
def cinema():
    """Launches movie-web.app in your default browser"""
    webbrowser.open_new_tab(MOVIE_WEB)


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
    help="Preferred ebook extension for search results",
)
@click.argument("q", nargs=-1)
def ebook(q, ext, output_dir):
    """Search and download an ebook available through Anna's Archive

    ex: getdat ebook <Search>
    """
    if not q:
        print_help(EBOOK_ERROR_MSG)
    ebook = AnnasEbook(q=q, ext=ext, output_dir=output_dir)
    ebook.run()
