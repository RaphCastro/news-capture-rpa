from dataclasses import dataclass


@dataclass
class Article:
    """Base class for Article object"""

    title: str
    date: str
    description: str
    image_filename: str
    count: int
    contains_money: bool
