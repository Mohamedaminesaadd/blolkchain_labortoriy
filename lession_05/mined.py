
import hashlib
import random
import time

MIN_NUMBER = 1
MAX_NUMBER = 1_000_000_00
BLOCK_SIZE = 10_000_0


def hash_number(number: int) -> str:
    return hashlib.sha256(str(number).encode("utf-8")).hexdigest()


def incremental_search(target_hash: str) -> None:
    start_time = time.perf_counter()

    for number in range(MIN_NUMBER, MAX_NUMBER + 1):
        if hash_number(number) == target_hash:
            break

    elapsed = time.perf_counter() - start_time
    print(f"Incremental search: {elapsed:.6f} seconds")


def random_block_search(target_hash: str, seed: int = 42) -> None:
    start_time = time.perf_counter()
    rng = random.Random(seed)

    total_numbers = MAX_NUMBER - MIN_NUMBER + 1
    number_of_blocks = (
        total_numbers + BLOCK_SIZE - 1
    ) // BLOCK_SIZE

    block_indices = list(range(number_of_blocks))
    rng.shuffle(block_indices)

    for block_index in block_indices:
        start = MIN_NUMBER + block_index * BLOCK_SIZE
        end = min(start + BLOCK_SIZE - 1, MAX_NUMBER)

        for number in range(start, end + 1):
            if hash_number(number) == target_hash:
                elapsed = time.perf_counter() - start_time
                print(f"Random block search: {elapsed:.6f} seconds")
                return

    elapsed = time.perf_counter() - start_time
    print(f"Random block search: {elapsed:.6f} seconds")


if __name__ == "__main__":
    secret_number = random.randint(MIN_NUMBER, MAX_NUMBER)
    target_hash = hash_number(secret_number)

    incremental_search(target_hash)
    random_block_search(target_hash, seed=42)
