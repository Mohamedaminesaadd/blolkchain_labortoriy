MASK = 0xffffffff #(32 bits)

INITIAL_VALUE = 0x811C9DC5 #(32 bits)
CONSTANT = 0x01000193 #(32 bits)


def rotate_left(x: int, r: int) -> int:
    x &= MASK
    return ((x << r) | (x >> (32 - r))) & MASK


def hash32(data: bytes) -> int:
    h = INITIAL_VALUE

    for byte in data:

        # 1. Mix the byte into the state
        h ^= byte #(mixing the byte into the state using XOR operation)

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