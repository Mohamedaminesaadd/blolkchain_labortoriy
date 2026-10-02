# ============================================================
# 1. HASH FUNCTION
# ============================================================

def hash32(data: bytes) -> int:
    """
    Simple 32-bit hash function.

    Output:
        integer between 0 and 2^32 - 1
    """

    h = 0

    for byte in data:
        h = (h + byte) % (2 ** 32)

    return h


# ============================================================
# 2. CALCULATE HAMMING DISTANCE
# ============================================================

def calculate_avalanche(m1: bytes, m2: bytes) -> float:
    """
    Calculate the avalanche effect between two messages.

    Steps:
        1. Calculate H(m1)
        2. Calculate H(m2)
        3. XOR the two hashes
        4. Count the number of 1 bits
        5. Calculate percentage

    Formula:

        avalanche = changed_bits / 32 * 100
    """

    h1 = hash32(m1)
    h2 = hash32(m2)

    # XOR
    diff = h1 ^ h2

    # Count the number of changed bits
    changed_bits = 0

    for i in range(32):

        # Check bit i
        if diff & (1 << i):
            changed_bits += 1

    # Avalanche percentage
    avalanche = (changed_bits / 32) * 100

    return avalanche


# ============================================================
# 3. DISPLAY HASH IN BINARY
# ============================================================

def print_hash_info(m1: bytes, m2: bytes):

    h1 = hash32(m1)
    h2 = hash32(m2)

    diff = h1 ^ h2

    changed_bits = diff.bit_count()

    avalanche = (changed_bits / 32) * 100

    print("=" * 60)

    print("MESSAGE 1:")
    print(m1)

    print("HASH 1:")
    print(f"{h1:032b}")

    print()

    print("MESSAGE 2:")
    print(m2)

    print("HASH 2:")
    print(f"{h2:032b}")

    print()

    print("XOR:")
    print(f"{diff:032b}")

    print()

    print(f"Changed bits : {changed_bits}/32")
    print(f"Avalanche    : {avalanche:.2f}%")

    print("=" * 60)


# ============================================================
# 4. MAIN
# ============================================================

def main():

    # Original message
    m1 = b"hello"

    # Change ONE bit in the message
    m2 = bytearray(m1)

    # Change the last bit of the last byte
    m2[-1] ^= 1

    # Convert back to bytes
    m2 = bytes(m2)

    print_hash_info(m1, m2)


# ============================================================
# PROGRAM ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()


