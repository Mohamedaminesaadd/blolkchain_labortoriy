# =========================
# RSA FROM SCRATCH
# =========================

p = 5
q = 11

# Public modulus
n = p * q

# Euler's totient
phi = (p - 1) * (q - 1)

# Public exponent
e = 3

# Original message
m = 7

# =========================
# ENCRYPTION
# =========================

# c = m^e mod n
c = pow(m, e, n)

print("n =", n)
print("phi =", phi)
print("e =", e)
print("Original message =", m)
print("Encrypted message =", c)


# =========================
# FIND PRIVATE EXPONENT d
# =========================

# Find d such that:
# e*d ≡ 1 (mod phi)

d = 1

while (e * d) % phi != 1:
    d += 1

print("Private exponent d =", d)


# =========================
# DECRYPTION
# =========================

# m = c^d mod n
m1 = pow(c, d, n)

print("Decrypted message =", m1)