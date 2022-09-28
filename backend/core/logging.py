log_config = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'console': {
            'fmt': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },
    'handlers': {
        'default': {
            'formatter': 'console',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'backend': {
            'handlers': ['default'],
            'level': 'DEBUG'
        },
    },
}
