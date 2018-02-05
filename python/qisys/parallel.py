import collections
import threading
import functools


def foreach(source, action, n_jobs=0):
    """Parallel for

    If n_jobs == 0, there is no limit to the number of jobs, i.e. a thread is
    launched for each item in `source`.

    If n_jobs == 1, this is equivalent to:
    >>> for i in source:
    >>>     action(i)
    """

    if not n_jobs:
        _foreach_no_limit(source, action)
    elif n_jobs == 1:
        for item in source:
            action(item)
    else:
        _foreach_with_limit(source, action, n_jobs)


def _foreach_worker(q, action):
    while True:
        try:
            item = q.popleft()
        except IndexError:
            break

        action(item)


def _foreach_with_limit(source, action, n_jobs):
    assert n_jobs >= 0

    q = collections.deque()
    for item in source:
        q.append(item)

    threads = [threading.Thread(target=functools.partial(_foreach_worker, q, action))
               for _ in range(n_jobs)]

    for t in threads:
        t.start()
    for t in threads:
        t.join()


def _foreach_no_limit(source, action):
    threads = [threading.Thread(target=functools.partial(action, item))
               for item in source]

    for t in threads:
        t.start()
    for t in threads:
        t.join()
