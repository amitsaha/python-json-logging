## Using QueueLogger with Python JSON Logger

When logging from multiple processes (via `multiprocessing` module), 
using [QueueHandler](https://pythonhosted.org/logutils/queue.html#logutils.queue.QueueHandler) is one 
approach with Python 2. `QueueHandler` however sets `exc_info` attribute of a [LogRecord](https://docs.python.org/2/library/logging.html#logging.LogRecord)
to `None` since it is not "pickleable" (more on this later). This becomes a problem
when you use [python-json-logger](https://github.com/madzak/python-json-logger/) 
to format your logs as JSON since it relies on `exc_info` being 
[set](https://github.com/madzak/python-json-logger/blob/master/src/pythonjsonlogger/jsonlogger.py#L125). 
The result is you don't get `exc_info` in your logs. [Sample Code](multi_process_json_logging.py).

### Solution #1: Modify Python JSON logger

The first solution is to look for `exc_text` which is set by the standard 
`Formatter` class as per my [PR](https://github.com/madzak/python-json-logger/pull/38/commits/ac42b205cc275fd0c226843f1dfd226695c09afd) and set that as the value of `exc_info` which means at least we get the string representation of the traceback.

### Solution #2: Subclass QueueHandler

The second solution is it to subclass `logutils.queue.QueueHandler` as follows
and add pickling support for `exc_info` via [tblib](https://github.com/ionelmc/python-tblib):

```python
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
```

Instead of `logutils.queue.QueueHandler`, we will then use `QueueHandlerWithTraceback` instead 
above ([Sample Code](multi_process_json_logging_tblib.py)).

