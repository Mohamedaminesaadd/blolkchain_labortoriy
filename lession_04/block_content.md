If you mean **“What is a blockchain block?”**, think of it as a **container of transactions** that is linked to the previous container.

### 1. Blockchain

A blockchain is a chain of blocks:

```text
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   Block 100 │ ───► │   Block 101 │ ───► │   Block 102 │
│             │      │             │      │             │
│ Transactions│      │ Transactions│      │ Transactions│
│ PreviousHash│      │ PreviousHash│      │ PreviousHash│
│ Hash        │      │ Hash        │      │ Hash        │
└─────────────┘      └─────────────┘      └─────────────┘
```

Each block contains information about the **previous block**.

### 2. What is inside a Bitcoin block?

Simplified:

```text
BLOCK
│
├── BLOCK HEADER
│   ├── Version
│   ├── Previous Block Hash
│   ├── Merkle Root
│   ├── Timestamp
│   ├── Difficulty Target
│   └── Nonce
│
└── TRANSACTIONS
    ├── Transaction 1
    ├── Transaction 2
    ├── Transaction 3
    └── ...
```

The **header** is especially important for Proof of Work.

Bitcoin calculates:

```text
SHA256(
    SHA256(
        block_header
    )
)
```

This is called **double SHA-256**.

The miner changes the `nonce` until the resulting hash satisfies the difficulty target:

```text
nonce = 0
    ↓
SHA256(SHA256(header))
    ↓
doesn't satisfy target ❌

nonce = 1
    ↓
SHA256(SHA256(header))
    ↓
doesn't satisfy target ❌

...

nonce = 83947291
    ↓
SHA256(SHA256(header))
    ↓
satisfies target ✅
```

Then the block can be proposed to the Bitcoin network.

### 3. Why does the block have `Previous Block Hash`?

This creates the chain:

```text
Block 100
hash = ABC123
       │
       ▼
Block 101
previous_hash = ABC123
hash = DEF456
       │
       ▼
Block 102
previous_hash = DEF456
hash = XYZ789
```

If someone modifies a transaction in Block 100:

```text
Transaction changed
       ↓
Merkle Root changes
       ↓
Block 100 hash changes
       ↓
Block 101's previous_hash becomes invalid
       ↓
Block 102 becomes invalid
       ↓
...
```

That's one of the fundamental ideas behind the Bitcoin blockchain.

### 4. You can see a real block with your Bitcoin Core

Once your node is synchronized, try:

```bash
bitcoin-cli getblockchaininfo
```

Get the current block hash:

```bash
bitcoin-cli getbestblockhash
```

Then:

```bash
bitcoin-cli getblock $(bitcoin-cli getbestblockhash)
```

You'll see a real Bitcoin block containing fields such as:

```text
"hash"
"height"
"version"
"previousblockhash"
"merkleroot"
"time"
"bits"
"nonce"
"nTx"
"tx"
```

**This is a very important lab for you:** next we can take one real block from your Bitcoin Core and examine **every field one by one**, then manually calculate its **double-SHA-256 Proof-of-Work** in Python.

