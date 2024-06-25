from io import BytesIO
from time import sleep
from PIL import Image
import logging
import os
import re
from datetime import datetime
from RPA.Browser.Selenium import WebDriverWait
import requests
from infrastructure.base_adapter import BaseAdapter
from domain.article import Article
from utils.helpers import sanitize_filename


class AlJazeeraAdapter(BaseAdapter):
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.aljazeera.com/"

    def scrape_news(
        self, search_phrase: str, category: str, months: int
    ) -> list[Article]:
        self.browser.wait_until_element_is_visible(
            "css:#root > div > div.container.container--header.container--white.header-is-sticky > div:nth-child(1) > div > header > div.site-header__live-menu--desktop > div.site-header__search-trigger > button",
            35,
        )
        self.browser.click_element(
            "css:#root > div > div.container.container--header.container--white.header-is-sticky > div:nth-child(1) > div > header > div.site-header__live-menu--desktop > div.site-header__search-trigger > button"
        )
        self.browser.input_text(
            "css:#root > div > div.container.container--header.container--white.header-is-sticky > div.site-post-header > div > div > form > div.search-bar__input-container > input",
            search_phrase,
        )
        self.browser.press_keys(
            "css:#root > div > div.container.container--header.container--white.header-is-sticky > div.site-post-header > div > div > form > div.search-bar__input-container > input", "ENTER"
        )
        self.browser.wait_until_element_is_visible(
            "css:#search-sort-option", 35
        )
        self.browser.select_from_list_by_value(
            "css:#search-sort-option", "date"
        )
        sleep(10)
        self.browser.wait_until_element_is_visible(
            "css:#main-content-area > div.l-col.l-col--8 > div.search-result__list > article:nth-child(1)", 35
        )

        articles = []
        articles_div = self.browser.find_element(
            "css:#main-content-area > div.l-col.l-col--8 > div.search-result__list"
        )
        i = 1
        for article in self.browser.find_elements("tag:article", articles_div):
            title = self.browser.find_element(
                "css:div.gc__content > div.gc__header-wrap > h3 > a > span", article
            ).text
            date_text = str(
                self.browser.find_element(
                    "css:div.gc__content > div.gc__header-wrap > h3 > a", article
                ).get_attribute("href")
            )
            description = self.browser.find_element(
                "css:div.gc__content > div.gc__body-wrap > div > p", article
            ).text
            image_url = self.browser.find_element(
                "css:div.gc__image-wrap > div > div > img", article
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

    def parse_date(self, date_text):
        splited = date_text.split("/")
        if len(splited) >= 7:
            parsed_date = f"{splited[4]}-{splited[5]}-{splited[6]}"
        else:
            parsed_date = datetime.strftime(datetime.now(), "%Y-%m-%d")
        return parsed_date

    def is_within_months(self, date, months):
        try:
            article_date = datetime.strptime(date, "%Y-%m-%d")
            return (datetime.now() - article_date).days <= months * 30
        except Exception as e:
            return (datetime.now() - datetime.now()).days <= months * 30

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
            filename = os.path.basename(f"aljazeera_article_{iter}")
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
