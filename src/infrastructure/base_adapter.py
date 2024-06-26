from abc import ABC, abstractmethod
from datetime import datetime
from typing import List
from domain.article import Article
from domain.locator import LocatorAdapter
from RPA.Browser.Selenium import Selenium


class BaseAdapter(ABC):
    """
    Base class for web scraping adapters.

    Attributes:
        browser (Selenium): Instance of Selenium browser for interacting with web pages.
        locator (LocatorAdapter): Adapter providing element locators for the specific website.
        base_url (str): Base URL for the specific website.
    """

    def __init__(self, locator: LocatorAdapter, base_url: str):
        """
        Initializes the BaseAdapter with a specific LocatorAdapter.

        Args:
            locator (LocatorAdapter): Adapter providing element locators for the specific website.
            base_url (str): Base URL of the website to scrape.
        """
        self.browser = Selenium()
        self.locator = locator
        self.base_url = base_url

    def start_browser(self) -> None:
        """
        Opens a new browser window and navigates to the base URL.
        """
        self.browser.open_available_browser(self.base_url)

    def maximize_browser(self) -> None:
        """
        Maximizes the current browser window.
        """
        self.browser.maximize_browser_window()

    def close_browser(self) -> None:
        """
        Closes the current browser window.
        """
        self.browser.close_browser()

    @abstractmethod
    def scrape_news(self, search_phrase: str, months: int) -> List[Article]:
        """
        Abstract method to be implemented by subclasses for scraping news articles.

        Args:
            search_phrase (str): Phrase to search for in news articles.
            months (int): Number of months within which the articles should be published (filter).

        Returns:
            List[Article]: List of Article objects scraped from the website.
        """
        pass

    @abstractmethod
    def parse_date(self, date_text: str) -> str:
        """
        Abstract method to parse date information from the provided text.

        Args:
            date_text (str): Text containing date information.

        Returns:
            str: Parsed string of date_text after treatment.
        """
        pass

    @abstractmethod
    def is_within_months(self, date: datetime, months: int) -> bool:
        """
        Abstract method to check if a given date is within the specified number of months.

        Args:
            date (datetime.datetime): Date to check.
            months (int): Number of months within which the date should be considered valid.

        Returns:
            bool: True if the date is within the specified months, False otherwise.
        """
        pass

    @abstractmethod
    def count_phrases(self, search_phrase: str, title: str, description: str) -> int:
        """
        Abstract method to count occurrences of a search phrase in article title and description.

        Args:
            search_phrase (str): Phrase to search for.
            title (str): Title of the article.
            description (str): Description or content of the article.

        Returns:
            int: Number of occurrences of the search phrase.
        """
        pass

    @abstractmethod
    def contains_money(self, title: str, description: str) -> bool:
        """
        Abstract method to check if an article title or description mentions money.

        Args:
            title (str): Title of the article.
            description (str): Description or content of the article.

        Returns:
            bool: True if the article mentions money, False otherwise.
        """
        pass

    @abstractmethod
    def download_image(self, image_url: str, iter: int, save_directory: str = "output") -> str:
        """
        Abstract method to download an image from the provided URL.

        Args:
            image_url (str): URL of the image to download.
            iter (int): Iterable auto-increment int for naming of image.
            save_directory (str / file_path): folder_path to store the images

        Returns:
            str: Filepath of the downloaded image.
        """
        pass