![Bitcoin Blockchain](https://marcsteiner-consulting.ch/wp-content/uploads/2020/01/bitcoin_block_overview-768x392.jpeg)

![Bitcoin Block Structure](https://www.researchgate.net/profile/Suhyeon-Lee-3/publication/343236233/figure/fig1/AS:917901632602113@1595856211342/Bitcoin-block-structure.ppm)



Yes. An **orphan block** is a block that was validly mined but **does not become part of the blockchain's accepted chain**.

### Simple example

Imagine the blockchain currently ends at:

```text
Block 100
   │
   └── ?
```

Two miners find a valid block almost simultaneously:

```text
             ┌── Block 101A
Block 100 ───┤
             └── Block 101B
```

Both blocks can be valid.

This creates a temporary **fork**:

```text
              ┌── 101A ── 102A
Block 100 ────┤
              └── 101B
```

Suppose miners eventually build on `101A`:

```text
100 → 101A → 102A
      ↑
   accepted
```

Then `101B` is no longer part of the best chain.

### What happens to 101B?

Historically, Bitcoin often called this an **orphan block**.

More precisely, modern Bitcoin terminology distinguishes:

- **Stale block** → a valid block that loses a race and isn't in the active chain.
- **Orphan block** → technically, a block whose **parent is unknown** to the node.

So when you're learning Bitcoin, if two miners find competing blocks at the same height, it's better to call the losing one a **stale block**.

### Why does this happen?

Because the Bitcoin network isn't instantaneous.

Imagine:

```text
Miner A                 Miner B
   │                       │
   │ finds 101A            │
   │                       │
   ├─────── network ───────┤
   │                       │
   │                       │ finds 101B
   │                       │
   ▼                       ▼
101A                    101B
```

Both miners may have been working on:

```text
Block 100
```

and both independently find valid PoW.

The network temporarily has:

```text
100
├── 101A
└── 101B
```

### How PoW resolves it

Mining continues:

```text
100
├── 101A ─── 102A
│
└── 101B
```

Now the chain with more **cumulative proof of work** wins:

```text
100 → 101A → 102A
       ↑
   active chain
```

`101B` becomes stale.

### Very important

An orphan/stale block is **not necessarily a malicious block**.

It can be:

```text
Valid transactions
      +
Valid PoW
      +
Valid block
      ↓
Lost the race
      ↓
Stale block
```

That's one of the reasons Bitcoin's consensus mechanism needs both:

**PoW + network propagation + chain selection.**

For your CUDA lab, you can actually simulate this: run **two miners simultaneously**, let both search for a valid nonce, and observe how two valid blocks at the same height create a temporary fork and how the next block determines which branch survives.

In Bitcoin, **Coinbase** has two different meanings, which can be confusing:

1. **coinbase transaction** → a special Bitcoin transaction inside every mined block.
2. **Coinbase** → the cryptocurrency exchange company.

For your PoW/Bitcoin lab, you mean the **coinbase transaction**.

### What is the coinbase transaction?

It is the transaction that allows the **miner who successfully mines a block to receive the block reward**.

A normal Bitcoin transaction looks like:

```text
Alice
  │
  │  0.5 BTC
  ▼
Bob
```

It spends previous transaction outputs.

A coinbase transaction is different:

```text
Bitcoin network
      │
      │ "Miner successfully mined block"
      ▼
Coinbase transaction
      │
      ▼
Miner's address
      │
      └── block reward + transaction fees
```

There is **no normal previous UTXO being spent**.

### Example

Suppose the block reward is:

```text
Subsidy = 3.125 BTC
Fees    = 0.20 BTC
```

The miner can create a coinbase transaction paying:

```text
Miner → 3.325 BTC
```

So:

\[
\boxed{\text{Miner reward} =
\text{Block subsidy} + \text{Transaction fees}}
\]

### Where is it in the block?

A Bitcoin block contains a list of transactions:

```text
Block
│
├── Coinbase transaction  ← first transaction
│
├── Transaction 1
├── Transaction 2
├── Transaction 3
└── ...
```

**The coinbase transaction must be the first transaction in the block.**

This is important because its transaction ID contributes to the **Merkle root**:

```text
                    Merkle Root
                       ↑
              ┌────────┴────────┐
              │                 │
        Hash(Coinbase)      Hash(Tx1)
              │                 │
              └──────┬──────────┘
                     ...
```

And the Merkle root goes into the block header:

```text
Block Header
├── Version
├── Previous Block Hash
├── Merkle Root       ← influenced by coinbase
├── Timestamp
├── nBits
└── Nonce
```

Therefore, when a miner changes something in the coinbase transaction, the **Merkle root changes**, which changes the block header, meaning the miner has to perform PoW again.

### What makes the coinbase transaction special?

A normal transaction:

```text
Input
  ↓
Previous UTXO
  ↓
Output
```

Coinbase:

```text
No normal input
      ↓
Block subsidy + fees
      ↓
Miner's output
```

The input contains special data called the **coinbase scriptSig**. Miners can put arbitrary data there subject to protocol rules.

For example, historically miners have used this space to include messages or mining-pool information.

### Important security rule: 100 blocks

Coinbase rewards have a **maturity period of 100 blocks** before they can be spent.

So:

```text
Miner mines Block 900
       ↓
receives coinbase reward
       ↓
cannot spend it immediately
       ↓
wait 100 blocks
       ↓
reward becomes spendable
```

This helps reduce problems caused by reorganizations of the chain.

### How it connects to your PoW lab

Your future Bitcoin miner will conceptually do:

```text
                 Transactions
                       │
                       ▼
             Create coinbase TX
                       │
                       ▼
              Build transaction list
                       │
                       ▼
                 Merkle Root
                       │
                       ▼
              Build Block Header
                       │
                       ▼
              ┌─────────────────┐
              │      CUDA GPU   │
              │                 │
              │ nonce 0         │
              │ nonce 1         │
              │ nonce 2         │
              │ ...             │
              │ nonce millions  │
              └────────┬────────┘
                       │
                       ▼
                 Double SHA-256
                       │
                       ▼
                hash < target ?
                    /       \
                  NO         YES
                  │           │
               continue     BLOCK
                              │
                              ▼
                       Miner gets reward
```

So **coinbase is the bridge between PoW and the miner's economic reward**: the miner proves work, produces a valid block, and the block's coinbase transaction creates the reward according to Bitcoin's rules.