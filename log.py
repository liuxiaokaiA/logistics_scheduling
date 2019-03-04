# coding: utf-8
"""
    The name of the log file changes automatically based on time.
    LOGGING_CONFIG: the config file about the logging.
    <logging.config.dictConfig>: such like next,
    logger --> handler --> formatter --> output
    # Create logger
    logger = logging.getLogger('user')
    logger.setLevel('DEBUG')
    # Create handler and set leverl
    handler = logging.StreamHandler()
    handler.setLevel('DEBUG')
    # Create formatter
    handler.setFormatter('%(levelname)s: %(message)s')
    # Add to logger
    logger.addHandler(handler)
    日志级别大小关系为：CRITICAL > ERROR > WARNING > INFO > DEBUG > NOTSET
"""


from logging.handlers import BaseRotatingHandler
import os, time, codecs, logging, logging.config


class SingleLevel(logging.Filter):
    def __init__(self, level):
        if isinstance(level, int):
            self.allow = level
        elif isinstance(level, basestring):
            self.allow = getattr(logging, level)
        else:
            raise ValueError('Invalid `level` type.')

    def filter(self, record):
        if record.levelno == self.allow:
            return True
        else:
            return False


BASE_DIR = os.path.dirname((os.path.abspath(__file__)))
print (BASE_DIR)
LOGGING = {
    'disable_existing_loggers': False,
    'version': 1,
    'formatters': {
        'verbose': {
            'format': '[%(levelname)s] %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'default': {
            'format': '[%(levelname)s] %(asctime)s %(module)s %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
        'poor': {
            'format': '%(message)s'
        }
    },
    'filters': {
        'debug_only': {
            '()': SingleLevel,
            'level': 'DEBUG',
        },
        'info_only': {
            '()': SingleLevel,
            'level': 'INFO',
        },
        'warn_only': {
            '()': SingleLevel,
            'level': 'WARN',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
        },
        'debug': {
            'level': 'DEBUG',
            'class': 'log.MultiProcessSafeDailyRotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'log/debug.log'),
            'when': 'midnight',
            'formatter': 'default',
            'filters': ['debug_only'],
        },
        'error': {
            'level': 'ERROR',
            'class': 'log.MultiProcessSafeDailyRotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'log/error.log'),
            'when': 'midnight',
            'formatter': 'default',
        },
        'info': {
            'level': 'INFO',
            'class': 'log.MultiProcessSafeDailyRotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'log/info.log'),
            'when': 'midnight',
            'formatter': 'default',
            'filters': ['info_only'],
        },
        'warn': {
            'level': 'WARN',
            'class': 'log.MultiProcessSafeDailyRotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'log/warn.log'),
            'when': 'midnight',
            'formatter': 'default',
            'filters': ['warn_only'],
        },
    },
    'loggers': {
        'default': {
            'handlers': ['error', 'info', 'warn', 'debug'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'debug': {
            'handlers': ['console', 'error', 'info', 'warn', 'debug'],
            'level': 'INFO',
            'propagate': False,
        },
        'debug.print': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
LOGGING_simple = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '[%(levelname)s] %(asctime)s %(module)s %('
                      'process)d %(thread)d: %(message)s',
            'datefmt': '%H:%M:%S'
        },
        'simple': {
            'format': '[%(levelname)s]: %(message)s'
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'default': {
            'level': 'DEBUG',
            'class': 'log.MultiProcessSafeDailyRotatingFileHandler',
            'formatter': 'standard',
            'filename': './log/info.log'
        }
    },
    'loggers': {
        'user': {
            'level': 'DEBUG',
            # console用于stdout输出，如果没有则不会再屏幕中显示
            'handlers': ['console', 'default']
        }
    }
}


class MyLogging(object):
    def __init__(self):
        # 1.The configuration below has no file to output.
        self.LOGGING_CONFIG = LOGGING
        # 2. To get the absolute path of the log file.
        # Log file is stored under the 'log' folder. If it not existed,
        # create it auto.
        dir_path = os.path.join(os.path.dirname(__file__), 'log')
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        # 3. Loading the config, and make it effect.
        # This command can not be executed after the logging.getLogger function
        # because there is no specific logger name.
        logging.config.dictConfig(self.LOGGING_CONFIG)
        # self.logger = logging.getLogger(logger_name)  # return a logger


class MultiProcessSafeDailyRotatingFileHandler(BaseRotatingHandler):
    """
    Similar with `logging.TimedRotatingFileHandler`, while this one is
    - Multi process safe
    - Rotate at midnight only
    - Utc not supported
    - This log will create day by day.
    """
    def __init__(self, filename, encoding=None, delay=False, utc=False, **kwargs):
        self.utc = utc
        self.suffix = "%Y%m%d"
        self.baseFilename = os.path.abspath(filename)
        self.currentFileName = self._compute_fn()
        BaseRotatingHandler.__init__(self, filename, 'a', encoding, delay)

    def shouldRollover(self, record):
        if self.currentFileName != self._compute_fn():
            return True
        return False

    def doRollover(self):
        if self.stream:
            self.stream.close()
            self.stream = None
        self.currentFileName = self._compute_fn()

    def _compute_fn(self):
        return self.baseFilename + "." + time.strftime(self.suffix, time.localtime())

    def _open(self):
        if self.encoding is None:
            stream = open(self.currentFileName, self.mode)
        else:
            stream = codecs.open(self.currentFileName, self.mode, self.encoding)
        # simulate file name structure of `logging.TimedRotatingFileHandler`
        if os.path.exists(self.baseFilename):
            try:
                os.remove(self.baseFilename)
            except OSError:
                pass
        try:
            # Create the symlink point the lastest log file.
            os.symlink(self.currentFileName, self.baseFilename)
        except OSError:
            pass
        return stream


if __name__ == '__main__':
    # mylogging = MyLogging(logger_name='user')  # This is a customized class;
    MyLogging()
    mylogging = logging.getLogger('default')
    while 1:
        mylogging.debug('%s' % time.time())
        mylogging.info('%s' % time.time())
        mylogging.error('%s' % time.time())
        mylogging.warn('%s' % time.time())
        time.sleep(5)
