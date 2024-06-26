from abc import ABC, abstractmethod


class LocatorAdapter(ABC):
    @property
    @abstractmethod
    def SEARCH_BUTTON(self):
        pass

    @property
    @abstractmethod
    def SEARCH_INPUT(self):
        pass

    @property
    @abstractmethod
    def SORT_BUTTON(self):
        pass

    @property
    @abstractmethod
    def SORT_FILTER(self):
        pass

    @property
    @abstractmethod
    def ARTICLES_LIST(self):
        pass

    @property
    @abstractmethod
    def ARTICLE(self):
        pass

    @property
    @abstractmethod
    def ARTICLE_TITLE(self):
        pass

    @property
    @abstractmethod
    def ARTICLE_DESCRIPTION(self):
        pass

    @property
    @abstractmethod
    def ARTICLE_DATE(self):
        pass

    @property
    @abstractmethod
    def ARTICLE_IMAGE_URL(self):
        pass

    @property
    @abstractmethod
    def DATE_ATTRIBUTE(self):
        pass


class LATimesLocatorAdapter(LocatorAdapter):
    SEARCH_BUTTON = "css:button[data-element='search-button']"
    SEARCH_INPUT = "css:input[data-element='search-form-input']"
    SORT_BUTTON = "css:select[class='select-input']"
    SORT_FILTER = "1"
    ARTICLES_LIST = "css:ul[class='search-results-module-results-menu']"
    ARTICLE = "tag:li"
    ARTICLE_TITLE = "css:a[class='link']"
    ARTICLE_DESCRIPTION = "css:p[class='promo-description']"
    ARTICLE_DATE = "css:p[class='promo-timestamp']"
    ARTICLE_IMAGE_URL = "css:img[class='image']"
    DATE_ATTRIBUTE = "data-timestamp"


class AlJazeeraLocatorAdapter(LocatorAdapter):
    SEARCH_BUTTON = "css:div[class='site-header__search-trigger'] > button"
    SEARCH_INPUT = "css:input[class='search-bar__input']"
    SORT_BUTTON = "css:#search-sort-option"
    SORT_FILTER = "Date"
    ARTICLES_LIST = "css:div[class='search-result__list']"
    ARTICLE = "tag:article"
    ARTICLE_TITLE = "css:a[class='u-clickable-card__link'] > span"
    ARTICLE_DESCRIPTION = "css:div[class='gc__excerpt'] > p"
    ARTICLE_DATE = "css:a[class='u-clickable-card__link']"
    ARTICLE_IMAGE_URL = "css:img[class='article-card__image gc__image']"
    DATE_ATTRIBUTE = "href"
