"""Utility functions for testing a multi page app with an index page"""
from typing import List

from playwright.sync_api import sync_playwright


def get_urls(index_url) -> List[str]:
    """Returns a list of the urls scraped from the index page"""
    with sync_playwright() as play:
        browser = play.chromium.launch()
        page = browser.new_page()
        page.goto(index_url)
        urls = []
        for link in page.locator(".card-link").all():
            url = link.get_attribute("href").replace("./", index_url)
            urls.append(url)
        browser.close()
        return urls
