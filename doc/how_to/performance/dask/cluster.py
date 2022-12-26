# cluster.py
from dask.distributed import LocalCluster

DASK_SCHEDULER_PORT = 64719
DASK_SCHEDULER_ADDRESS = f"tcp://127.0.0.1:{DASK_SCHEDULER_PORT}"
N_WORKERS = 4

if __name__ == '__main__':
    cluster = LocalCluster(scheduler_port=DASK_SCHEDULER_PORT, n_workers=N_WORKERS)
    print(cluster.scheduler_address)
    input()