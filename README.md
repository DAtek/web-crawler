[![codecov](https://codecov.io/gh/DAtek/web-crawler/branch/master/graph/badge.svg?token=rrht7DUefF)](https://codecov.io/gh/DAtek/web-crawler)

# Web Crawler

Performant, extensible and lean web crawler, utilizes all available CPUs by default. 

Uses event loop for I/O and processes for analyzing the pages.

## Batteries included
- Basic `httpx` page downloader
- `S3` page storage
- Local filesystem page storage

## Usage
- Have a look at `tests/integration/test_crawl.py`
- Implement your own `PageAnalyzer` and `PageDownloader` classes
- Optionally customize `structlog` logging, see [configuration](https://www.structlog.org/en/stable/configuration.html)
- Have fun!

## Customization
All classes in the modules folder can be replaced with your custom implementation.
