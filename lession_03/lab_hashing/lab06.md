Absolutely. A **Merkle Tree** is an excellent next lab after learning hashing because it shows you how hashes can be combined to efficiently verify that data has not changed.

# Lab 05 — Build a Merkle Tree From Scratch

## 1. The main idea

Suppose you have four pieces of data:

```text
Transaction A
Transaction B
Transaction C
Transaction D
```

First, hash every piece:

```text
A ──hash──> H(A)
B ──hash──> H(B)
C ──hash──> H(C)
D ──hash──> H(D)
```

Then combine hashes in pairs:

```text
H(A) + H(B) ──hash──> H(AB)

H(C) + H(D) ──hash──> H(CD)
```

Then combine those:

```text
H(AB) + H(CD) ──hash──> ROOT
```

The final value is called the **Merkle Root**.

---

# 2. Visual structure

For four transactions:

```text
                         ROOT
                          │
                   H(HAB + HCD)
                    /          \
                   /            \
                HAB              HCD
                / \              / \
               /   \            /   \
             HA    HB          HC    HD
              │     │           │     │
              A     B           C     D
```

Mathematically:

$$
H_A = H(A)
$$

$$
H_B = H(B)
$$

$$
H_C = H(C)
$$

$$
H_D = H(D)
$$

Then:

$$
H_{AB}=H(H_A||H_B)
$$

$$
H_{CD}=H(H_C||H_D)
$$

and finally:

$$
Root=H(H_{AB}||H_{CD})
$$

where \(||\) means **concatenation**.

---

# 3. Why not simply hash everything?

You could do:

$$
H(A||B||C||D)
$$

but then verifying one transaction is inefficient.

A Merkle Tree lets you prove:

> "Transaction B is included in this dataset."

without giving you all the other transactions.

For example, to prove that `B` exists, you only need:

```text
B
HB
HA
HCD
ROOT
```

The proof is:

```text
B
 │
 ▼
HB
 │
 + HA
 │
 ▼
HAB
 │
 + HCD
 │
 ▼
ROOT
```

This is called a **Merkle Proof**.

---

# 4. Why is this useful?

Merkle Trees are used in systems such as:

* blockchains
* distributed systems
* version/data verification
* peer-to-peer systems
* authenticated data structures
* some database/storage systems

The key property is **tamper detection**.

Suppose:

```text
A
B
C
D
```

produces:

```text
ROOT = 8F3A...
```

Someone changes:

```text
C
```

to:

```text
C'
```

Then:

```text
C
 ↓
HC
 ↓
HCD
 ↓
ROOT
```

changes.

So:

```text
ROOT_old != ROOT_new
```

You immediately know that something in the tree changed.

---

# 5. Building it from scratch

For your lab, don't use a Merkle Tree library.

Use your own `hash32()` from the previous lab.

Your architecture becomes:

```text
                 hash32()
                    │
                    ▼
             ┌─────────────┐
             │ Transaction │
             └─────────────┘
                    │
                    ▼
                  HASH
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
       HASH A              HASH B
          │                   │
          └────────┬──────────┘
                   ▼
               HASH AB
                   │
          ┌────────┴────────┐
          ▼                 ▼
       HASH AB            HASH CD
          │                 │
          └────────┬────────┘
                   ▼
               MERKLE ROOT
```

---

# 6. Important concept: levels

A Merkle Tree is usually constructed **bottom-up**.

For four transactions:

### Level 0

```text
A    B    C    D
```

### Level 1

```text
AB       CD
```

### Level 2

```text
       ROOT
```

So:

```text
Level 0:  A   B   C   D

Level 1:    AB      CD

Level 2:       ROOT
```

Each level contains approximately half the number of nodes.

---

# 7. The algorithm

Suppose:

```python
data = [
    b"Transaction A",
    b"Transaction B",
    b"Transaction C",
    b"Transaction D"
]
```

First:

```python
level = [
    hash32(b"Transaction A"),
    hash32(b"Transaction B"),
    hash32(b"Transaction C"),
    hash32(b"Transaction D")
]
```

Then process pairs:

```text
hash A + hash B
        ↓
      hash
        ↓
     hash AB
```

and:

```text
hash C + hash D
        ↓
      hash
        ↓
     hash CD
```

Then:

```text
hash AB + hash CD
        ↓
      hash
        ↓
       ROOT
```

---

# 8. The interesting part: odd number of nodes

What happens with:

```text
A B C
```

?

You have:

```text
HA HB HC
```

But `HC` has no partner.

There are several Merkle Tree conventions.

A common educational convention is to **duplicate the last node**:

```text
HA HB HC HC
```

Then:

```text
HA + HB → HAB

HC + HC → HCC
```

and:

```text
HAB + HCC → ROOT
```

So your implementation can use:

```python
if len(level) % 2 == 1:
    level.append(level[-1])
```

But this behavior is a **design choice**; different protocols can define odd-node handling differently.

---

# 9. The hash combination

This part is important.

You don't want:

```python
hash32(str(hash_a) + str(hash_b))
```

Instead, work with the underlying bytes.

For a 32-bit hash:

```python
hash_a.to_bytes(4, "big")
```

and:

```python
hash_b.to_bytes(4, "big")
```

Then:

```python
combined = hash_a.to_bytes(4, "big") + \
           hash_b.to_bytes(4, "big")
```

Then:

```python
parent = hash32(combined)
```

So:

$$
Parent=H(H_A||H_B)
$$

---

# 10. Your complete lab architecture

I recommend structuring the next lab like this:

```text
LAB 05 — MERKLE TREE
│
├── 1. Existing hash32()
│
├── 2. Hash transactions
│
├── 3. Build leaf level
│
├── 4. Combine pairs
│
├── 5. Build parent level
│
├── 6. Repeat until one hash remains
│
├── 7. Return Merkle Root
│
├── 8. Print the tree
│
├── 9. Modify one transaction
│
└── 10. Compare old root vs new root
```

The most important experiment is #9.

Start with:

```text
A
B
C
D
```

calculate:

```text
ROOT1
```

Then change only:

```text
C → C'
```

and calculate:

```text
ROOT2
```

You should get:

```text
ROOT1 != ROOT2
```

And because your `hash32()` has an avalanche mechanism, the difference between the roots should generally be substantial.

That gives you a beautiful progression from your previous labs:

```text
Hash
  ↓
Collision
  ↓
Avalanche
  ↓
Merkle Tree
  ↓
Merkle Proof
  ↓
Blockchain-style data integrity
```

The **next natural step after building the tree** is **Lab 06 — Merkle Proof from Scratch**, where you'll prove that a transaction belongs to the tree using only the transaction, its sibling hashes, and the Merkle root.
