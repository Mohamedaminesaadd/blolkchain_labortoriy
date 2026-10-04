from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding


# ============================================================
# RSA KEY GENERATION
# ============================================================

def generate_rsa_keys():

    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=4096
    )

    public_key = private_key.public_key()

    return public_key, private_key


# ============================================================
# SHA-256
# ============================================================

def sha256(message):

    if isinstance(message, str):
        message = message.encode()

    digest = hashes.Hash(hashes.SHA256())
    digest.update(message)

    return digest.finalize()


# ============================================================
# DIGITAL SIGNATURE
# RSA-PSS + SHA-256
# ============================================================

def sign(message, private_key):

    if isinstance(message, str):
        message = message.encode()

    signature = private_key.sign(
        message,

        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),

        hashes.SHA256()
    )

    return signature


# ============================================================
# VERIFY
# ============================================================

def verify(message, signature, public_key):

    if isinstance(message, str):
        message = message.encode()

    try:

        public_key.verify(
            signature,
            message,

            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),

            hashes.SHA256()
        )

        return True

    except Exception:
        return False


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    message = "Hello Blockchain"

    print("Message:")
    print(message)

    # --------------------------------------------------------
    # Generate RSA-4096 keys
    # --------------------------------------------------------

    print("\nGenerating RSA-4096 keys...")

    public_key, private_key = generate_rsa_keys()

    print("✓ Keys generated")

    # --------------------------------------------------------
    # SHA-256
    # --------------------------------------------------------

    print("\nSHA-256:")

    digest = sha256(message)

    print(digest.hex())

    # --------------------------------------------------------
    # Sign
    # --------------------------------------------------------

    print("\nGenerating digital signature...")

    signature = sign(
        message,
        private_key
    )

    print("\nSignature:")
    print(signature.hex())

    # --------------------------------------------------------
    # Verify original message
    # --------------------------------------------------------

    print("\nVerifying signature...")

    valid = verify(
        message,
        signature,
        public_key
    )

    if valid:
        print("✓ Digital signature is VALID")
    else:
        print("✗ Digital signature is INVALID")

    # --------------------------------------------------------
    # Modify message
    # --------------------------------------------------------

    print("\nTesting modified message...")

    modified_message = "Hello Blockchain"

    valid = verify(
        modified_message,
        signature,
        public_key
    )

    if valid:
        print("✓ Digital signature is VALID")
    else:
        print("✗ Digital signature is INVALID")