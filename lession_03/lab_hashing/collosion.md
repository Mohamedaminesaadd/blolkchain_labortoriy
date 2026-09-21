Yes. The key idea is:

> **A collision happens when two different inputs produce the same hash value.**

For example:

```text
hash(b"abc") == hash(b"xyz")
```

while:

```text
b"abc" != b"xyz"
```

Your current code has several Python syntax problems, but the experiment you're trying to build is a very good one.

### 1. A simple weak hash

If you want a deliberately weak hash with only **256 possible outputs**:

```python
def weak_hash(data: bytes) -> int:
    h = 0

    for byte in data:
        h = (h + byte) % 256

    return h
```

This makes collisions very easy to find.

### 2. Detect collisions

Use a dictionary where:

```text
hash_value → first input that produced it
```

Then, when another input produces the same hash, compare the inputs.

```python
def find_collisions(inputs):
    seen = {}
    collisions = []

    for data in inputs:
        h = weak_hash(data)

        if h in seen:
            old_data = seen[h]

            if old_data != data:
                collisions.append((old_data, data, h))
        else:
            seen[h] = data

    return collisions
```

Then:

```python
inputs = [
    b"abc",
    b"abd",
    b"bac",
    b"zzz",
    b"abc"
]

collisions = find_collisions(inputs)

for a, b, h in collisions:
    print(f"Collision!")
    print(f"  {a} -> {h}")
    print(f"  {b} -> {h}")
```

You should see something like:

```text
Collision!
  b'abc' -> 38
  b'bac' -> 38
```

because:

```text
a + b + c = 97 + 98 + 99 = 294
b + a + c = 98 + 97 + 99 = 294
```

---

## 3. Your generator

Your intended generator is approximately:

```python
def generate_input(n: int) -> list:
    result = []

    for i in range(n):
        for j in range(n // 2):
            for k in range(n // 4):
                result.append(bytes([i, j, k]))

    return result
```

But there is an important problem:

```python
bytes([i, j, k])
```

requires every value to be between:

```text
0 ≤ value ≤ 255
```

So `n = 10000` cannot work.

Use:

```python
def generate_input(n: int) -> list:
    result = []

    limit = min(n, 256)

    for i in range(limit):
        for j in range(limit // 2):
            for k in range(limit // 4):
                result.append(bytes([i, j, k]))

    return result
```

However, even this produces millions of inputs. You don't actually need that many to demonstrate collisions.

---

# 4. Better collision experiment

I recommend doing this statistically:

```python
def weak_hash(data: bytes) -> int:
    return sum(data) % 256


def find_collisions(n: int):
    seen = {}
    collision_count = 0

    for i in range(n):
        for j in range(n):
            data = bytes([i, j])

            h = weak_hash(data)

            if h in seen:
                old_data = seen[h]

                if old_data != data:
                    collision_count += 1

                    if collision_count <= 10:
                        print(
                            f"Collision #{collision_count}: "
                            f"{old_data} and {data} -> {h}"
                        )
            else:
                seen[h] = data

    print()
    print(f"Inputs tested: {n * n}")
    print(f"Unique hashes: {len(seen)}")
    print(f"Collisions: {collision_count}")


find_collisions(256)
```

You'll discover something fundamental:

```text
Number of possible inputs
        ↓
      65,536

Number of possible hashes
        ↓
        256
```

Therefore collisions are **mathematically unavoidable**.

---

# 5. The mathematical reason

Suppose your hash function is:

$$
H : X \rightarrow Y
$$

where:

* \(X\) = possible inputs
* \(Y\) = possible hash values

If:

$$
|X| > |Y|
$$

then by the **pigeonhole principle**, at least two different inputs must have the same hash.

For your 256-bit-value example:

$$
|Y| = 256
$$

but for two-byte inputs:

$$
|X| = 256^2 = 65,536
$$

Therefore:

$$
65,536 > 256
$$

and collisions are guaranteed.

---

## 6. This connects directly to your 32-bit hash lab

If you build:

```python
def hash32(data: bytes) -> int:
    ...
```

then the output space is:

$$
2^{32}
$$

which is:

$$
4,294,967,296
$$

possible hash values.

But the number of possible arbitrary byte strings is effectively much larger.

Therefore:

$$
|X| > 2^{32}
$$

and collisions are **still guaranteed**.

The goal of a good hash isn't:

> "Never collide."

That's impossible for a fixed-size hash.

The goal is:

> **Make collisions sufficiently difficult/unlikely and distribute inputs uniformly across the output space.**

---

### Your next lab should be

I would structure your hash learning exactly like this:

```text
LAB 01 — Weak Hash
    ↓
LAB 02 — Collision Detection
    ↓
LAB 03 — Collision Rate Measurement
    ↓
LAB 04 — Pigeonhole Principle Experiment
    ↓
LAB 05 — 8-bit Hash
    ↓
LAB 06 — 16-bit Hash
    ↓
LAB 07 — 32-bit Hash
    ↓
LAB 08 — XOR + Rotation
    ↓
LAB 09 — Avalanche Effect
    ↓
LAB 10 — Hash Table + Collision Resolution
```

The **most important experiment after collision detection** is measuring the **collision rate** and comparing your weak hash with your new 32-bit hash.
