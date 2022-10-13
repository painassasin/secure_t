from backend.core import settings


log_config = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'health_check': {
            '()': 'backend.core.logging.filters.HealthCheckFilter'
        },
    },
    'formatters': {
        'default': {
            'format': '%(asctime)s - %(levelname)s - %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'formatter': 'default',
            'class': 'logging.StreamHandler',
            'filters': ['health_check'],
        },
    },
    'loggers': {
        'backend': {
            'handlers': ['console'],
            'level': 'DEBUG' if settings.DEBUG else 'INFO'
        },
        'uvicorn.access': {
            'handlers': ['console'],
            'level': 'INFO'
        }
    },
}
