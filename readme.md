# process pool + thread pool
- max_workers: num of processes
- num_threads: num of threads per process

## USAGE
same as ProcessPoolExecutor, ThreadPoolExecutor

```python
    with combined_pool.CombinedPoolExecutor(max_workers=max_workers, num_threads=num_threads) as executor:
        executor.submit(f, 1, 2)
        executor.map(g, range(8), itertools.repeat(9))
```

# test
```
$ python tests.py  --max-workers 8 --num-cpu-task 32
elapsed_time: 14.47368574142456
$ python tests.py  --num-threads 8 --num-cpu-task 32
elapsed_time: 50.58192777633667
$ python tests.py  --max-workers 8 --num-io-task 32
elapsed_time: 4.724894285202026
$ python tests.py  --num-threads 8 --num-io-task 32
elapsed_time: 6.835118055343628
```

## supported versions
```
$ tox
  py37: commands succeeded
  py38: commands succeeded
  py39: commands succeeded
```
