Yes. This is a very good lab because it makes the internal mechanics of a hash function concrete.

The goal is **not cryptographic security yet**. We will build a custom **32-bit non-cryptographic hash** from scratch and then test its properties.

## 1. First, define the mathematics

We want:

$$
H:\{0,1,\ldots,255\}^* \rightarrow \{0,1,\ldots,2^{32}-1\}
$$

So:

* Input: arbitrary bytes
* Internal state: 32 bits
* Output: exactly 32 bits
* Arithmetic: modulo \(2^{32}\)

Define:

$$
M = 2^{32}
$$

Every time we perform an arithmetic operation, we can force the result back into 32 bits with:

$$
h \leftarrow h \bmod 2^{32}
$$

In Python:

```python
h &= 0xffffffff
```

---

# 2. Build the rotation operation

A rotation is different from a normal shift.

For a 32-bit value:

$$
ROTL(x,r)
=
((x \ll r) \;|\; (x \gg (32-r))) \bmod 2^{32}
$$

Python:

```python
def rotate_left(x: int, r: int) -> int:
    x &= 0xffffffff

    return ((x << r) | (x >> (32 - r))) & 0xffffffff
```

For example, rotating left by 5:

```text
abcdefgh ijklmnop qrstuvwx yzABCDEF
     ↓
fghij... 
```

The bits that leave the left side come back on the right.

This is important because a normal `<<` would simply throw away those bits.

---

# 3. Create your first hash

Let's make a deliberately simple algorithm.

```python
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
```

Test it:

```python
print(hex(hash32(b"hello")))
print(hex(hash32(b"hello!")))
print(hex(hash32(b"Hello")))
print(hex(hash32(b"")))
```

You should get a 32-bit hexadecimal value such as:

```text
0x........
```

The exact values are determined by your algorithm.

---

# 4. But let's make it a real laboratory

I recommend that you **don't stop here**.

Let's build a version with **multiple mixing rounds**.

The architecture will be:

```text
                input byte
                    │
                    ▼
              ┌───────────┐
              │    XOR    │
              └─────┬─────┘
                    │
                    ▼
              ┌───────────┐
              │ multiply  │
              └─────┬─────┘
                    │
                    ▼
              ┌───────────┐
              │ rotate    │
              └─────┬─────┘
                    │
                    ▼
              ┌───────────┐
              │    XOR    │
              └─────┬─────┘
                    │
                    ▼
              ┌───────────┐
              │ multiply  │
              └─────┬─────┘
                    │
                    ▼
                  h
```

Implementation:

```python
MASK = 0xffffffff

INITIAL_VALUE = 0x9E3779B9
C1 = 0x85EBCA77
C2 = 0xC2B2AE3D


def rotate_left(x: int, r: int) -> int:
    x &= MASK
    return ((x << r) | (x >> (32 - r))) & MASK


def hash32(data: bytes) -> int:
    h = INITIAL_VALUE

    for byte in data:

        # Round 1
        h ^= byte
        h = (h * C1) & MASK
        h = rotate_left(h, 5)

        # Round 2
        h ^= (h >> 13)
        h = (h * C2) & MASK
        h = rotate_left(h, 7)

    # Final mixing
    h ^= h >> 16
    h = (h * C1) & MASK
    h ^= h >> 13
    h = (h * C2) & MASK
    h ^= h >> 16

    return h
```

This is now much more interesting.

---

# 5. Understand exactly what each operation does

Suppose:

```python
h = 0x12345678
```

### XOR

```python
h ^= byte
```

Mathematically:

$$
h = h \oplus b
$$

XOR changes selected bits depending on the input byte.

---

### Multiplication

```python
h = (h * C1) & MASK
```

Mathematically:

$$
h = (hC_1)\mod 2^{32}
$$

This introduces nonlinear behavior in the bit representation.

---

### Rotation

```python
h = rotate_left(h, 5)
```

Mathematically:

$$
h = ROTL_{32}(h,5)
$$

This redistributes bits across different positions.

---

### XOR with shifted state

```python
h ^= h >> 13
```

Mathematically:

$$
h = h \oplus \left\lfloor\frac{h}{2^{13}}\right\rfloor
$$

This mixes information from high-order bits into lower-order bits.

---

# 6. Why do we need `& 0xffffffff`?

This is one of the most important parts of your lab.

Python integers are not naturally restricted to 32 bits.

For example:

```python
x = 0xffffffff
x *= 2

print(hex(x))
```

You get:

```text
0x1fffffffe
```

That's **33 bits**.

But our hash must operate in:

$$
0 \le h < 2^{32}
$$

Therefore:

```python
h &= 0xffffffff
```

keeps only the lowest 32 bits.

So:

$$
0x1FFFFFFFE
$$

becomes:

$$
0xFFFFFFFE
$$

This is equivalent to:

$$
h \mod 2^{32}
$$

---

# 7. Why 32-bit?

This connects directly to your previous question about **32-bit vs 64-bit computers**.

The hash size is **not determined by whether your computer is 32-bit or 64-bit**.

