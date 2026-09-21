MASK = 0xffffffff

INITIAL_VALUE = 0x9E3779B9
C1 = 0x85EBCA77
C2 = 0xC2B2AE3D


def rotate_left(x: int, r: int) -> int:
    x &= MASK
    return ((x << r) | (x >> (32 - r))) & MASK


def hash32(data: bytes) -> int:
    h = INITIAL_VALUE

    for byte in data:

        # Round 1
        h ^= byte
        h = (h * C1) & MASK
        h = rotate_left(h, 5)

        # Round 2
        h ^= (h >> 13)
        h = (h * C2) & MASK
        h = rotate_left(h, 7)

    # Final mixing
    h ^= h >> 16
    h = (h * C1) & MASK
    h ^= h >> 13
    h = (h * C2) & MASK
    h ^= h >> 16

    return h


def main():
    data = b"hello every on"
    return hash32(data)


if __name__ == "__main__":
    print(main())