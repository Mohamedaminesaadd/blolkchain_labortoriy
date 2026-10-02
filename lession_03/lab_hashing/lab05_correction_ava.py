# ============================================================
# LAB 04 — AVALANCHE EFFECT
# 32-BIT CUSTOM HASH
# ============================================================

MASK = 0xFFFFFFFF


# ============================================================
# 1. ROTATE LEFT
# ============================================================

def rotate_left(x: int, r: int) -> int:
    """
    Rotate a 32-bit integer to the left.

    Example:
        ABCD -> BCDA
    """

    return ((x << r) | (x >> (32 - r))) & MASK


# ============================================================
# 2. 32-BIT HASH FUNCTION
# ============================================================

def hash32(data: bytes) -> int:
    """
    Custom educational 32-bit hash.

    Output:
        32-bit integer
    """

    # Initial value
    h = 0x811C9DC5 # value of the FNV-1a hash arbitrarily chosen for this example

    for byte in data:

        # ----------------------------------------------------
        # Step 1 — XOR input byte
        # ----------------------------------------------------
        h ^= byte # h = h XOR byte

        # ----------------------------------------------------
        # Step 2 — Multiplication
        # ----------------------------------------------------
        h = (h * 0x01000193) & MASK #(h * 16777619) mod 2^32

        # ----------------------------------------------------
        # Step 3 — Rotation
        # ----------------------------------------------------
        h = rotate_left(h, 5) #(h << 5) | (h >> (32 - 5)) mod 2^32

        # ----------------------------------------------------
        # Step 4 — XOR with shifted version
        # ----------------------------------------------------
        h ^= h >> 13 # h = h XOR (h >> 13)

        # ----------------------------------------------------
        # Step 5 — More multiplication
        # ----------------------------------------------------
        h = (h * 0x85EBCA6B) & MASK

    # ========================================================
    # FINAL AVALANCHE / FINALIZATION
    # ========================================================

    h ^= h >> 16

    h = (h * 0x85EBCA6B) & MASK

    h ^= h >> 13

    h = (h * 0xC2B2AE35) & MASK

    h ^= h >> 16

    return h & MASK


# ============================================================
# 3. CALCULATE AVALANCHE
# ============================================================

def calculate_avalanche(m1: bytes, m2: bytes):
    """
    Compare two messages.

    Steps:

        H(m1)
          XOR
        H(m2)
          ↓
        Count changed bits
          ↓
        Avalanche percentage
    """

    h1 = hash32(m1)
    h2 = hash32(m2)

    # XOR the two hashes
    diff = h1 ^ h2

    # Count the number of 1 bits
    changed_bits = diff.bit_count()

    # Calculate percentage
    percentage = (changed_bits / 32) * 100

    return h1, h2, diff, changed_bits, percentage


# ============================================================
# 4. PRINT HASH INFORMATION
# ============================================================

def print_hash_info(m1: bytes, m2: bytes):

    h1, h2, diff, changed_bits, percentage = \
        calculate_avalanche(m1, m2)

    print("=" * 70)

    print("MESSAGE 1")
    print("--------------------")
    print(m1)

    print()

    print("MESSAGE 2")
    print("--------------------")
    print(m2)

    print()

    print("HASH 1")
    print("--------------------")
    print(f"{h1:032b}")
    print(f"0x{h1:08X}")

    print()

    print("HASH 2")
    print("--------------------")
    print(f"{h2:032b}")
    print(f"0x{h2:08X}")

    print()

    print("XOR")
    print("--------------------")
    print(f"{diff:032b}")
    print(f"0x{diff:08X}")

    print()

    print("AVALANCHE RESULT")
    print("--------------------")
    print(f"Changed bits : {changed_bits}/32")
    print(f"Avalanche    : {percentage:.2f}%")

    print("=" * 70)


# ============================================================
# 5. CHANGE ONE BIT
# ============================================================

def change_one_bit(data: bytes, bit_position: int) -> bytes:
    """
    Change exactly ONE bit in the input.

    bit_position:
        0 = first bit
        1 = second bit
        ...

    """

    data = bytearray(data)

    byte_position = bit_position // 8
    bit_in_byte = bit_position % 8

    data[byte_position] ^= (1 << bit_in_byte)

    return bytes(data)


# ============================================================
# 6. TEST ONE-BIT CHANGES
# ============================================================

def test_one_bit_changes(data: bytes):

    total_percentage = 0
    total_changed_bits = 0

    number_of_bits = len(data) * 8

    print("\n")
    print("=" * 70)
    print("ONE-BIT AVALANCHE TEST")
    print("=" * 70)

    print(f"Original message: {data}")
    print(f"Number of input bits: {number_of_bits}")

    print()

    for bit in range(number_of_bits):

        modified = change_one_bit(data, bit)

        h1 = hash32(data)
        h2 = hash32(modified)

        diff = h1 ^ h2

        changed_bits = diff.bit_count()

        percentage = (changed_bits / 32) * 100

        total_changed_bits += changed_bits
        total_percentage += percentage

        print(
            f"Bit {bit:2d} | "
            f"Changed output bits: {changed_bits:2d}/32 | "
            f"Avalanche: {percentage:6.2f}%"
        )

    # Average
    average_changed_bits = total_changed_bits / number_of_bits
    average_percentage = total_percentage / number_of_bits

    print()
    print("-" * 70)

    print(
        f"Average changed bits : "
        f"{average_changed_bits:.2f}/32"
    )

    print(
        f"Average avalanche    : "
        f"{average_percentage:.2f}%"
    )

    print("-" * 70)


# ============================================================
# 7. MAIN
# ============================================================

def main():

    # --------------------------------------------------------
    # Test 1 — Simple one-bit modification
    # --------------------------------------------------------

    message1 = b"hello"

    message2 = bytearray(message1)

    # Change ONE bit
    message2[-1] ^= 1

    message2 = bytes(message2)

    print_hash_info(
        message1,
        message2
    )

    # --------------------------------------------------------
    # Test 2 — Test every input bit
    # --------------------------------------------------------

    test_one_bit_changes(
        b"hello"
    )


# ============================================================
# PROGRAM ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()