You can run a 32-bit hash on a 64-bit computer.

We explicitly define:

$$
M = 2^{32}
$$

Therefore the hash has:

$$
2^{32}
$$

possible outputs.

That is:

$$
4,294,967,296
$$

possible hash values.

---

# 8. And here comes the collision problem

Your input space is potentially enormous.

For example:

```text
b"a"
b"b"
b"hello"
b"hello world"
...
```

There are infinitely many possible byte strings.

But our output space contains only:

$$
2^{32}
$$

values.

Therefore collisions are mathematically unavoidable.

There must exist:

$$
x \ne y
$$

such that:

$$
H(x)=H(y)
$$

This follows from the pigeonhole principle.

Your hash is:

$$
H:\text{arbitrarily many inputs}\rightarrow 2^{32}\text{ outputs}
$$

Therefore:

$$
\boxed{\text{Collisions must exist}}
$$

---

# 9. Let's actually search for collisions

Create a collision experiment:

```python
def find_collision():
    seen = {}

    i = 0

    while True:
        data = i.to_bytes(8, "little")
        h = hash32(data)

        if h in seen:
            return seen[h], data, h

        seen[h] = data
        i += 1


a, b, h = find_collision()

print("Input A:", a.hex())
print("Input B:", b.hex())
print("Hash:", hex(h))
```

Eventually:

```text
Input A: ...
Input B: ...
Hash: 0x........
```

You have found:

$$
H(A)=H(B)
$$

while:

$$
A\ne B
$$

That's the central concept behind hash collisions.

---

# 10. Test the avalanche effect

A good hash should ideally have an **avalanche effect**.

Change one input bit:

```text
input A:
01101000 01101001

input B:
01101000 01101000
                     ↑
```

Then compare:

```python
a = hash32(b"hi")
b = hash32(b"hh")

print(hex(a))
print(hex(b))
```

We can count how many output bits changed:

```python
def count_bits(x: int) -> int:
    return x.bit_count()


def hamming_distance(a: int, b: int) -> int:
    return count_bits(a ^ b)


a = hash32(b"hi")
b = hash32(b"hh")

print("Hash A:", hex(a))
print("Hash B:", hex(b))
print("Changed bits:", hamming_distance(a, b))
```

Ideally, changing one input bit should change roughly half of the 32 output bits:

$$
\frac{32}{2}=16
$$

So something like:

```text
Changed bits: 15
```

or:

```text
Changed bits: 17
```

is reasonable.

---

# 11. Your complete Lab 01

I would structure your project like this:

```text
better-hash/
│
├── hash32.py
├── test_hash.py
├── collision_test.py
├── avalanche_test.py
└── README.md
```

### `hash32.py`

```python
MASK = 0xffffffff

INITIAL_VALUE = 0x9E3779B9
C1 = 0x85EBCA77
C2 = 0xC2B2AE3D


def rotate_left(x: int, r: int) -> int:
    x &= MASK
    return ((x << r) | (x >> (32 - r))) & MASK


def hash32(data: bytes) -> int:
    h = INITIAL_VALUE

    for byte in data:

        h ^= byte

        h = (h * C1) & MASK

        h = rotate_left(h, 5)

        h ^= h >> 13

        h = (h * C2) & MASK

        h = rotate_left(h, 7)

    h ^= h >> 16
    h = (h * C1) & MASK
    h ^= h >> 13
    h = (h * C2) & MASK
    h ^= h >> 16

    return h & MASK
```

Then:

```python
from hash32 import hash32


tests = [
    b"",
    b"a",
    b"hello",
    b"Hello",
    b"hello!",
    b"hello world",
    bytes(range(256)),
]


for data in tests:
    print(
        f"{data!r:20} -> "
        f"0x{hash32(data):08x}"
    )
```

---

## 12. The important conceptual picture

You are essentially constructing a **32-bit state machine**:

$$
h_0 = IV
$$

For each byte \(b_i\):

$$
h_{i+1}=F(h_i,b_i)
$$

where your mixing function is approximately:

$$
h' = h \oplus b_i
$$

$$
h' = h'C_1 \pmod {2^{32}}
$$

$$
h' = ROTL(h',5)
$$

$$
h' = h'\oplus(h'\gg13)
$$

$$
h' = h'C_2 \pmod {2^{32}}
$$

$$
h' = ROTL(h',7)
$$

After the input:

$$
H(x)=FinalMix(h_n)
$$

This is the abstraction I want you to understand:

```text
              arbitrary input
                    │
                    ▼
        ┌─────────────────────┐
        │   32-bit state h    │
        └──────────┬──────────┘
                   │
             XOR / arithmetic
                   │
                   ▼
              rotation
                   │
                   ▼
             XOR / shift
                   │
                   ▼
              multiplication
                   │
                   ▼
              32-bit state
                   │
                   ▼
              final mixing
                   │
                   ▼
             32-bit hash
```

And this is **exactly the right foundation** for your next labs: first build this hash, then measure **distribution → collisions → avalanche → bias → performance → hash-table behavior**.
