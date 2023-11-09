import click
from .utils import Ebook

@click.group()
def cli():
    """A command line utility for getting resources available online"""
    pass


@cli.command()
@click.option(
    '-b',
    '--browser',
    is_flag=True,
    help="Continue search in your default browser"
)
@click.option(
    '-e',
    '--ext',
    type=click.Choice(['epub', 'pdf']),
    default="epub",
    help="Preferred Ebook extension"
)
@click.option(
    '-s',
    '--source',
    type=click.Choice(['annas_archive']),
    default="annas_archive",
    help="Website you would like to use for your search",
)
@click.argument('q', nargs=-1)
def ebook(q, source, ext, browser):
    """Search for a particular ebook."""
    ebook = Ebook(q=q, source=source, ext=ext, browser=browser)
    ebook.run()

