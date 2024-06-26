import logging
import logging.config
import os


def setup_logging(log_directory="output"):
    """
    Creates the logging configuration for code usage
    Args:
        log_directory (str / folder_path): folder path to store the logs
    """
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

    log_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            },
        },
        'handlers': {
            'console': {
                'level': 'INFO',
                'class': 'logging.StreamHandler',
                'formatter': 'standard'
            },
            'file': {
                'level': 'INFO',
                'class': 'logging.FileHandler',
                'filename': os.path.join(log_directory, 'application.log'),
                'formatter': 'standard'
            },
        },
        'loggers': {
            '': {
                'handlers': ['console', 'file'],
                'level': 'INFO',
                'propagate': True
            },
        }
    }

    logging.config.dictConfig(log_config)
