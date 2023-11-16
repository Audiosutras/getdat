## Local Development

Python Version: `3.11`. To install python on MacOS & Debian-based systems
```bash
-> sudo apt install software-properties-common
-> sudo add-apt-repository ppa:deadsnakes/ppa
-> sudo apt update
-> sudo apt install python3.11
```

This python package uses [poetry](https://python-poetry.org/docs/) for dependency management. To install:
```bash
# install pipx if you have not already
-> python3 -m pip install --user pipx
-> python3 -m pipx ensurepath
# install poetry
-> pipx install poetry
```

Assuming that you have *forked the repository* and have a copy on your local machine. Within the `getdat` directory, install dependencies and open a `virtualenv` shell managed by poetry.
```bash
-> poetry install
-> poetry shell
(getdat-py3.11) ->
```

To run/develop the cli program.
```bash
(getdat-py3.11) -> getdat
Usage: getdat [OPTIONS] COMMAND [ARGS]...

  A command line utility for getting resources available online

Options:
  --help  Show this message and exit.

Commands:
  cinema  Launches movie-web.app in your default browser
  ebook   Search and download an ebook available through Anna's Archive...

  Check out our docs at https://github.com/Audiosutras/getdat/docs for more
  details

```

Project uses [pytest](https://docs.pytest.org/en/7.4.x/) for unit testing. Test run quickly with the help of [pytest-mock](https://pytest-mock.readthedocs.io/en/latest/usage.html)
```bash
(getdat-py3.11) -> pytest -v
```

Style guide and code check enforced with [pre-commit](https://pre-commit.com/)
```
(getdat-py3.11) -> pre-commit install
```

## Additional Sections

### [Home](/READMe.md)
