LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s %(levelname)-8s %(message)s'
        },
        'detail': {
            'format': '%(asctime)s %(levelname)-8s %(pathname)s[line:%(lineno)d] %(message)s'
        },
        'debug': {
            'format': '\n%(pathname)s, line:%(lineno)d\n>%(levelname)-8s %(message)s\n'
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'debug',
        },
        # 'file': {
        #     'level': 'INFO',
        #     'class': 'logging.handlers.RotatingFileHandler',
        #     'filename': '/var/log/django.log',
        #     'maxBytes': 1024 * 1024 * 5,  # 5 MB
        #     'backupCount': 100,
        #     'formatter': 'detail',
        # },
        # 'app1_file': {
        #     'level': 'INFO',
        #     'class': 'logging.handlers.RotatingFileHandler',
        #     'filename': '/var/log/app1.log',
        #     'maxBytes': 1024 * 1024 * 5,  # 5 MB
        #     'backupCount': 100,
        #     'formatter': 'detail',
        # },
        # 'app2_file': {
        #     'level': 'INFO',
        #     'class': 'logging.handlers.RotatingFileHandler',
        #     'filename': '/var/log/app2.log',
        #     'maxBytes': 1024 * 1024 * 5,  # 5 MB
        #     'backupCount': 100,
        #     'formatter': 'detail',
        # },
    },
    'loggers': {
        # 'django': {
        #     'handlers': ['console', 'file'],
        #     'level': 'INFO',
        #     'propagate': True,
        # },
        'debugger': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        # 自定义模块日志
        # 'users': {
        #     'handlers': ['console', 'file'],
        #     'level': 'DEBUG',
        #     'propagate': True,
        # },
        # 'common': {
        #     'handlers': ['console', 'file'],
        #     'level': 'DEBUG',
        #     'propagate': True,
        # },
        # 'myapp': {
        #     'handlers': ['console', 'file'],
        #     'level': 'DEBUG',
        #     'propagate': True,
        # },
        # 'app1': {
        #     'handlers': ['console', 'app1_file'],
        #     'level': 'INFO',
        #     'propagate': True,
        # },
        # 'pushdata': {
        #     'handlers': ['console', 'app2_file'],
        #     'level': 'INFO',
        #     'propagate': True,
        # },

    },
}
