<div align="center">
    <h1>GetDat</h1>
    <p><i>A command line utility for getting resources available online</i></p>
    <img
        src="/docs/static/getdat-logo.png"
        alt="GetDat Package Logo"
        height="400"
    />
    <p align="center">
        <a href="https://iv.ggtyler.dev/watch?v=4b8P8cqc-UQ">
            GetDat Theme Music
        </a>
    </p>
</div>

## Installation

Once Unit Testing for the `ebook` command is complete this package will be made available on pypi.org. Currently to install run:

```bash
pipx install git+https://github.com/Audiosutras/getdat.git
```

## Commands

#### [Cinema](#cinema)

#### [Ebook](#ebook)

## Cinema
Launches [movie-web.app](https://movie-web.app/search/movie) in your default browser

<div align="center">
    <img
        src="/docs/static/getdat-cinema.gif"
        alt="Gif of GetDat Cinema Command In Action"
    />
</div>

```bash
-> getdat cinema
```

## Ebook
Search and download an ebook available through Anna's Archive

<div align="center">
    <img
        src="/docs/static/getdat-ebook.gif"
        alt="Gif of GetDat Cinema Command In Action"
    />
</div>

```bash
-> getdat ebook <Search>
```
* Tests are a work in progress for this command
* The demo for this command downloaded an epub format of Robert Louis Stevenson's and N.C. Wyeth's book *Treasure Island*. This book is in the public domain.
* The demo opens the downloaded epub  