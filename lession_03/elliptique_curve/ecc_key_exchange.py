from cryptography.hazmat.primitives.asymmetric import ec

# ============================================================
# Alice generates her private/public keys
# ============================================================

alice_private = ec.generate_private_key(
    ec.SECP256R1()
)

alice_public = alice_private.public_key()

print("Alice private key:", alice_private.private_numbers().private_value,"\n")
print("Alice public key:", alice_public.public_numbers().x, alice_public.public_numbers().y,"\n")

# ============================================================
# Bob generates his private/public keys
# ============================================================

bob_private = ec.generate_private_key(
    ec.SECP256R1()
)

bob_public = bob_private.public_key()

print("Bob private key:", bob_private.private_numbers().private_value,"\n")
print("Bob public key:", bob_public.public_numbers().x, bob_public.public_numbers().y,"\n")


# ============================================================
# Alice calculates shared secret
# ============================================================

alice_secret = alice_private.exchange(
    ec.ECDH(),
    bob_public
)

print("Alice secret:", alice_secret.hex())


# ============================================================
# Bob calculates shared secret
# ============================================================

bob_secret = bob_private.exchange(
    ec.ECDH(),
    alice_public
)

print("Bob secret:  ", bob_secret.hex())


print("Alice secret:", alice_secret.hex())
print("Bob secret:  ", bob_secret.hex())

print("Same secret:", alice_secret == bob_secret)