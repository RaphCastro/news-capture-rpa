from application.news_service import NewsService
from utils.logger import setup_logging


def main():
    setup_logging()
    service = NewsService()
    service.run()


if __name__ == "__main__":
    main()
