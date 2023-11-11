import click
from webbrowser import open_new_tab
from .utils import AnnasEbook

@click.group(epilog='Check out our docs at https://github.com/Audiosutras/getdat for more details')
def cli():
    """A command line utility for getting resources available online"""
    pass

@cli.command()
def cinema():
    """Launches movie-web.app in your default browser
    """
    open_new_tab("https://movie-web.app")

@cli.command()
@click.option(
    '-e',
    '--ext',
    type=click.Choice(['epub', 'pdf']),
    default="epub",
    help="Preferred Ebook extension"
)
@click.argument('q', nargs=-1)
def ebook(q, ext):
    """Search for a particular ebook using Anna's Archive"""
    ebook = AnnasEbook(q=q, ext=ext)
    ebook.run()

