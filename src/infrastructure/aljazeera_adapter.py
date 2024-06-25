from io import BytesIO
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
        self.browser.wait_until_element_is_visible("xpath://*[@id='root']/div/div[1]/div[1]/div/header/div[4]/div[2]/button", 35)
        self.browser.click_element("xpath://*[@id='root']/div/div[1]/div[1]/div/header/div[4]/div[2]/button")
        self.browser.input_text("xpath://*[@id='root']/div/div[1]/div[2]/div/div/form/div[1]/input", search_phrase)
        self.browser.press_keys("xpath://*[@id='root']/div/div[1]/div[2]/div/div/form/div[1]/input", "ENTER")
        self.browser.wait_until_element_is_visible("xpath://*[@id='search-sort-option']", 35)
        self.browser.select_from_list_by_value("xpath://*[@id='search-sort-option']", "date")
        self.browser.wait_until_element_is_visible("xpath://*[@id='main-content-area']/div[2]/div[2]/article[1]", 35)

        articles = []
        articles_div = self.browser.find_element("xpath://*[@id='main-content-area']/div[2]/div[2]")
        for article in self.browser.find_elements("tag:article", articles_div):
            title = self.browser.find_element("xpath:div[2]/div[1]/h3/a/span", article).text
            date_text = str(self.browser.find_element("xpath:div[2]/div[1]/h3/a", article).get_attribute("href"))
            description = self.browser.find_element("xpath:div[2]/div[2]/div/p", article).text
            image_url = self.browser.find_element("xpath:div[3]/div/div/img", article).get_attribute("src")
            date = self.parse_date(date_text)
            if self.is_within_months(date, months):
                count = self.count_phrases(search_phrase, title, description)
                contains_money = self.contains_money(title, description)
                articles.append(
                    Article(
                        title=title,
                        date=date,
                        description=description,
                        image_filename=self.download_image(image_url),
                        count=count,
                        contains_money=contains_money,
                    )
                )
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

    def download_image(self, image_url, save_directory="output"):
        if not os.path.exists(save_directory):
            os.makedirs(save_directory)
        response = requests.get(image_url)
        if response.status_code == 200:
            image = Image.open(BytesIO(response.content))
            filename = os.path.basename(image_url)
            filename = sanitize_filename(filename)
            if not filename.lower().endswith(".jpeg"):
                filename = os.path.splitext(filename)[0] + ".jpeg"
            file_path = os.path.join(save_directory, filename)
            image.convert("RGB").save(file_path, "JPEG")

            return file_path
        else:
            logging.error(
                f"Failed to download image. Status code: {response.status_code}"
            )
            return image_url
