MASK = 0xffffffff

INITIAL_VALUE = 0x811C9DC5
CONSTANT = 0x01000193


def rotate_left(x: int, r: int) -> int:
    x &= MASK
    return ((x << r) | (x >> (32 - r))) & MASK


def hash32(data: bytes) -> int:
    h = INITIAL_VALUE

    for byte in data:

        # 1. Mix the byte into the state
        h ^= byte

        # 2. Modular multiplication
        h *= CONSTANT
        h &= MASK

        # 3. Rotate bits
        h = rotate_left(h, 5)

    return h



def main():
    data = b"hello every on"
    return hash32(data)


if __name__ == "__main__":
    print(main())