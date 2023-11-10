import click
from .utils import AnnasEbook

@click.group()
def cli():
    """A command line utility for getting resources available online"""
    pass


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

