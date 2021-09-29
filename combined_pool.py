# tested in python 3.7, 3.8, 3.9

import os
from concurrent.futures import _base
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from concurrent.futures.process import (
    _ExceptionWithTraceback, _sendback_result
)


class Task(object):
    def __init__(self, call_item, result_queue):
        self.call_item = call_item
        self.result_queue = result_queue

    def __call__(self):
        try:
            r = self.call_item.fn(
                *self.call_item.args, **self.call_item.kwargs)
        except BaseException as e:
            exc = _ExceptionWithTraceback(e, e.__traceback__)
            _sendback_result(
                self.result_queue, self.call_item.work_id, exception=exc)
        else:
            _sendback_result(
                self.result_queue, self.call_item.work_id, result=r)
            del r


def _process_worker(call_queue, result_queue,
                    initializer, initargs, num_threads):
    if initializer is not None:
        try:
            initializer(*initargs)
        except BaseException:
            _base.LOGGER.critical('Exception in initializer:', exc_info=True)
            # The parent will notice that the process stopped and
            # mark the pool broken
            return

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        while True:
            call_item = call_queue.get(block=True)
            if call_item is None:
                # Wake up queue management thread
                result_queue.put(os.getpid())
                return

            executor.submit(Task(call_item, result_queue))
            del call_item


class CombinedPoolExecutor(ProcessPoolExecutor):
    def __init__(self, *args, num_threads=8, **kwargs):
        super().__init__(*args, **kwargs)
        self._num_threads = num_threads  # <= added

    def _adjust_process_count(self):
        # if there's an idle process, we don't need to spawn a new one.
        if hasattr(self, '_idle_worker_semaphore'):
            if self._idle_worker_semaphore.acquire(blocking=False):
                return

        # 3.9の実装と3.8の実装が違う
        while len(self._processes) < self._max_workers:
            p = self._mp_context.Process(
                target=_process_worker,
                args=(self._call_queue,
                      self._result_queue,
                      self._initializer,
                      self._initargs,
                      self._num_threads))  # <= added
            p.start()
            self._processes[p.pid] = p
