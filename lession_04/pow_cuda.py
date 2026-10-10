from numba import cuda
import numpy as np
import hashlib


@cuda.jit
def search_nonce(start_nonce, results):
    i = cuda.grid(1)

    nonce = start_nonce + i

    # For demonstration only:
    # real SHA-256 implementation inside CUDA
    # would need to be implemented separately.

    results[i] = nonce


threads_per_block = 256
blocks = 1024

n = threads_per_block * blocks

results = np.zeros(n, dtype=np.uint64)

d_results = cuda.to_device(results)

search_nonce[blocks, threads_per_block](0, d_results)

results = d_results.copy_to_host()

print(results[:20])