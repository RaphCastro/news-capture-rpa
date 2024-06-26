import yaml
from infrastructure.aljazeera_adapter import AlJazeeraAdapter
from infrastructure.latimes_adapter import LATimesAdapter
from utils.helpers import save_to_excel


class NewsService:
    def __init__(self):
        """
        Initializes the NewsService with adapters for different news websites.

        args:
            adapters: Object that contains the name and adapter to be used for each website

        """
        self.adapters = {
            "latimes": LATimesAdapter(),
            "aljazeera": AlJazeeraAdapter(),
        }

    def load_config(self):
        """
        Loads configuration settings from a YAML file.

        Returns:
            dict: Configuration settings loaded from "src/config.yaml".
        """
        with open("src/config.yaml", "r") as file:
            return yaml.safe_load(file)

    def scrape_news(self, search_phrase, months, websites):
        """
        Scrapes news articles from specified websites using their respective adapters.
        Args:
            search_phrase (str): Phrase to search for in news articles.
            months (int): Number of months within which the articles should be published.
            websites (list): List of website identifiers to scrape news from.
        """

        for site in websites:
            adapter = self.adapters.get(site)
            if adapter:
                adapter.start_browser()
                adapter.maximize_browser()
                try:
                    articles = adapter.scrape_news(search_phrase, months)
                    save_to_excel(articles, adapter)
                finally:
                    adapter.close_browser()

    def run(self):
        """
        Runs the news scraping process using configured settings.

        Reads configuration settings, initializes scraping for configured websites,
        and saves scraped articles to Excel.

        """
        config = self.load_config()
        search_phrase = config["search_phrase"]
        months = config["months"]
        websites = config["websites"]

        self.scrape_news(search_phrase, months, websites)
