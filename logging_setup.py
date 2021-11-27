"""
Logging configuration used in example.
"""
from logging.config import dictConfig


def setup_logging() -> None:
    """
    Set up logging, so library emited logs are shown on console.
    """
    dictConfig({
        'version': 1,
        'formatters': {
            'detailed': {
                'class': 'logging.Formatter',
                'format': '%(asctime)s %(name)s %(levelname)s %(message)s',
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'DEBUG',
                'formatter': 'detailed',
            },
        },
        'loggers': {
            'script_args_parser': {
                'handlers': ['console'],
                'propagate': False,
            },
        },
        'root': {
            'level': 'DEBUG',
            'handlers': ['console'],
        },
    })
