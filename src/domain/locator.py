from abc import ABC
from dataclasses import dataclass


@dataclass
class LocatorAdapter(ABC):
    """
    Adapter class for locators.

    This base class defines the interface for locator adapters, which provide specific CSS or XPath selectors for elements on different websites.

    Attributes:
        ELEMENT (str) : Locator for the specific Element
    """
    SEARCH_BUTTON: str = ""
    SEARCH_INPUT: str = ""
    SORT_BUTTON: str = ""
    SORT_FILTER: str = ""
    ARTICLES_LIST: str = ""
    ARTICLE: str = ""
    ARTICLE_TITLE: str = ""
    ARTICLE_DESCRIPTION: str = ""
    ARTICLE_DATE: str = ""
    ARTICLE_IMAGE_URL: str = ""
    DATE_ATTRIBUTE: str = ""


class LATimesLocatorAdapter(LocatorAdapter):
    SEARCH_BUTTON: str = "css:button[data-element='search-button']"
    SEARCH_INPUT: str = "css:input[data-element='search-form-input']"
    SORT_BUTTON: str = "css:select[class='select-input']"
    SORT_FILTER: str = "1"
    ARTICLES_LIST: str = "css:ul[class='search-results-module-results-menu']"
    ARTICLE: str = "tag:li"
    ARTICLE_TITLE: str = "css:a[class='link']"
    ARTICLE_DESCRIPTION: str = "css:p[class='promo-description']"
    ARTICLE_DATE: str = "css:p[class='promo-timestamp']"
    ARTICLE_IMAGE_URL: str = "css:img[class='image']"
    DATE_ATTRIBUTE: str = "data-timestamp"


class AlJazeeraLocatorAdapter(LocatorAdapter):
    SEARCH_BUTTON: str = "css:div[class='site-header__search-trigger'] > button"
    SEARCH_INPUT: str = "css:input[class='search-bar__input']"
    SORT_BUTTON: str = "css:#search-sort-option"
    SORT_FILTER: str = "date"
    ARTICLES_LIST: str = "css:div[class='search-result__list']"
    ARTICLE: str = "tag:article"
    ARTICLE_TITLE: str = "css:h3[class='gc__title'] > a > span"
    ARTICLE_DESCRIPTION: str = "css:div[class='gc__excerpt'] > p"
    ARTICLE_DATE: str = "css:a[class='u-clickable-card__link']"
    ARTICLE_IMAGE_URL: str = "css:img[class='article-card__image gc__image']"
    DATE_ATTRIBUTE: str = "href"
