<div align="center">
    <h1>GetDat</h1>
    <p><i>A command line utility for getting resources available online</i></p>
    <img
        src="docs/static/getdat-logo.png"
        alt="GetDat Package Logo"
        height="400"
    />
    <p align="center">
        <a href="https://iv.ggtyler.dev/watch?v=4b8P8cqc-UQ" target="_blank">
            GetDat Theme Music
        </a>
    </p>
</div>

![Tests](https://github.com/Audiosutras/getdat/actions/workflows/tests.yml/badge.svg?branch=master)

## Installation Methods

Install using `pipx`:

```bash
-> python3 -m pip install --user pipx
-> python3 -m pipx ensurepath
-> pipx install git+https://github.com/Audiosutras/getdat.git
```

## Commands

#### [Cinema](#cinema)

#### [Ebook](#ebook)

## Cinema
Launches [movie-web.app](https://movie-web.app/search/movie) in your default browser

<div align="center">
    <img
        src="docs/static/getdat-cinema.gif"
        alt="Gif of GetDat Cinema Command In Action"
    />
</div>

```bash
-> getdat cinema
```

## Ebook
Search and download an ebook available through [Anna's Archive](https://annas-archive.org/). You can think of this command as "headless" Anna's Archive

<div align="center">
    <img
        src="docs/static/getdat-ebook.gif"
        alt="Gif of GetDat Cinema Command In Action"
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

| Name | Convention 1 | Convention 2 | Type | Help |
| ---- | ------------ | ------------ | ----| ----|
| Output Directory | -o | --output_dir | Text | Path to ebook's output directory from home directory. Path must be prefixed by `~` on Unix or `~user` on Windows. This argument overrides `GETDAT_BOOK_DIR` env var if set. Outputs book to working directory if neither are set.
| Extension | -e | --ext | [epub | pdf] | Preferred ebook extension for search results

Example:
```bash
-> getdat ebook Treasure Island Stevenson --ext=epub --output_dir=~/books/epub/
```
or
```bash
-> getdat ebook "Treasure Island Stevensonn" -e epub -o ~/books/epub
```

#### Environment Variable

- `GETDAT_BOOK_DIR` - Path from home directory to destination directory. Ignored if `--output_dir` is specified as an [option](#options)

## Additional Sections

### [Local Development](docs/local_dev.md)
