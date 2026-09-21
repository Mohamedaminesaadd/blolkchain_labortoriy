from collections import defaultdict


# ============================================================
# 1. WEAK HASH FUNCTION
# ============================================================

def weak_hash(data: bytes) -> int:
    """
    Very weak hash function.

    Output range:
        0 ... 255

    Therefore there are only 256 possible hash values.
    """

    h = 0

    for byte in data:
        h = (h + byte) % 256

    return h


# ============================================================
# 2. GENERATE INPUTS
# ============================================================

def generate_input(n: int) -> list[bytes]:
    """
    Generate 3-byte inputs.

    Each byte must be between 0 and 255.
    """

    result = []

    limit = min(n, 256)

    for i in range(limit):
        for j in range(limit // 2):
            for k in range(limit // 4):

                data = bytes([i, j, k])

                result.append(data)

    return result


# ============================================================
# 3. COLLISION DETECTION
# ============================================================

def find_collisions(inputs: list[bytes]):
    """
    Detect collisions.

    A collision occurs when:

        data1 != data2

    but:

        hash(data1) == hash(data2)
    """

    seen = {}
    collisions = []

    for data in inputs:

        h = weak_hash(data)

        if h in seen:

            previous_data = seen[h]

            if previous_data != data:

                collisions.append(
                    (previous_data, data, h)
                )

        else:

            seen[h] = data

    return collisions, seen


# ============================================================
# 4. MAIN
# ============================================================

def main():

    # Number of values used for each byte
    n = 32

    print("=" * 60)
    print("HASH COLLISION LAB")
    print("=" * 60)

    # Generate inputs
    inputs = generate_input(n)

    print(f"\nInputs generated: {len(inputs)}")

    # Find collisions
    collisions, seen = find_collisions(inputs)

    print(f"Unique hash values: {len(seen)}")
    print(f"Collisions found: {len(collisions)}")

    print("\n" + "=" * 60)
    print("FIRST COLLISIONS")
    print("=" * 60)

    # Display only first 20 collisions
    for index, (data1, data2, h) in enumerate(
        collisions[:20],
        start=1
    ):

        print(
            f"\nCollision #{index}"
        )

        print(
            f"  Input 1 : {data1}"
        )

        print(
            f"  Input 2 : {data2}"
        )

        print(
            f"  Hash    : {h}"
        )

        print(
            f"  Different inputs? {data1 != data2}"
        )

        print(
            f"  Same hash?       {weak_hash(data1) == weak_hash(data2)}"
        )


# ============================================================
# PROGRAM ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()