import logging
import sys

import logging
from logstash_formatter import LogstashFormatterV1

logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = LogstashFormatterV1()

handler.setFormatter(formatter)
logger.addHandler(handler)


#logger.warn('A warning')
# This won't show up in stdout since the default level is WARNING
#logger.info('A Info')

# Now, we setup a hook to handle uncaugh exceptions
# to be logged via the logging module
def handle_exception(exc_type, exc_value, exc_tb):
    logger.error('Uncaugh exception', exc_info=(exc_type, exc_value, exc_tb))
sys.excepthook = handle_exception

# Trigger an exception
def f():
    print 1/0
def g():
    f()
f()
