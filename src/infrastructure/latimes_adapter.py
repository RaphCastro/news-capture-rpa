from time import sleep
import os
import re
import logging
from PIL import Image
from io import BytesIO
import requests
from domain.locator import LATimesLocatorAdapter
from infrastructure.base_adapter import BaseAdapter
from domain.article import Article
from datetime import datetime

from utils.helpers import sanitize_filename


class LATimesAdapter(BaseAdapter):
    def __init__(self):
        super().__init__(
            locator=LATimesLocatorAdapter, base_url="https://www.latimes.com/"
        )

    def scrape_news(self, search_phrase: str, months: int) -> list[Article]:

        self.browser.wait_until_element_is_visible(self.locator.SEARCH_BUTTON, 35)
        self.browser.click_element(self.locator.SEARCH_BUTTON)

        self.browser.input_text(self.locator.SEARCH_INPUT, search_phrase)
        self.browser.click_element(self.locator.SEARCH_INPUT)
        self.browser.press_keys(self.locator.SEARCH_INPUT, "ENTER")

        self.browser.wait_until_element_is_visible(self.locator.SORT_BUTTON, 35)
        self.browser.wait_until_element_is_visible(self.locator.SORT_BUTTON, 35)
        self.browser.select_from_list_by_value(
            self.locator.SORT_BUTTON, self.locator.SORT_FILTER
        )

        sleep(10)
        self.browser.wait_until_element_is_visible(self.locator.ARTICLES_LIST, 35)

        articles = []
        articles_list = self.browser.find_element(self.locator.ARTICLES_LIST)
        i = 1

        for article in self.browser.find_elements(self.locator.ARTICLE, articles_list):
            title = self.browser.find_element(self.locator.ARTICLE_TITLE, article).text

            try:
                date_text = self.browser.find_element(
                    self.locator.ARTICLE_DATE, article
                ).get_attribute(self.locator.DATE_ATTRIBUTE)
            except Exception:
                date_text = None

            description = self.browser.find_element(
                self.locator.ARTICLE_DESCRIPTION, article
            ).text

            image_url = self.browser.find_element(
                self.locator.ARTICLE_IMAGE_URL, article
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

    def parse_date(self, date_text: str) -> str:
        try:
            splited = date_text.split("/")
            parsed_date = datetime.strptime(
                f"{splited[4]}-{splited[5]}-{splited[6]}", "%Y-%m-%d"
            )
            return parsed_date
        except Exception:
            parsed_date = datetime.strftime(datetime.now(), "%Y-%m-%d")
            return parsed_date

    def is_within_months(self, date: datetime, months: int) -> bool:
        try:
            article_date = datetime.strptime(date, "%Y-%m-%d")
            return (datetime.now() - article_date).days <= months * 30
        except Exception:
            return (datetime.now() - datetime.now()).days <= months * 30

    def count_phrases(self, search_phrase: str, title: str, description: str) -> int:
        count = sum(
            1
            for _ in re.finditer(
                r"\b%s\b" % re.escape(search_phrase), title + description, re.IGNORECASE
            )
        )
        return count

    def contains_money(self, title: str, description: str) -> bool:
        pattern = r"\$\d+(?:,\d{3})*(?:\.\d{2})?|\d+ dollars|\d+ USD"
        return bool(re.search(pattern, title + description, re.IGNORECASE))

    def download_image(
        self, image_url: str, iter: int, save_directory: str = "output"
    ) -> str:

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
            return f"aljazeera_article_{iter}"
