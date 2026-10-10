from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes

# ============================================================
# 1. Generate ECC private key
# ============================================================

private_key = ec.generate_private_key(
    ec.SECP256R1() # algorithm for the elliptic curve (NIST P-256)
)

# Generate public key
public_key = private_key.public_key()

print("ECC keys generated\n","Private key:", private_key.private_numbers().private_value,"\n",
      "Public key:", public_key.public_numbers().x, public_key.public_numbers().y)  


# ============================================================
# 2. Message
# ============================================================

message = b"Hello ECC"


# ============================================================
# 3. Create ECDSA signature
# ============================================================

signature = private_key.sign(
    message,
    ec.ECDSA(hashes.SHA256()) #algorithm for the signature (ECDSA with SHA-256)
)

print("ECC signature created",signature.hex())


# ============================================================
# 4. Verify signature
# ============================================================

#message = b"Helclo ECC"  this is to test the signature verification with a modified message
try:
    public_key.verify(
        signature,
        message,
        ec.ECDSA(hashes.SHA256())
    )

    print("ECC signature VALID")

except Exception:
    print("ECC signature INVALID")