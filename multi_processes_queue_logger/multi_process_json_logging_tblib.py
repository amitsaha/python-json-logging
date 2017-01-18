import logging
import logging.config
import logutils.queue
from pythonjsonlogger import jsonlogger
import multiprocessing
from multiprocessing import Process
import os
import sys
import time

# Bring in support for serializing/deserializing tracebacks
# needed by QueueHandler
from tblib import pickling_support
pickling_support.install()


class QueueHandlerWithTraceback(logutils.queue.QueueHandler):
    """ QueueHandler with support for pickling/unpickling
        Tracebacks via tblib. We only override the prepare()
        method to *not* set `exc_info=None`
    """
    def __init__(self, *args, **kwargs):
        logutils.queue.QueueHandler.__init__(self, *args, **kwargs)

    def prepare(self, record):
        self.format(record)
        record.msg = record.message
        record.args = None
        return record

def setup_logging():
    logging.config.fileConfig('logging.conf')
    logger = logging.getLogger('test_logging')
    root_logger = logging.getLogger()
    # Save our registered handlers
    registered_handlers = [h for h in root_logger.handlers]
    # Remove all the root handlers
    for h in registered_handlers:
        root_logger.removeHandler(h)
    # Re-route all the handlers to a QueueListener
    logqueue = multiprocessing.Queue()
    root_logger.addHandler(QueueHandlerWithTraceback(logqueue))
    ql = logutils.queue.QueueListener(logqueue, *registered_handlers)
    ql.start()

    return logger, ql


def raise_exception():
    1/0

def a_fun_which_logs(logger):
    try:
        raise_exception()
    except Exception as e:
        logger.error(str(e), exc_info=True)
    logger.info('I am in process %s' % os.getpid())

if __name__ == '__main__':
    logger, ql = setup_logging()
    p = Process(target=a_fun_which_logs, args=(logger,))
    p.start()
    p.join()
    ql.stop()
