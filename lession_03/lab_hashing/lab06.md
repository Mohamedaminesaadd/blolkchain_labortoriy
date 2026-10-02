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



### the implementation 
Your **idea is on the right track**, but the current `build_tree_vide()` is **not yet correct for building a complete Merkle tree**.

The main conceptual issue is here:

```python
temp = self.root

i = 1

if temp.node_gauche is None:
    temp.node_gauche = TreeMerkleNode()
    temp = temp.node_gauche

if temp.node_droite is None:
    temp.node_droite = TreeMerkleNode()
    temp = temp.node_droite
```

After creating the left child, you immediately move:

```python
temp = temp.node_gauche
```

So when you create `node_droite`, you're actually creating the **right child of the left node**, not the right child of the root.

You want:

```text
              root
             /    \
            /      \
         gauche   droite
```

but your logic starts moving down:

```text
              root
             /
          gauche
             \
            droite
```

### For your Merkle tree

If you have 7 transactions:

```text
A B C D E F G
```

you normally need to make the number of leaves even:

```text
A B C D E F G G
```

Then the tree structure is:

```text
                    ROOT
                  /      \
                H01      H23
               /  \     /  \
             H(A,B) H(C,D) H(E,F) H(G,G)
              / \    / \    / \    / \
             A   B  C   D  E   F  G   G
```

So your instinct to do:

```python
if n % 2 == 1:
    n = n + 1
```

is reasonable **if `n` represents the number of transactions/leaves**.

But `build_tree_vide()` should build the tree **level by level**, rather than following only one path downward.

So: **your overall idea is correct, but the current implementation of the tree construction is not.** The next thing to fix is specifically the construction logic while keeping your current classes and approach.


----------------------------------------------------------------
in what the **merkle tree**
A Merkle Tree (arbre de Merkle) is a data structure used in computer science and cryptography to verify the integrity of large amounts of data efficiently, without needing to compare or download all the data.

It is particularly important in:

- Blockchain and Bitcoin
- Distributed systems
- Peer-to-peer networks
- Git and version control
- Distributed databases
- Data integrity verification

Let's understand it from your Python implementation.

## 1. The fundamental idea

Imagine you have 4 transactions:

```
Transaction A
Transaction B
Transaction C
Transaction D
```

You calculate a hash for each transaction:

\\[ H_A = hash(A) \\]

\\[ H_B = hash(B) \\]

\\[ H_C = hash(C) \\]

\\[ H_D = hash(D) \\]

Then you combine hashes pairwise:

\\[ H\_{AB}=hash(H_A \parallel H_B) \\]

\\[ H\_{CD}=hash(H_C \parallel H_D) \\]

Finally:

\\[ Root=hash(H\_{AB}\parallel H\_{CD}) \\]

