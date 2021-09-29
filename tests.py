import time
import random
import itertools

import combined_pool


def cpu_bound(task_id, cpu_cycle, verbose):
    if verbose:
        print(f'task(cpu):{task_id} started')
    s, x = 0, 12345678
    for i in range(cpu_cycle << 23):
        s += x
        x = (x * x + x + 1) & ((1 << 32) - 1)
    if verbose:
        print(f'task(cpu):{task_id} ended')


def io_bound(task_id, elapsed_time, verbose):
    if verbose:
        print(f'task(io):{task_id} started')
    et = time.time() + elapsed_time
    while et > time.time():
        time.sleep(random.random())
    if verbose:
        print(f'task(io):{task_id} ended')


def main(max_workers, num_threads, verbose, num_cpu_task, num_io_task, cpu_cycle, io_elapsed_time):
    st = time.time()
    with combined_pool.CombinedPoolExecutor(max_workers=max_workers, num_threads=num_threads) as executor:
        executor.map(cpu_bound, range(num_cpu_task), itertools.repeat(cpu_cycle), itertools.repeat(verbose))
        executor.map(io_bound, range(num_io_task), itertools.repeat(io_elapsed_time), itertools.repeat(verbose))
    print(f"elapsed_time: {time.time() - st}")


def __entry_point():
    import argparse
    parser = argparse.ArgumentParser(
        description=u'',  # プログラムの説明
    )
    parser.add_argument("--max-workers", type=int, default=1)
    parser.add_argument("--num-threads", type=int, default=2)
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--num-cpu-task", type=int, default=1)
    parser.add_argument("--num-io-task", type=int, default=1)
    parser.add_argument("--cpu-cycle", type=int, default=1)
    parser.add_argument("--io-elapsed-time", type=int, default=1)
    main(**dict(parser.parse_args()._get_kwargs()))


if __name__ == '__main__':
    __entry_point()
