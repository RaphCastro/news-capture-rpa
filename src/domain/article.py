from dataclasses import dataclass

@dataclass
class Article:
    title: str
    date: str
    description: str
    image_filename: str
    count: int
    contains_money: bool
