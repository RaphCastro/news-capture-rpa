from time import sleep
import os
import re
import logging
from PIL import Image
from io import BytesIO
import requests
from infrastructure.base_adapter import BaseAdapter
from domain.article import Article
from datetime import datetime

from utils.helpers import sanitize_filename


class LATimesAdapter(BaseAdapter):
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.latimes.com/"

    def scrape_news(
        self, search_phrase: str, category: str, months: int
    ) -> list[Article]:
        self.browser.wait_until_element_is_visible(
            "css:body > ps-header > header > div.flex.\[\@media_print\]\:hidden > button",
            35,
        )
        self.browser.click_element("css:body > ps-header > header > div.flex.\[\@media_print\]\:hidden > button")
        self.browser.input_text(
            "css:body > ps-header > header > div.flex.\[\@media_print\]\:hidden > div.ct-hidden.fixed.md\:absolute.top-12\.5.right-0.bottom-0.left-0.z-25.bg-header-bg-color.md\:top-15.md\:bottom-auto.md\:h-25.md\:shadow-sm-2 > form > label > input",
            search_phrase,
        )
        self.browser.click_element(
            "css:body > ps-header > header > div.flex.\[\@media_print\]\:hidden > div.ct-hidden.fixed.md\:absolute.top-12\.5.right-0.bottom-0.left-0.z-25.bg-header-bg-color.md\:top-15.md\:bottom-auto.md\:h-25.md\:shadow-sm-2 > form > label > input",
        )
        self.browser.press_keys(
            "css:body > ps-header > header > div.flex.\[\@media_print\]\:hidden > div.ct-hidden.fixed.md\:absolute.top-12\.5.right-0.bottom-0.left-0.z-25.bg-header-bg-color.md\:top-15.md\:bottom-auto.md\:h-25.md\:shadow-sm-2 > form > label > input",
            "ENTER"
        )
        self.browser.wait_until_element_is_visible(
            "css:body > div.page-content > ps-search-results-module > form > div.search-results-module-ajax > ps-search-filters > div > main > ul",
            35,
        )
        self.browser.wait_until_element_is_visible(
            "css:body > div.page-content > ps-search-results-module > form > div.search-results-module-ajax > ps-search-filters > div > main > div.search-results-module-results-header > div.search-results-module-sorts > div > label > select",
            35,
        )
        self.browser.select_from_list_by_value(
            "css:body > div.page-content > ps-search-results-module > form > div.search-results-module-ajax > ps-search-filters > div > main > div.search-results-module-results-header > div.search-results-module-sorts > div > label > select",
            "1",
        )
        sleep(10)
        self.browser.wait_until_element_is_visible(
            "css:body > div.page-content > ps-search-results-module > form > div.search-results-module-ajax > ps-search-filters > div > main > ul",
            35,
        )

        articles = []
        articles_list = self.browser.find_element(
            "css:body > div.page-content > ps-search-results-module > form > div.search-results-module-ajax > ps-search-filters > div > main > ul"
        )
        i = 1
        for article in self.browser.find_elements("tag:li", articles_list):
            title = self.browser.find_element(
                "css:ps-promo > div > div.promo-content > div > h3 > a", article
            ).text
            try:
                date_text = self.browser.find_element(
                    "css:ps-promo > div > div.promo-content > p.promo-timestamp", article
                ).get_attribute("data-timestamp")
            except Exception:
                date_text = None
            description = self.browser.find_element(
                "css:ps-promo > div > div.promo-content > p.promo-description", article
            ).text
            image_url = self.browser.find_element(
                "css:ps-promo > div > div.promo-media > a > picture > img", article
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
                        image_filename=self.download_image(image_url, i),
                        count=count,
                        contains_money=contains_money,
                    )
                )
                i += 1
            logging.info(f"Currently processed: {title} --> {description}")
        return articles

    def parse_date(self, timestamp):
        if timestamp is None:
            return datetime.now().strftime("%Y-%m-%d")

        try:
            parse_timestamp = int(timestamp)
            parsed_date = datetime.fromtimestamp(parse_timestamp / 1000).strftime(
                "%Y-%m-%d"
            )
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

    def download_image(self, image_url: str, iter: int, save_directory="output"):
        if not os.path.exists(save_directory):
            os.makedirs(save_directory)
        response = requests.get(image_url)
        if response.status_code == 200:
            image = Image.open(BytesIO(response.content))
            filename = os.path.basename(f"latimes_article_{iter}")
            filename = sanitize_filename(filename)
            if not filename.lower().endswith(".jpeg"):
                filename = os.path.splitext(filename)[0] + ".jpeg"

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{filename}"

            file_path = os.path.join(save_directory, filename)
            image.convert("RGB").save(file_path, "JPEG")

            return file_path
        else:
            logging.error(
                f"Failed to download image. Status code: {response.status_code}"
            )
            return f"latimes_article_{iter}"
