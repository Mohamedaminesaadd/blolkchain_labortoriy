import random


# ============================================================
# 1. GCD
# ============================================================

def gcd(a, b):
    while b != 0:
        a, b = b, a % b
    return a


# ============================================================
# 2. Extended Euclidean Algorithm
# ============================================================

def extended_gcd(a, b):
    if b == 0:
        return a, 1, 0

    g, x1, y1 = extended_gcd(b, a % b)

    x = y1
    y = x1 - (a // b) * y1

    return g, x, y


# ============================================================
# 3. Modular inverse
# ============================================================

def mod_inverse(e, phi):
    g, x, y = extended_gcd(e, phi)

    if g != 1:
        raise ValueError("e has no modular inverse")

    return x % phi


# ============================================================
# 4. Fast modular exponentiation
# ============================================================

def mod_pow(base, exponent, modulus):

    result = 1

    base = base % modulus

    while exponent > 0:

        # If exponent is odd
        if exponent % 2 == 1:
            result = (result * base) % modulus

        # Square the base
        base = (base * base) % modulus

        # Divide exponent by 2
        exponent //= 2

    return result


# ============================================================
# 5. Check if number is prime
# ============================================================

def is_prime(n):

    if n < 2:
        return False

    if n == 2:
        return True

    if n % 2 == 0:
        return False

    i = 3

    while i * i <= n:

        if n % i == 0:
            return False

        i += 2

    return True


# ============================================================
# 6. Generate prime
# ============================================================

def generate_prime(start=100, end=1000):

    while True:

        p = random.randint(start, end)

        if is_prime(p):
            return p


# ============================================================
# 7. Choose public exponent e
# ============================================================

def choose_e(phi):

    # Common RSA choice
    e = 65537

    if e < phi and gcd(e, phi) == 1:
        return e

    # Otherwise search
    e = 3

    while e < phi:

        if gcd(e, phi) == 1:
            return e

        e += 2

    raise ValueError("Could not find e")


# ============================================================
# 8. RSA Key Generation
# ============================================================

def generate_keys():

    # Generate two primes
    p = generate_prime()
    q = generate_prime()

    # Make sure they are different
    while q == p:
        q = generate_prime()

    # RSA modulus
    n = p * q

    # Euler's totient
    phi = (p - 1) * (q - 1)

    # Public exponent
    e = choose_e(phi)

    # Private exponent
    d = mod_inverse(e, phi)

    public_key = (e, n)
    private_key = (d, n)

    return public_key, private_key, p, q


# ============================================================
# 9. RSA Encryption
# ============================================================

def encrypt(message, public_key):

    e, n = public_key

    return mod_pow(message, e, n)


# ============================================================
# 10. RSA Decryption
# ============================================================

def decrypt(ciphertext, private_key):

    d, n = private_key

    return mod_pow(ciphertext, d, n)


# ============================================================
# 11. MAIN
# ============================================================

public_key, private_key, p, q = generate_keys()

print("p =", p)
print("q =", q)

print()

print("Public key:")
print(public_key)

print()

print("Private key:")
print(private_key)

# Message
message = 42

print()

print("Original message:")
print(message)

# Encryption
ciphertext = encrypt(message, public_key)

print()

print("Encrypted:")
print(ciphertext)

# Decryption
decrypted = decrypt(ciphertext, private_key)

print()

print("Decrypted:")
print(decrypted)