[Merkle Tree in Blockchain](https://images.openai.com/static-rsc-4/exu299De2Z3-ma_KHpa5FT_Jl1911KwZAPFhYFoI__Y2xRzh3ZBP9SQcREHOsIalAoxi5gXepR4TPPVv8wPHUJscm44qc91vkWfg5MFmV5J_Jol4dnl7vx6GaFbAx8LKmXoum-j6Kp9QWQhMVdaHDcnNb8vs68fVPn9apYmdF87xZ-YIUTv5wWzMFYzcu1SH?purpose=fullsize)

The final value is called the Merkle Root.

It represents the integrity of all the transactions in the tree.

## 2. Real application: Bitcoin

[Introduction to Bitcoin](https://images.openai.com/static-rsc-4/pFfkpdDFDRhi0-M6GCQ_GN44AoNSBWS3GR1RJmzC1BOBo5hYuCXgQfpwiqFEFme1pYRsObckODYX2liFOO2tT7JOAl1TNRxTYOLYoi8b3NGrHc7qLCnOSJ83GnGb6rjMSf1zB_nqzKhSDWoqbfhEPdW20dHTMWlbgoijD9vk1I1aVqPy0XEYm-YmkMu4C7nV?purpose=fullsize)

In Bitcoin, each block contains transactions.

For example:

```
Block #100
│
├── Transaction A
├── Transaction B
├── Transaction C
├── Transaction D
├── Transaction E
└── Merkle Root
```

The Merkle Root is stored in the block header.

### Why?

Imagine someone modifies a transaction:

```
Original:
Transaction A = Transfer 2 BTC

Modified:
Transaction A = Transfer 20 BTC
```

The transaction hash changes:

\\[ H_A \neq H'\_A \\]

Consequently, its parent hash changes, and this modification propagates toward the root.

```
Before modification:

        ROOT_1
       /      \
     H_AB     H_CD


After modification:

        ROOT_2
       /      \
     H'_AB    H_CD
```

Therefore:

\\[ ROOT_1 \neq ROOT_2 \\]

This allows the system to detect that the data has changed.

## 3. One of the most interesting applications: SPV

Suppose you use a Bitcoin wallet on your phone.

Your phone doesn't necessarily need to download every transaction in every block.

Instead, it can use a Merkle Proof.

For example, you want to verify that transaction C belongs to a particular block.

You only need:

- Hash of transaction C
- Hash of transaction D
- Hash of the A-B subtree
- The Merkle Root from the block header

[Merkle Proofs - Blockchain Academy](https://images.openai.com/static-rsc-4/2pu-GJ5khBD7BCDzQqzxfDoMsSCb1xhwCI9enc1gqsVIOtq5xmNS8i4h0gxgnxX5jlE8fjXcJVM6xXK2PwP09mWri-qkT1458LkeDs_KZ2vU23ZLW5PYBpp-EYOWfeNhbMbGScNUZaGryM4YW55pt8ICE5HVLk5eo-8t_8hSITIq_gmQyW1LIM3gIFrkvZ6X?purpose=fullsize)

You calculate:

\\[ H\_{CD}=hash(H_C\parallel H_D) \\]

Then:

\\[ Root=hash(H\_{AB}\parallel H\_{CD}) \\]

If the calculated root matches the trusted block header's root, the proof establishes that transaction C is included in the committed transaction set, assuming the hash function's security and the header's authenticity.

This is called a Merkle Proof / Proof of Inclusion.

## 4. Other real-world applications

| Application           | Why Merkle Trees are used            |
| --------------------- | ------------------------------------ |
| Blockchain            | Verify transactions                  |
| Git                   | Detect changes in repository objects |
| Distributed databases | Compare data efficiently             |
| P2P networks          | Verify downloaded chunks             |
| File systems          | Detect corrupted files               |
| Software distribution | Verify file integrity                |

For example, in a distributed database, two servers can compare their Merkle Roots.

```
Server A                  Server B

Root = 0x1234             Root = 0x1234
       │                         │
       └───────────┬─────────────┘
                   ▼
              Same hashes
```

If roots differ, the servers can recursively compare subtrees to locate the inconsistent data.

## 5. Why not just hash all transactions together?

Suppose you have 1 million transactions.

With a simple hash of all data, changing one transaction requires processing the entire dataset again to compute the new hash.

With a Merkle Tree, a changed leaf affects only its path to the root.

For a balanced binary tree:

\\[ \text{Number of affected hashes} \approx \log_2(n)+1 \\]

For 1,000,000 transactions:

\\[ \log_2(1,000,000)\approx 20 \\]

So the path contains approximately 21 nodes, including the leaf and root.

This is the main advantage: efficient verification and localized updates.

## 6. What you should understand from your lab

Your lab has three fundamental concepts:

| Component        | Role                                                 |
| ---------------- | ---------------------------------------------------- |
| `hash32(data)`   | Converts data into a 32-bit hash                     |
| `TreeMerkleNode` | Represents a node containing a hash and two children |
| `TreeMerlede`    | Constructs the tree and calculates the root          |

Your next important learning objective is to implement a function that verifies whether a particular transaction belongs to the Merkle Tree without traversing or downloading the entire tree. This is the Merkle Proof algorithm.


------------------------------------------------------------------
Let's forget the code for a moment. I will explain the concept of proving a transaction belongs to a Merkle Tree using a real-world example.

The key question is:

> How can I convince someone that transaction C is inside my Merkle Tree without giving them all the other transactions?

## 1. Imagine a bank with 4 transactions

A bank has a database containing:

```
Transaction A: Mohamed sends 100 DT
Transaction B: Ahmed sends 50 DT
Transaction C: Ali sends 200 DT
Transaction D: Sami sends 30 DT
```

The bank constructs a Merkle Tree:

Merkle Root

## H( H(A,B), H(C,D) )

H(A,B)

Left subtree

H(C,D)

Right subtree

## A

Transaction

## B

Transaction

## C

Transaction

## D

Transaction

The bank publishes the Merkle Root.

Now, Ali wants to prove that his transaction C is included in the bank's transaction set.

## 2. The naive method (without Merkle Proof)

Ali asks the bank:

"Can you prove that transaction C is registered?"

The bank sends:

```
A
B
C
D
```

Ali must receive all transactions and reconstruct the entire tree.

This is inefficient when the bank has millions of transactions.

## 3. The Merkle Proof method

Instead, the bank sends Ali only:

```
1. Transaction C
2. Hash of transaction D
3. Hash of subtree H(A,B)
4. The order of the hashes
```

Why these two hashes?

Because Ali already has C, and these are exactly the missing pieces needed to reconstruct the root.

[Deep dive into the internals of an immutable database, immudb | by Farhan Ali Khan | Medium](https://images.openai.com/static-rsc-4/QClfE9sSgiSiwR3C_Y5OpQGXydSjiobvhtDU_yIhVQBwVqLGOMh2LtlNU0HyCbFdf0IGWKSJDwjJm_nY0HLTwzQte5Zh2l2syZdmomd4Jbtsl6qZs43p1xKYDkzNbbhXPk1GMSJW-MXw2J7QUg3W8mV8h2bzbDILLCFFGRWkQE114D1fZAvZz7aAGn7DfX6o?purpose=fullsize)

Think of it like a puzzle.

Ali has one piece (C), and the bank gives him the other hashes needed to reconstruct the final result.

## 4. How Ali verifies the proof

Suppose the bank gives him:

\\[ H_D = hash(D) \\]

\\[ H\_{AB}=hash(hash(A)\parallel hash(B)) \\]

Ali performs these operations:

Step 1 — Hash his transaction

\\[ h_1=hash(C) \\]

Step 2 — Combine with D

\\[ h_2=hash(h_1\parallel H_D) \\]

Now Ali has reconstructed the hash of the C-D subtree.

Step 3 — Combine with the A-B subtree

\\[ h_3=hash(H\_{AB}\parallel h_2) \\]

He now has a reconstructed root.

Step 4 — Compare

The bank previously published:

\\[ Root\_{\text{trusted}} \\]

Ali calculated:

\\[ Root\_{\text{calculated}}=h_3 \\]

If:

\\[ \boxed{Root\_{\text{calculated}}=Root\_{\text{trusted}}} \\]

then the proof is valid.

Ali has verified that C is included in the data committed to by that root, without downloading A, B, or D themselves.

## 5. What if the bank lies?

Imagine the bank sends:

```
Transaction C = Ali sends 200 DT
```

But Ali receives a modified transaction:

```
Transaction C = Ali sends 2,000 DT
```

The hash changes:

\\[ hash(C)\neq hash(C') \\]

Therefore, the reconstructed root will not match the trusted root.

Original transaction

Proof valid — reconstructed root matches.

Modified transaction

Proof invalid — reconstructed root differs.

One important distinction: a valid proof establishes inclusion relative to a trusted root. It does not independently prove that the bank's transaction is truthful or that the root itself is legitimate.

## 6. Connect this to your Python lab

Your current implementation already has:

```
tree.root.data
```

This is your Merkle Root.

And:

```
tree.leaves[2].data
```

This is the hash of transaction C, assuming index 2 corresponds to C.

Your next task is to implement a function that receives:

```
transaction_Cprooftrusted_root
```

And returns:

```
True   # transaction belongs to the committed treeFalse  # proof is invalid
```

The most important thing to understand is:

Merkle Proof is not about copying the original tree and comparing it with a modified tree. It is about reconstructing the trusted root using only the transaction and a small set of sibling hashes.


Let's forget the code for a moment. I will explain the concept of proving a transaction belongs to a Merkle Tree using a real-world example.

The key question is:

> How can I convince someone that transaction C is inside my Merkle Tree without giving them all the other transactions?

## 1. Imagine a bank with 4 transactions

A bank has a database containing:

```
Transaction A: Mohamed sends 100 DT
Transaction B: Ahmed sends 50 DT
Transaction C: Ali sends 200 DT
Transaction D: Sami sends 30 DT
```

The bank constructs a Merkle Tree:

Merkle Root

## H( H(A,B), H(C,D) )

H(A,B)

Left subtree

H(C,D)

Right subtree

## A

Transaction

## B

Transaction

## C

Transaction

## D

Transaction

The bank publishes the Merkle Root.

Now, Ali wants to prove that his transaction C is included in the bank's transaction set.

## 2. The naive method (without Merkle Proof)

Ali asks the bank:

"Can you prove that transaction C is registered?"

The bank sends:

```
A
B
C
D
```

Ali must receive all transactions and reconstruct the entire tree.

This is inefficient when the bank has millions of transactions.

## 3. The Merkle Proof method

Instead, the bank sends Ali only:

```
1. Transaction C
2. Hash of transaction D
3. Hash of subtree H(A,B)
4. The order of the hashes
```

Why these two hashes?

Because Ali already has C, and these are exactly the missing pieces needed to reconstruct the root.

[Deep dive into the internals of an immutable database, immudb | by Farhan Ali Khan | Medium](https://images.openai.com/static-rsc-4/QClfE9sSgiSiwR3C_Y5OpQGXydSjiobvhtDU_yIhVQBwVqLGOMh2LtlNU0HyCbFdf0IGWKSJDwjJm_nY0HLTwzQte5Zh2l2syZdmomd4Jbtsl6qZs43p1xKYDkzNbbhXPk1GMSJW-MXw2J7QUg3W8mV8h2bzbDILLCFFGRWkQE114D1fZAvZz7aAGn7DfX6o?purpose=fullsize)

Think of it like a puzzle.

Ali has one piece (C), and the bank gives him the other hashes needed to reconstruct the final result.

## 4. How Ali verifies the proof

Suppose the bank gives him:

\\[ H_D = hash(D) \\]

\\[ H\_{AB}=hash(hash(A)\parallel hash(B)) \\]

Ali performs these operations:

Step 1 — Hash his transaction

\\[ h_1=hash(C) \\]

Step 2 — Combine with D

\\[ h_2=hash(h_1\parallel H_D) \\]

Now Ali has reconstructed the hash of the C-D subtree.

Step 3 — Combine with the A-B subtree

\\[ h_3=hash(H\_{AB}\parallel h_2) \\]

He now has a reconstructed root.

Step 4 — Compare

The bank previously published:

\\[ Root\_{\text{trusted}} \\]

Ali calculated:

\\[ Root\_{\text{calculated}}=h_3 \\]

If:

\\[ \boxed{Root\_{\text{calculated}}=Root\_{\text{trusted}}} \\]

then the proof is valid.

Ali has verified that C is included in the data committed to by that root, without downloading A, B, or D themselves.

## 5. What if the bank lies?

Imagine the bank sends:

```
Transaction C = Ali sends 200 DT
```

But Ali receives a modified transaction:

```
Transaction C = Ali sends 2,000 DT
```

The hash changes:

\\[ hash(C)\neq hash(C') \\]

Therefore, the reconstructed root will not match the trusted root.

Original transaction

Proof valid — reconstructed root matches.

Modified transaction

Proof invalid — reconstructed root differs.

One important distinction: a valid proof establishes inclusion relative to a trusted root. It does not independently prove that the bank's transaction is truthful or that the root itself is legitimate.

## 6. Connect this to your Python lab

Your current implementation already has:

```
tree.root.data
```

This is your Merkle Root.

And:

```
tree.leaves[2].data
```

This is the hash of transaction C, assuming index 2 corresponds to C.

Your next task is to implement a function that receives:

```
transaction_Cprooftrusted_root
```

And returns:

```
True   # transaction belongs to the committed treeFalse  # proof is invalid
```

The most important thing to understand is:

Merkle Proof is not about copying the original tree and comparing it with a modified tree. It is about reconstructing the trusted root using only the transaction and a small set of sibling hashes.


Let's build a small practical example with 4 transactions. You will see how to prove that transaction C belongs to the Merkle Tree without sending the entire tree.

## Step 1: Imagine these transactions

```
transactions = [    b"Transaction A",    b"Transaction B",    b"Transaction C",    b"Transaction D",]
```

The Merkle Tree looks like this:

ROOT

H(H(AB) + H(CD))

H(AB)

H(CD)

A

B

C

D

Suppose someone wants to prove that Transaction C is inside this tree.

They do not need to send A, B, and D themselves. They only need:

- Transaction C
- Hash of D
- Hash of the subtree AB
- The trusted Merkle Root

## Step 2: Implement the proof

Use your existing `hash32()` function.

```
def hash_pair(left, right):    data = (        left.to_bytes(4, "big") +        right.to_bytes(4, "big")    )    return hash32(data)
```

### Generate a proof for C

```
def generate_proof(transactions, index):    level = [hash32(tx) for tx in transactions]    proof = []    while len(level) > 1:        # If odd number of nodes, duplicate last        if len(level) % 2 != 0:            level.append(level[-1])        sibling_index = index ^ 1        sibling_hash = level[sibling_index]        sibling_is_left = sibling_index < index        proof.append((sibling_hash, sibling_is_left))        # Build next level        next_level = []        for i in range(0, len(level), 2):            parent = hash_pair(level[i], level[i + 1])            next_level.append(parent)        level = next_level        index //= 2    return proof
```

### Verify the proof

```
def verify_proof(transaction, proof, trusted_root):    current_hash = hash32(transaction)    for sibling_hash, sibling_is_left in proof:        if sibling_is_left:            current_hash = hash_pair(                sibling_hash,                current_hash            )        else:            current_hash = hash_pair(                current_hash,                sibling_hash            )    return current_hash == trusted_root
```

## Step 3: Test the complete example

```
transactions = [    b"Transaction A",    b"Transaction B",    b"Transaction C",    b"Transaction D",]# Build the tree using your classtree = TreeMerlede(transactions)tree.fill_tree()# Save trusted roottrusted_root = tree.root.data# Generate proof for C (index 2)proof = generate_proof(transactions, 2)# Verify Cresult = verify_proof(    b"Transaction C",    proof,    trusted_root)print("Valid proof:", result)
```

Expected result:

```
Valid proof: True
```

Now modify C:

```
result = verify_proof(    b"Transaction C modified",    proof,    trusted_root)print("Valid proof:", result)
```

Expected result:

```
Valid proof: False
```

## What did we prove?

| Situation                                  | Result |
| ------------------------------------------ | ------ |
| Original C + correct proof + trusted root  | True   |
| Modified C + original proof + trusted root | False  |
| Original C + incorrect sibling hash        | False  |

The key idea: the verifier reconstructs the Merkle Root from C and its sibling hashes. If it matches the trusted root, C is included in the committed tree.

This is called a Merkle Inclusion Proof, not Proof of Work. Your custom 32-bit hash is suitable for learning, but real systems use cryptographic hashes such as SHA-256.