import pandas as pd
from domain.article import Article


def save_to_excel(articles: list[Article], adapter):
    data = [article.__dict__ for article in articles]
    df = pd.DataFrame(data)
    website_name = adapter.__class__.__name__.replace("Adapter", "").lower()
    filename = f"output/{website_name}.xlsx"
    df.to_excel(filename, index=False)
