from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization


# ============================================================
# 1. GENERATE RSA-4096 KEY PAIR
# ============================================================

private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=4096
)

public_key = private_key.public_key()


# ============================================================
# 2. MESSAGE
# ============================================================

message = b"Hello, this is a secret message."


# ============================================================
# 3. ENCRYPT WITH PUBLIC KEY
# ============================================================

ciphertext = public_key.encrypt(
    message,
    padding.OAEP(
        mgf=padding.MGF1(
            algorithm=hashes.SHA256()
        ),
        algorithm=hashes.SHA256(),
        label=None
    )
)

print("Ciphertext:")
print(ciphertext.hex())


# ============================================================
# 4. DECRYPT WITH PRIVATE KEY
# ============================================================

plaintext = private_key.decrypt(
    ciphertext,
    padding.OAEP(
        mgf=padding.MGF1(
            algorithm=hashes.SHA256()
        ),
        algorithm=hashes.SHA256(),
        label=None
    )
)

print("\nDecrypted message:")
print(plaintext.decode())