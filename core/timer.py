import time


def elapsed(timer, stamp=None):
    stamp = time.time() if stamp is None else stamp
    return max(0, timer.get('seconds',0) + (stamp-timer['running_since'] if timer.get('running_since') is not None else 0))


def start(timer, stamp=None):
    if timer.get('running_since') is None:
        timer['running_since'] = time.time() if stamp is None else stamp


def pause(timer, stamp=None):
    timer['seconds'] = elapsed(timer, stamp)
    timer['running_since'] = None
