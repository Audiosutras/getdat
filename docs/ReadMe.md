<div align="center">
    <h1>GetDat</h1>
    <p><i>A command line utility for getting resources available online</i></p>
    <img
        src="{{ 'assets/images/getdat-logo.png' }}"
        alt="GetDat Package Logo"
        height="400"
    />
    <p align="center">
        <a href="https://iv.ggtyler.dev/watch?v=4b8P8cqc-UQ" target="_blank">
            GetDat Theme Music
        </a>
    </p>
</div>

<div class="flex flex-row justify-between flex-wrap">
  <a href="https://pypi.org/project/getdat/" alt="Link to PyPi package homepage">
    <img class="p-2" alt="PyPI - Downloads" src="https://img.shields.io/pypi/dm/getdat?logo=pypi">
  </a>
  <a href="https://github.com/Audiosutras/getdat/actions/workflows/ci.yml?query=branch%3Amaster" alt="Link to CI jobs for master branch">
    <img class="p-2" alt="CI" src="https://github.com/Audiosutras/getdat/actions/workflows/ci.yml/badge.svg?branch=master">
  </a>
  <a href="https://github.com/Audiosutras/getdat" alt="Link to Github Issues">
    <img alt="GitHub issues" src="https://img.shields.io/github/issues/Audiosutras/getdat">
  </a>
</div>

Table of Contents

- [Installation Methods](#installation-methods)
- [Commands](#commands)
- [Local Development](#local-development)
- [Deployment - Publishing GetDat](#deployment---publishing-getdat)
- [Contributors](#contributors)

## Installation Methods

PYPI - Stable Release:
```bash
-> pipx install getdat
```

From Head commit of Repository:
```bash
-> pipx install git+https://github.com/Audiosutras/getdat.git
```

## Commands

### Cinema
Launches [movie-web.app](https://movie-web.app/search/movie) in your default browser

<div align="center" class="gif-image">
    <img
        src="{{ 'assets/images/getdat-cinema.gif' | relative_url }}"
        alt="Gif of GetDat Cinema Command In Action"
    />
</div>

```bash
-> getdat cinema
```

### Ebook
Search and download an ebook available through [Anna's Archive](https://annas-archive.org/). You can think of this command as "headless" Anna's Archive

<div align="center" class="gif-image">
    <img
        src="{{ 'assets/images/getdat-ebook.gif' | relative_url }}"
        alt="Gif of GetDat Ebook Command In Action"
        style="border: red"
    />
</div>

* The demo for this command downloaded an epub format of Robert Louis Stevenson's and N.C. Wyeth's book *Treasure Island*. This book is in the public domain.
* The demo for this command opens the downloaded ebook using [epr](https://github.com/wustho/epr), a terminal epub reader to show the contents of the downloaded book. You can expect higher ebook quality by using a desktop e-reader like [librum](https://librumreader.com/)
* Anna's Archive `SciDB` search is not yet supported.


```bash
-> getdat ebook [OPTIONS] [Q]
```

#### ARGUMENTS

| Name | Help |
|------|------|
| Q    | Search |

Example:
```bash
-> getdat ebook "Treasure Island Stevenson"
```
or
```bash
-> getdat ebook Treasure Island Stevenson
```

#### OPTIONS

```bash
-> getdat ebook --help
Usage: getdat ebook [OPTIONS] [Q]...

  Search and download an ebook available through Anna's Archive

  ex: getdat ebook <Search>

Options:
  -o, --output_dir TEXT       Path to ebook's output directory from home
                              directory. Path must be prefixed by '~' on Unix
                              or '~user' on Windows. This argument overrides
                              GETDAT_BOOK_DIR env var if set. Outputs book to
                              working directory if neither are set.
  -e, --ext [epub|pdf]        Preferred ebook extension for search results -
                              Default: epub
  -i, --instance [org|gs|se]  The instance of Anna's Archive you would like to
                              use for your search:  https://annas-archive.org,
                              https://annas-archive.gs, https://annas-
                              archive.se - Default: org
  --help                      Show this message and exit.

```

Example:
```bash
-> getdat ebook Treasure Island Stevenson --ext=epub --output_dir=~/books/epub/ --instance=gs
```
or
```bash
-> getdat ebook "Treasure Island Stevenson" -e epub -o ~/books/epub -i gs
```
or
```bash
-> getdat ebook "Treasure Island Stevenson"
```

#### Environment Variable

- `GETDAT_BOOK_DIR` - Path from home directory to destination directory. Ignored if `--output_dir` is specified as an [option](#options)

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
```bash
(getdat-py3.11) -> pre-commit install
```

Running `docs` site locally for making changes to `github-pages` requires [ruby](https://www.ruby-lang.org/en/) to be installed
```bash
-> cd docs
-> bundler install
-> bundler exec jekyll build
-> bundler exec jekyll serve
```

## Deployment - Publishing Getdat

Workflow: `master` branch

- In `pyproject.toml` *bump* the version number `*.*.*`

- Create a [git tag](https://git-scm.com/book/en/v2/Git-Basics-Tagging) with the new version number `*.*.*` you specified in `pyproject.toml`.

- Push the newly created tag `git push origin *.*.*` to the repository. This will trigger the `pre-release.yml` github workflow to publish our package to `test.pypi`. The pre-release can be seen [here](https://test.pypi.org/project/getdat/) for testing. Install with:
```bash
-> python3.11 -m pip install --index-url https://test.pypi.org/simple/ getdat --extra-index-url https://pypi.org/simple beautifulsoup4 requests click
```
    - *Note*: `--extra-index-url` option is pulling dependencies from `pypi.org` and not `test.pypi.org` though our package is coming in from `test.pypi.org`. Make sure to add all dependencies from `[tool.poetry.dependencies]` in `pyproject.toml` (except python) before running this command.

- *Create* a [release](https://www.toolsqa.com/git/github-releases/) on github. Make sure to select `Tags` from the toggle menu. Select the latest tag (highest version number). Name the release `Release *.*.*`. Make sure the version number in `pyproject.toml` syncs up with the release version. *Click* `Publish release`. This will kick off our `release.yml` workflow to publish our package to `pypi`. The release can be seen [here and installed](https://pypi.org/project/getdat/) for production use. Install with:
```bash
-> pipx install getdat
```

---
## Contributors

![GitHub Contributors Image](https://contrib.rocks/image?repo=Audiosutras/getdat)
