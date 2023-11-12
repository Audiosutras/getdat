import click
import webbrowser
from .utils import AnnasEbook, print_help

@click.group(epilog='Check out our docs at https://github.com/Audiosutras/getdat for more details')
def cli():
    """A command line utility for getting resources available online"""
    pass

@cli.command()
def cinema():
    """Launches movie-web.app in your default browser
    """
    webbrowser.open_new_tab("https://movie-web.app")

@cli.command()
@click.option(
    '-o',
    '--output_dir',
    help=(
        "Path to ebook's output directory from home directory. "
        "Path must be prefixed by '~' on Unix or '~user' on Windows. "
        "This argument overrides GETDAT_BOOK_DIR env var if set. "
        "Outputs book to working directory if neither are set."
    )
)
@click.option(
    '-e',
    '--ext',
    type=click.Choice(['epub', 'pdf']),
    default="epub",
    help="Preferred Ebook extension"
)
@click.argument('q', nargs=-1)
def ebook(q, ext, output_dir):
    """Search for a particular ebook using Anna's Archive"""
    if not q:
        print_help("Please provide your search to continue.")
    ebook = AnnasEbook(q=q, ext=ext, output_dir=output_dir)
    ebook.run()

