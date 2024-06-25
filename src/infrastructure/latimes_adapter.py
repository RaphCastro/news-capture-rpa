import re
import logging
from infrastructure.base_adapter import BaseAdapter
from domain.article import Article
from datetime import datetime


class LATimesAdapter(BaseAdapter):
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.latimes.com/"

    def scrape_news(
        self, search_phrase: str, category: str, months: int
    ) -> list[Article]:
        self.browser.wait_until_element_is_visible(
            "xpath:html/body/ps-header/header/div[2]/button",
            35,
        )
        self.browser.click_element(
            "xpath:html/body/ps-header/header/div[2]/button"
        )
        self.browser.input_text(
            "xpath:html/body/ps-header/header/div[2]/div[2]/form/label/input", search_phrase
        )
        self.browser.press_keys(
            "xpath:html/body/ps-header/header/div[2]/div[2]/form/label/input", "ENTER"
        )
        self.browser.wait_until_element_is_visible(
            "xpath:html/body/div[2]/ps-search-results-module/form/div[2]/ps-search-filters/div/main/ul", 35
        )

        articles = []
        articles_list = self.browser.find_element(
            "xpath:html/body/div[2]/ps-search-results-module/form/div[2]/ps-search-filters/div/main/ul"
        )
        for article in self.browser.find_elements("tag:li", articles_list):
            title = self.browser.find_element(
                "xpath:ps-promo/div/div[2]/div/h3/a", article
            ).text
            try:
                date_text = self.browser.find_element(
                    "xpath:ps-promo/div/div[2]/p[2]", article
                ).get_attribute("data-timestamp")
            except Exception:
                date_text = None
            description = self.browser.find_element(
                "xpath:ps-promo/div/div[2]/p[1]", article
            ).text
            image_url = self.browser.find_element(
                "xpath:ps-promo/div/div[1]/a/picture/img", article
            ).get_attribute("src")
            date = self.parse_date(date_text)
            if self.is_within_months(date, months):
                count = self.count_phrases(search_phrase, title, description)
                contains_money = self.contains_money(title, description)
                articles.append(
                    Article(
                        title=title,
                        date=date,
                        description=description,
                        image_filename=image_url,
                        count=count,
                        contains_money=contains_money,
                    )
                )
            logging.info(f"Currently processed: {title} --> {description}")
        return articles

    def parse_date(self, timestamp):
        if timestamp is None:
            return datetime.now().strftime("%Y-%m-%d")

        try:
            parse_timestamp = int(timestamp)
            parsed_date = datetime.fromtimestamp(parse_timestamp / 1000).strftime("%Y-%m-%d")
        except Exception as e:
            logging.warning(f"An error occurred while parsing the timestamp: {e}")
            parsed_date = datetime.now().strftime("%Y-%m-%d")
        return parsed_date

    def is_within_months(self, date, months):
        try:
            article_date = datetime.strptime(date, "%Y-%m-%d")
            return (datetime.now() - article_date).days <= months * 30
        except Exception as e:
            logging.warning(f"An error occurred while checking the date: {e}")
            return False

    def count_phrases(self, phrase, title, description):
        count = sum(
            1
            for _ in re.finditer(
                r"\b%s\b" % re.escape(phrase), title + description, re.IGNORECASE
            )
        )
        return count

    def contains_money(self, title, description):
        pattern = r"\$\d+(?:,\d{3})*(?:\.\d{2})?|\d+ dollars|\d+ USD"
        return bool(re.search(pattern, title + description, re.IGNORECASE))
