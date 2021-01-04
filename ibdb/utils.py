import logging
import re
import time


def normalize_raw_list(raw):
    return '\n'.join(
        line
        for line in (
            re.sub(r'^(\*\s+|[0-9]+\.\s+)', '', line.strip())
            for line in raw.splitlines()
        )
        if line
    )


def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        if 'log_time' in kw:
            name = kw.get('log_name', method.__name__.upper())
            kw['log_time'][name] = int((te - ts) * 1000)
        else:
            logging.info('Time taken in %s  %2.2f ms' %
                         (method.__name__, (te - ts) * 1000))
        return result
    return timed


class Stats(object):

    def __init__(self, d):
        self.__dict__ = d

    def __repr__(self):
        return 'Stats:\n{0}'.format('\n'.join(' {0}: {1}'.format(stat, val) for stat, val in self.__dict__.items()))
