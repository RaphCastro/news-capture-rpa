from abc import ABC, abstractmethod
from RPA.Browser.Selenium import Selenium
from domain.article import Article


class BaseAdapter(ABC):
    def __init__(self):
        self.browser = Selenium()

    def start_browser(self):
        self.browser.open_available_browser(self.base_url)

    def maximize_browser(self):
        self.browser.maximize_browser_window()

    def close_browser(self):
        self.browser.close_browser()

    @abstractmethod
    def scrape_news(
        self, search_phrase: str, category: str, months: int
    ) -> list[Article]:
        pass
