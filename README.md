# Proxy Scraper

A simple program to scrape proxies from various sites.

## Getting Started

Edit config.json to your liking, then run main.py.

## config.json

* proxySites - Sites currently supported (don't change)
* testSite - Site you'd like to test the proxies on
* totalProxies - Number of proxies you'd like to collect
* output - Name of text file to save working proxies to
* timeout - Number of seconds to wait before aborting a request
* width - Number of characters to center the program output around

## Prerequisites

* Working on Python 2.7.16 or Python 3.6.8
* [requests](http://docs.python-requests.org/en/master/)
* [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
* [eventlet](https://eventlet.net/)

## To-Do

- [ ] Add support for more sites