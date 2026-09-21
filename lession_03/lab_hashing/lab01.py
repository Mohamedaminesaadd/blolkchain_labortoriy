def my_hash(data):
    h = 1

    for byte in data.encode():
        h = (h * 31 + byte) % (2**32 - 1)

    for byte in h.to_bytes(8, byteorder='big'):
        h = (h * 31 + byte) % (2**64 - 1)

    return h



def main():
    data = "hello every on"
    return my_hash(data)


if __name__ == "__main__":
    print(main())