import hashlib

target = "0000000"
nonce =0

while True:
    data = f"hellotcoin {nonce}"

    hash_value = hashlib.sha256(
        data.encode()
    ).hexdigest()

    if hash_value.startswith(target):
        print("proof of work found ")
        print("Nonce,",nonce)
        print("hash",hash_value)
        break
    nonce+=1
