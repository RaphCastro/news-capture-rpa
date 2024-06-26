import re
import pandas as pd
from domain.article import Article
from infrastructure.base_adapter import BaseAdapter


def save_to_excel(articles: list[Article], adapter: BaseAdapter):
    """Takes a list of Article Dataclass, transforms it into a Pandas Dataframe and Saves to an excel file
       Args:
        articles (list[Article Dataclass]): list of Article Dataclass processed
        adapter (BaseAdapter Class): Adapter used in the process
    """
    data = [article.__dict__ for article in articles]
    df = pd.DataFrame(data)
    website_name = adapter.__class__.__name__.replace("Adapter", "").lower()
    filename = f"output/{website_name}.xlsx"
    df.to_excel(filename, index=False)


def sanitize_filename(filename):
    return re.sub(r'[\\/*?:"<>|]', "_", filename)
