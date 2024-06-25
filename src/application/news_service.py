import yaml
from infrastructure.aljazeera_adapter import AlJazeeraAdapter
from infrastructure.latimes_adapter import LATimesAdapter
from utils.helpers import save_to_excel


class NewsService:
    def __init__(self):
        self.adapters = {
            "latimes": LATimesAdapter(),
            "aljazeera": AlJazeeraAdapter(),
        }

    def load_config(self):
        with open("src/config.yaml", "r") as file:
            return yaml.safe_load(file)

    def scrape_news(self, search_phrase, category, months, websites):
        for site in websites:
            adapter = self.adapters.get(site)
            if adapter:
                adapter.start_browser()
                adapter.maximize_browser()
                try:
                    articles = adapter.scrape_news(search_phrase, category, months)
                    save_to_excel(articles, adapter)
                finally:
                    adapter.close_browser()

    def run(self):
        config = self.load_config()
        search_phrase = config["search_phrase"]
        category = config["category"]
        months = config["months"]
        websites = config["websites"]

        self.scrape_news(search_phrase, category, months, websites)
