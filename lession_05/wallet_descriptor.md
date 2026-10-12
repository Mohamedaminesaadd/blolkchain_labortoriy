# Lab 13 — Bitcoin Wallet Key Management

Objective: Understand how Bitcoin wallets manage private keys, derive public keys and addresses, and use seed phrases and descriptors to organize access to funds.

In this lab, we will connect the theory to your Bitcoin Core 31.1 `regtest` environment on Ubuntu. The goal is to understand what happens inside a wallet, not to implement cryptography from scratch.

## 1. The big picture

A Bitcoin wallet is not a container that physically stores bitcoins. The blockchain records transaction outputs, while the wallet manages the keys and information needed to receive and spend those outputs.

A simplified wallet key-management flow looks like this:

```
                 Seed / Root Secret
                         |
                         v
                 HD Key Derivation
                         |
              +----------+----------+
              |                     |
              v                     v
         Private Key A         Private Key B
              |                     |
              v                     v
          Public Key A          Public Key B
              |                     |
              v                     v
           Address A              Address B
```

This diagram represents a hierarchical deterministic (HD) wallet. Older or non-HD wallets may manage keys differently.

The key concepts to understand are:

- Private key: Secret information used to authorize spending.
- Public key: Derived from a private key and used in signature verification or spending conditions.
- HD wallet: A wallet that derives many keys from a common root.
- Derivation: The process of generating child keys from a parent key.
- Descriptor: A description of how Bitcoin output scripts and addresses are generated.
- Seed: Secret starting material used to recover or derive wallet keys, depending on the wallet design.

## 2. Private keys

A private key is a secret number used to authorize spending bitcoin under the corresponding spending conditions.

Bitcoin uses the elliptic curve `secp256k1`. A private key is a valid scalar in the range:

\\[ 1 \leq d < n \\]

where \\(n\\) is the order of the elliptic curve's base point.

The private key \\(d\\) is used to derive a public key \\(P\\):

\\[ P=dG \\]

Here, \\(G\\) is the curve's predefined generator point. This operation is elliptic-curve scalar multiplication.

### Example

Suppose Amine's wallet controls a UTXO worth 5 BTC. To spend it, his wallet must produce the required authorization, typically a digital signature, using the relevant private key.

```
Amine's wallet
      |
      v
Private key (secret)
      |
      v
Creates digital signature
      |
      v
Bitcoin nodes verify the signature
      |
      v
Transaction can be accepted if all
consensus and policy requirements hold
```

The private key itself is not sent to the network. The signature is included in the transaction's unlocking data.

Important: Possessing a private key does not mean that the key automatically controls every UTXO associated with an address. The UTXO's locking conditions must correspond to the key or script information you can satisfy.

### What you should remember

- Never reveal a real wallet's private key.
- A private key is not the same as a wallet password.
- A wallet password may encrypt stored wallet data; it is not necessarily the cryptographic key used to spend bitcoin.
- Losing the only usable copy of the required keys can mean permanently losing access to the associated funds.

## 3. Public keys

A public key is mathematically derived from a private key. It can be shared without revealing the private key, assuming the cryptographic system remains secure.

For the common elliptic-curve relationship:

\\[ P=dG \\]

- \\(d\\) is the private key.
- \\(G\\) is the generator point.
- \\(P\\) is the public key.

The operation is easy to perform in the forward direction but computationally infeasible to reverse with known practical methods: deriving the private key from the public key should be infeasible.

### How is a public key used?

In a common single-key spending arrangement:

1. A wallet derives a public key from its private key.
2. The public key, or a hash of it, contributes to the spending conditions.
3. When spending, the wallet generates a digital signature.
4. Bitcoin nodes verify the signature using the relevant public key.

For Legacy P2PKH, the locking script uses a hash of the public key. For native SegWit P2WPKH, the output also commits to a public-key hash, but uses a witness program.

Other output types, such as Taproot, have different spending constructions.

### Private key versus public key

| Property                                              | Private key                               | Public key                                                 |
| ----------------------------------------------------- | ----------------------------------------- | ---------------------------------------------------------- |
| Secret?                                               | Yes                                       | No                                                         |
| Derived from                                          | Random generation or a derivation process | Private key                                                |
| Main purpose                                          | Signing and authorization                 | Signature verification and spending conditions             |
| Safe to share?                                        | No                                        | Generally yes                                              |
| Can it be used to derive the private key in practice? | Not applicable                            | Not feasibly, with current practical cryptographic methods |

## 4. HD wallets — Hierarchical Deterministic Wallets

An HD wallet can generate many related keys from a common root secret.

Instead of generating and backing up every private key individually, an HD wallet can derive a tree of keys using a defined derivation scheme.

The widely used Bitcoin HD-wallet standard is BIP32.

### Why are HD wallets useful?

Imagine Amine generates a new receiving address every time someone pays him.

Without an HD structure, backing up each independently generated key could become difficult.

With an HD wallet, many keys can be derived from a root, allowing the wallet to recover its derived keys from the appropriate backup material.

```
                 HD Wallet Root
                       |
             +---------+---------+
             |                   |
          Branch 0            Branch 1
          Receiving           Change
             |                   |
        +----+----+         +----+----+
        |         |         |         |
      Key 0     Key 1     Key 0     Key 1
        |         |         |         |
    Address A Address B  Change A  Change B
```

This is a conceptual example. Real wallets use defined derivation paths and may have multiple accounts, branches, and address types.

### Common derivation path

A path such as:

```
m/84'/0'/0'/0/0
```

can be interpreted as follows:

- `m`: the master node.
- `84'`: the purpose associated with native SegWit P2WPKH under BIP84.
- `0'`: the Bitcoin mainnet coin type.
- `0'`: account zero.
- `0`: the external receiving branch.
- `0`: the first child address index.

The apostrophe (`'`) indicates hardened derivation.

For the equivalent common regtest wallet structure, the coin-type component can differ because regtest uses test-network conventions. Do not assume every wallet uses this exact path.

### Receiving and change branches

Many HD wallets distinguish between:

- External branch: Generates addresses intended to receive payments.
- Internal branch: Generates change addresses when spending.

For example, if Amine spends 2 BTC from a 5 BTC UTXO and pays Sara 2 BTC plus a 0.001 BTC fee, the wallet may create a change output of 2.999 BTC back to Amine's wallet.

That change output can use a different derived address from the one Amine gave to other people.

The purpose is to manage change and receiving addresses systematically, not to create new bitcoins.

## 5. Key derivation

Key derivation is the process of generating child keys from a parent key using defined cryptographic operations.

BIP32 defines how an HD wallet derives child extended keys. An extended key includes key material and a chain code, which supports further derivation.

There are two important types of derivation.

### 5.1. Normal (non-hardened) derivation

Non-hardened derivation allows a child public key to be derived from the parent extended public key, without knowing the parent's private key.

This is useful for systems that need to generate or monitor addresses without being able to spend funds.

For example, a payment-monitoring application could use an extended public key to derive receiving addresses while keeping private keys offline.

However, this must be designed carefully: a leaked parent extended public key combined with a corresponding non-hardened child private key can expose the parent private key under the BIP32 derivation construction.

### 5.2. Hardened derivation

Hardened derivation requires private key material from the parent extended private key. It cannot be performed using only the parent extended public key.

Hardened derivation is commonly used at account and purpose boundaries to isolate branches of the key hierarchy.

### Comparison

| Property                                              | Non-hardened                          | Hardened                                   |
| ----------------------------------------------------- | ------------------------------------- | ------------------------------------------ |
| Can derive using parent extended public key?          | Yes                                   | No                                         |
| Requires parent private key?                          | Not necessarily                       | Yes                                        |
| Can derive child public keys from public information? | Yes                                   | No                                         |
| Common use                                            | Receiving and change address branches | Purpose, coin type, and account boundaries |

### Why derivation matters in your app

Your Streamlit application can request a new address through Bitcoin Core:

```
bitcoin-cli -regtest -rpcwallet=amine getnewaddress
```

Bitcoin Core manages the relevant key derivation internally when the wallet supports it.

You do not need to calculate child private keys or implement BIP32 yourself.

## 6. Seed concepts

A seed is secret starting material used by a wallet to create or recover its key hierarchy.

It is important to distinguish between a seed, a mnemonic phrase, and a private key.

### 6.1. Seed

In an HD wallet, a seed is used to generate the master extended private key and associated chain code according to BIP32.

The seed is not itself a Bitcoin address and is not necessarily identical to any individual private key.

### 6.2. Mnemonic phrase

BIP39 defines a method for representing entropy as a human-readable sequence of words, commonly 12 or 24 words.

The mnemonic and an optional passphrase are processed using a defined key-stretching procedure to produce seed material.

Conceptually:

```
Random entropy
      |
      v
BIP39 mnemonic phrase
      |
      | Optional passphrase
      v
BIP39 seed
      |
      v
BIP32 master key
      |
      v
Child keys and addresses
```

Not every Bitcoin wallet uses BIP39. Some wallet software uses other backup and key-generation mechanisms, so you must know which scheme your wallet supports before attempting recovery.

### 6.3. Why is the seed important?

Suppose Amine's computer breaks.

If he has a valid backup that contains the necessary recovery material, he may be able to restore his wallet on another compatible device.

However, successful recovery depends on more than just entering words:

- The correct mnemonic standard must be used.
- Any required passphrase must be known.
- The correct derivation paths and wallet type must be used.
- The wallet's scripts and other relevant information may need to be restored or rediscovered.

A seed phrase is extremely sensitive. Anyone who obtains sufficient recovery material may be able to control the associated funds. Never upload a real seed phrase to a website, paste it into an online service, or commit it to Git.

## 7. Descriptors — Describing how addresses are generated

A Bitcoin output descriptor is a structured expression that describes a set of output scripts or the conditions for generating them.

Descriptors make wallet behavior easier to represent and reproduce. They can describe single-key outputs, multisignature outputs, SegWit outputs, Taproot outputs, and HD derivation patterns.

Examples of descriptor expressions include:

```
pkh(KEY)
wpkh(KEY)
sh(wpkh(KEY))
tr(KEY)
```

These are schematic examples; `KEY` is a placeholder, not a literal key accepted as a complete descriptor.

Their meanings are:

- `pkh(...)`: Pay to public-key hash, commonly associated with Legacy P2PKH.
- `wpkh(...)`: Native SegWit public-key hash, commonly associated with P2WPKH.
- `sh(wpkh(...))`: P2SH-wrapped SegWit.
- `tr(...)`: Taproot output construction.

An HD descriptor can also contain a derivation path and a wildcard to describe a range of addresses.

### Why are descriptors useful?

Suppose Amine's wallet generates hundreds of receiving addresses.

Rather than listing every address separately, a descriptor can describe the rule used to derive them. Wallet software can then generate or recognize addresses from that rule.

Descriptors can also be used in watch-only wallets, provided the available descriptor information is sufficient for the intended monitoring task.

### Inspect descriptors in Bitcoin Core

In your regtest lab, generate an address:

```
bitcoin-cli -regtest -rpcwallet=amine getnewaddress
```

Copy the address and inspect it:

```
bitcoin-cli -regtest -rpcwallet=amine getaddressinfo "YOUR_ADDRESS"
```

Look for the `desc` field when present. Bitcoin Core may return a descriptor representing the output conditions associated with that address.

To inspect the wallet's available descriptors, you can also try:

```
bitcoin-cli -regtest -rpcwallet=amine listdescriptors
```

Availability and behavior depend on the wallet type and its configuration. Do not share descriptors containing private key material, such as those marked with `prv`, or other sensitive wallet information.

## 8. How all six concepts fit together

Let's connect the concepts using Amine's wallet.

Amine wants to receive bitcoin from Sara, then spend some of it later.

1. Seed: The wallet's recovery material enables reconstruction of its key hierarchy, if it uses a compatible seed-based scheme.
2. HD wallet: The wallet derives multiple keys from its root.
3. Derivation: A specific derivation path selects a child key.
4. Private key: The relevant private key authorizes spending under the associated conditions.
5. Public key: The wallet derives the public key used by the relevant output construction.
6. Descriptor: The descriptor describes how the output script and associated addresses are generated.

The resulting address is shared with Sara. When Sara sends bitcoin to that address, the transaction creates a UTXO with the corresponding locking conditions. Later, Amine's wallet uses the appropriate key or script information to spend it.

Remember that descriptors describe output conditions, while seeds and private keys are sensitive key material. They have different purposes.

## 9. Practical exercises for your Bitcoin Core lab

Use your existing `regtest` wallet. These exercises inspect wallet information without exposing private keys.

### Exercise 1 — Inspect wallet metadata

```
bitcoin-cli -regtest -rpcwallet=amine getwalletinfo
```

Observe fields such as wallet name, wallet format, balance, and keypool information, depending on the wallet type.

### Exercise 2 — Generate and inspect an address

```
bitcoin-cli -regtest -rpcwallet=amine getnewaddress
```

Copy the result and run:

```
bitcoin-cli -regtest -rpcwallet=amine getaddressinfo "YOUR_ADDRESS"
```

Identify the address, script, ownership information, and descriptor if present.

### Exercise 3 — Inspect available descriptors

```
bitcoin-cli -regtest -rpcwallet=amine listdescriptors
```

Look at the descriptor expressions and determine which output type they describe. Treat the output as sensitive if it contains private key material.

### Exercise 4 — Inspect public keys when available

Run `getaddressinfo` again and look for `pubkey`. Some address types do not expose a conventional public key in this field.

Do not export or print private keys for this exercise.

## 10. Knowledge check

Try answering these questions without looking back at the explanations.

1. Why must a private key remain secret, while a public key can generally be shared?
2. What problem do HD wallets solve compared with managing many unrelated private keys?
3. What is the difference between a normal child-key derivation and a hardened derivation?
4. Is a BIP39 mnemonic phrase the same thing as a private key?
5. What does a Bitcoin output descriptor describe?
6. Why is a descriptor containing private key material sensitive?
7. If Amine loses his computer but has a valid backup, what additional information might he need to restore his wallet correctly?

Lab 13 completion goal: You should be able to explain the difference between key material, key derivation, recovery information, and output descriptors—and know how to inspect your Bitcoin Core wallet without exposing its secrets.
----------------------------------------------------------------
# Understanding Omar's Bitcoin Wallet Descriptors

This JSON shows the output of Bitcoin Core's `listdescriptors` command for Omar's wallet. It tells us how the wallet generates and tracks different types of Bitcoin addresses.

The most important idea: Omar does not need to store 1,000 independent private keys just to manage 1,000 receiving addresses. His wallet can use hierarchical key derivation and descriptors to describe entire ranges of addresses.

Your JSON contains 8 descriptors, representing four address types, each with an external branch and an internal branch.

## 1. Understand the overall structure

Your wallet has these four address-generation schemes:

| Descriptor expression | Address type        | Mainnet prefix | Typical regtest prefix |
| --------------------- | ------------------- | -------------- | ---------------------- |
| `pkh(...)`            | Legacy P2PKH        | `1...`         | `m...` or `n...`       |
| `sh(wpkh(...))`       | P2SH-wrapped SegWit | `3...`         | `2...`                 |
| `tr(...)`             | Taproot             | `bc1p...`      | `bcrt1p...`            |
| `wpkh(...)`           | Native SegWit       | `bc1q...`      | `bcrt1q...`            |

Each scheme has two branches:

- `/0/*` — external branch, typically used to generate receiving addresses.
- `/1/*` — internal branch, typically used to generate change addresses when spending.

The `*` is a wildcard: it represents a child index that can vary, such as `0`, `1`, `2`, and so on.

Your wallet therefore has four address-generation schemes, each with two branches, giving eight descriptors.

## 2. Decode one descriptor step by step

Let's take the first descriptor:

```
pkh([d09100b8/44h/1h/0h]tpub.../0/*)#dfx8xl60
```

We can divide it into five parts:

```
pkh(
    [d09100b8/44h/1h/0h]
    tpub...
    /0/*
)
#dfx8xl60
```

### Part A — `pkh(...)`

This tells Bitcoin Core which type of output script to generate.

`pkh` means Pay to Public Key Hash (P2PKH), the traditional Legacy address format.

For example, the wallet derives a child public key, hashes it, and encodes the corresponding payment destination as a Legacy address.

### Part B — `[d09100b8/44h/1h/0h]`

This is the origin information.

- `d09100b8` is the master key fingerprint used to identify the key's origin.
- `44h` indicates hardened purpose 44, associated with the traditional BIP44 derivation scheme.
- `1h` is the hardened coin-type component for Bitcoin test networks.
- `0h` indicates account zero.

The `h` suffix means hardened derivation; it is equivalent to an apostrophe in paths such as `44'`.

### Part C — `tpub...`

This is an extended public key, commonly used on Bitcoin test networks.

It contains public key material and a chain code used for deriving child public keys.

Important: An extended public key is not a private key. It cannot independently sign transactions. However, it can reveal many derived addresses and transaction relationships, so it should still be treated as privacy-sensitive information.

### Part D — `/0/*`

This specifies the remaining derivation path:

- `/0/` selects the external branch.
- `*` means the child index varies.

Conceptually, the descriptor can generate addresses at paths like:

```
m/44'/1'/0'/0/0
m/44'/1'/0'/0/1
m/44'/1'/0'/0/2
...
```

The paths above illustrate the derivation structure. The `m` at the start denotes the master node in the complete path, not a literal part of the descriptor.

### Part E — `#dfx8xl60`

This is the descriptor checksum.

It helps detect accidental changes or typing errors in the descriptor. It is not a digital signature, a secret, or proof that the descriptor is trustworthy.

## 3. Understand every JSON field

Each descriptor object contains metadata that tells Bitcoin Core how to use and track that descriptor.

### `wallet_name`

```
"wallet_name": "omar"
```

This identifies the wallet whose descriptors are being listed: Omar's wallet.

### `timestamp`

```
"timestamp": 1791528858
```

This is a Unix timestamp associated with the descriptor's creation or import time. Bitcoin Core uses timestamp information when determining how far back to scan for relevant transactions.

It is not the timestamp of a transaction or a block.

### `active`

```
"active": true
```

The descriptor is active for its assigned purpose in the wallet. For example, an active external descriptor can be used to generate receiving addresses.

### `internal`

```
"internal": false
```

This identifies the branch's purpose:

- `false`: external branch, generally used for receiving addresses.
- `true`: internal branch, generally used for change addresses.

Notice that every external descriptor in your JSON has a corresponding internal descriptor.

### `range`

```
"range": [0, 999]
```

This specifies the currently tracked derivation-index range for the descriptor.

In this example, the range runs from index `0` through index `999`, inclusive. That represents 1,000 possible child indexes.

Your native SegWit external descriptor has:

```
"range": [0, 1002]
```

That range covers indexes `0` through `1002`, inclusive: 1,003 indexes.

A range does not mean that all these addresses have received bitcoin, nor that all have been used.

### `next` and `next_index`

Your native SegWit external descriptor contains:

```
"next": 4,
"next_index": 4
```

These fields identify the next child index tracked for address generation by this descriptor in the returned wallet metadata.

The practical interpretation is that index `4` is the next index to consider for address generation. It does not mean that Omar has four BTC or that four transactions have been confirmed.

For example, a derivation sequence could look like this:

```
External branch: /0/*

Index 0  -> Address 0
Index 1  -> Address 1
Index 2  -> Address 2
Index 3  -> Address 3
Index 4  -> Next index
```

The exact history of address use cannot be established from `next` alone. The wallet's actual address and transaction records provide more context.

## 4. Why does Omar's wallet have four address types?

Your wallet has descriptors for four common Bitcoin output types.

### 4.1. Legacy — `pkh(...)`

You have two descriptors:

```
pkh(.../0/*)    External receiving branch
pkh(.../1/*)    Internal change branch
```

These describe traditional P2PKH outputs.

### 4.2. Wrapped SegWit — `sh(wpkh(...))`

```
sh(wpkh(.../0/*))    External receiving branch
sh(wpkh(.../1/*))    Internal change branch
```

These describe P2SH-wrapped SegWit outputs. They combine a P2SH wrapper with a SegWit v0 public-key-hash witness program.

### 4.3. Taproot — `tr(...)`

```
tr(.../0/*)    External receiving branch
tr(.../1/*)    Internal change branch
```

These describe Taproot outputs. The `tr` expression creates Taproot output scripts using the derived key and the applicable descriptor construction.

### 4.4. Native SegWit — `wpkh(...)`

```
wpkh(.../0/*)    External receiving branch
wpkh(.../1/*)    Internal change branch
```

These describe native SegWit P2WPKH outputs, commonly represented by Bech32 addresses.

Your external Native SegWit descriptor has `next: 4`, while its internal descriptor has `next: 0`. That means the tracked address-generation positions differ between the two branches; it does not indicate a balance difference.

## 5. What does `tpub` tell us?

The extended keys in your descriptors begin with `tpub`, which is commonly associated with test-network extended public keys.

Your paths also use `/1h/`, the test-network coin-type component.

Together, these are consistent with a wallet configured for a Bitcoin test network, such as your regtest lab.

However, `tpub` alone does not prove that the node is running regtest. Test networks share some extended-key conventions, so you should verify the active network with:

```
bitcoin-cli -regtest getblockchaininfo
```

## 6. How to inspect Omar's wallet yourself

Run these commands:

```
# Inspect general wallet information
bitcoin-cli -regtest -rpcwallet=omar getwalletinfo
```

```
# List the descriptors
bitcoin-cli -regtest -rpcwallet=omar listdescriptors
```

```
# Generate a new receiving address
bitcoin-cli -regtest -rpcwallet=omar getnewaddress
```

```
# Inspect a particular address
bitcoin-cli -regtest -rpcwallet=omar getaddressinfo "YOUR_ADDRESS"
```

These commands help you connect the descriptor definitions with the addresses the wallet actually generates.

## 7. Final mental model

Think of the descriptor as a recipe for generating Bitcoin payment destinations.

```
Extended public key + derivation path
                  |
                  v
          Child public keys
                  |
                  v
        Descriptor output type
                  |
                  v
             Addresses
                  |
                  v
      Transactions and UTXOs
```

The wallet uses its corresponding private key material to authorize spending. The descriptors describe how outputs are constructed and, depending on the information they contain, how the wallet can derive or monitor addresses.

One final security note: your example contains extended public keys, not obvious private extended keys. Even so, avoid publishing complete descriptors unnecessarily, because they can expose address-generation information and make it easier to link the wallet's transactions.
----------------------------------------------------------
Yes, exactly! One Bitcoin wallet can generate thousands of different Bitcoin addresses. You do not need to create a new wallet for every person who sends you bitcoin.

Let's use Omar's wallet from your lab to understand this.

# 1. One wallet, many addresses

Imagine Omar has one Bitcoin wallet in Bitcoin Core.

```
              OMAR'S WALLET
                    |
        +-----------+-----------+
        |           |           |
        v           v           v
    Address 1   Address 2   Address 3
        |           |           |
        v           v           v
     Payment     Payment     Payment
      from         from        from
      Amine        Sara       Ahmed
```

Omar has one wallet, but he can generate a new receiving address for each payment.

For example:

- Omar gives Address 1 to Amine.
- Omar gives Address 2 to Sara.
- Omar gives Address 3 to Ahmed.

All three addresses can belong to Omar's same wallet. Bitcoin Core manages the corresponding keys and tracks the funds received at those addresses.

The advantage is that Omar can use different addresses for different payments instead of reusing one address repeatedly.

# 2. Does each address have its own balance?

Technically, Bitcoin records individual transaction outputs (UTXOs), not one balance per wallet.

Suppose these payments arrive:

| Receiving address | Payment received |
| ----------------- | ---------------- |
| Omar's Address 1  | 2 BTC            |
| Omar's Address 2  | 3 BTC            |
| Omar's Address 3  | 1 BTC            |
| Total received    | 6 BTC            |

Omar's wallet can recognize all three payments and report a combined balance of 6 BTC, assuming all three outputs remain unspent and are spendable by the wallet.

```
Address 1: 2 BTC ──┐
Address 2: 3 BTC ──┼──> Omar's wallet: 6 BTC
Address 3: 1 BTC ──┘
```

The wallet combines the value of the UTXOs it controls to calculate its balance. The addresses themselves do not contain bitcoin.

# 3. So why does your wallet have eight descriptors?

Your JSON lists four address-generation types:

- Legacy (`pkh`)
- Wrapped SegWit (`sh(wpkh)`)
- Taproot (`tr`)
- Native SegWit (`wpkh`)

Each type has two branches:

- External (`/0/*`): typically used for receiving addresses.
- Internal (`/1/*`): typically used for change addresses when you spend bitcoin.

That gives you:

```
                  OMAR'S WALLET
                        |
        +---------------+---------------+
        |               |               |
     Legacy          SegWit           Taproot
        |               |               |
   Receiving        Receiving        Receiving
   + Change         + Change         + Change

        Native SegWit also has:
        Receiving + Change
```

There are eight descriptors because there are four address-generation types, each with an external and internal branch.

A descriptor is not a wallet and is not a single address. It describes how the wallet generates or recognizes a range of addresses.

# 4. Let's verify this on your computer

Generate two addresses using Omar's wallet:

```
bitcoin-cli -regtest -rpcwallet=omar getnewaddress
```

Run it again:

```
bitcoin-cli -regtest -rpcwallet=omar getnewaddress
```

You should receive two different addresses.

Now inspect each address:

```
bitcoin-cli -regtest -rpcwallet=omar getaddressinfo "FIRST_ADDRESS"
```

```
bitcoin-cli -regtest -rpcwallet=omar getaddressinfo "SECOND_ADDRESS"
```

The returned information should indicate that the addresses are associated with Omar's wallet, assuming they were generated by that wallet.

## Remember this distinction

- Wallet: Manages keys, addresses, and transaction information.
- Address: A payment destination.
- Descriptor: A recipe for generating or recognizing a set of payment destinations.
- UTXO: An unspent transaction output containing bitcoin that can potentially be spent.

For your Streamlit dashboard, this means you only need to select Omar's wallet to display its combined balance. You do not need to select every address individually.
----------------------------------------------------------
# Bitcoin Lab — Understanding `getaddressinfo`

You ran `getaddressinfo` twice on Omar's Bitcoin Core wallet. Both commands returned information about a receiving address.

The main result is that you have two different Native SegWit addresses belonging to the same wallet, Omar. Bitcoin Core recognizes both addresses and indicates that they are spendable by the wallet, assuming the required wallet keys remain available.

Let's understand what you did and what each result tells us.

## 1. What did you do?

Your first command was:

```
bitcoin-cli -regtest -rpcwallet=omar getaddressinfo bcrt1qc5j5zxvkl3z9tujmzty4mea62fzc4zmqz4r59w
```

Your second command was:

```
bitcoin-cli -regtest -rpcwallet=omar getaddressinfo bcrt1q2mq6a9pwerwcnwqpfahy4tem0tglhlpdg4fcya
```

The command has three important parts:

- `-regtest`: use your local Bitcoin regtest network.
- `-rpcwallet=omar`: query Omar's loaded wallet.
- `getaddressinfo ADDRESS`: ask Bitcoin Core to describe the specified address.

This command does not send bitcoin, generate a new address, or change the blockchain. It only retrieves information about the address.

## 2. What do we have here?

First address

`bcrt1qc5j5zxvkl3z9tujmzty4mea62fzc4zmqz4r59w`

Omar's wallet

Second address

`bcrt1q2mq6a9pwerwcnwqpfahy4tem0tglhlpdg4fcya`

Omar's wallet

Both addresses use the `bcrt1q` prefix, indicating Native SegWit version 0 addresses on regtest.

Both addresses share these properties:

- `"ismine": true` — Omar's wallet recognizes the address as belonging to its wallet-controlled spending conditions.
- `"solvable": true` — the wallet knows enough information about the output's spending conditions to construct a spending solution.
- `"iswatchonly": false` — the address is not merely being watched without spending authority.
- `"iswitness": true` — the address uses a SegWit witness program.
- `"witness_version": 0` — this is a SegWit version 0 output.

These fields describe wallet ownership and the type of payment destination. They do not prove that either address currently has a bitcoin balance.

## 3. Why are the addresses different if they belong to the same wallet?

Look at the `hdkeypath` field.

First address:

```
"hdkeypath": "m/84h/1h/0h/0/4"
```

Second address:

```
"hdkeypath": "m/84h/1h/0h/0/5"
```

The paths are almost identical. The final number changes from `4` to `5`.

Let's decode the first path:

```
m / 84h / 1h / 0h / 0 / 4
|    |     |     |    |   |
|    |     |     |    |   +-- Address index 4
|    |     |     |    +------ External receiving branch
|    |     |     +----------- Account 0
|    |     +----------------- Bitcoin test-network coin type
|    +----------------------- Native SegWit purpose
+---------------------------- Master key
```

The second address uses index `5` instead of `4`.

In other words, Bitcoin Core derives two different child keys from the same wallet's hierarchical deterministic (HD) key structure.

Conceptually:

```
                 Omar's HD wallet
                        |
                Account 0 (84h)
                        |
                External branch /0
                        |
                 +------+------+
                 |             |
                 v             v
              Index 4       Index 5
                 |             |
                 v             v
             Public key A  Public key B
                 |             |
                 v             v
             Address A     Address B
```

Each address has its own corresponding derived public key and spending key material. The wallet manages the relationship between these keys.

The `84h` purpose indicates the BIP84 derivation convention for native SegWit P2WPKH wallets. The `1h` coin type is used for Bitcoin test networks.

## 4. What is `scriptPubKey`?

Your first address has:

```
"scriptPubKey": "0014c525411996fc4455f25b12c95de7ba52458a8b60"
```

This is the locking script that Bitcoin places in a transaction output when someone pays that address.

For a native SegWit P2WPKH output, its structure is:

```
00 14 c525411996fc4455f25b12c95de7ba52458a8b60
|  |  |
|  |  +-- 20-byte public-key hash (witness program)
|  +----- Length: 20 bytes
+-------- Witness version 0
```

The first byte `00` represents witness version 0. The byte `14` means that the following witness program is 20 bytes long.

The second address has a different script:

```
001456c1ae942ec8dd89b8014f6e4aaf3b7ad1fbfc2d
```

Its witness program differs, so the output scripts are different.

Why does this matter? When someone pays either address, the transaction creates a UTXO locked to the corresponding script. Omar's wallet can later identify and spend that UTXO using the appropriate key and signature.

## 5. What is the `pubkey` field?

Your first address has this public key:

```
027723cdd2e0de1f809b38ab844f319dd993eb395b84b48f64b4f0bd27981e3626
```

Your second address has another:

```
02ba2e2a5e448a79192516bb936b844084219bda6d6c3aa473a8426739035c336f
```

They are different because they are derived at different child indexes.

The public key is used to derive the public-key hash in a P2WPKH address. When Omar spends the corresponding UTXO, his wallet uses the matching private key to generate a signature.

The private key is not shown in your output.

## 6. What is `parent_desc`?

Your output includes:

```
wpkh([d09100b8/84h/1h/0h]tpub.../0/*)#lpm3gkwp
```

This is the parent descriptor that describes the address-generation rule for the external Native SegWit branch.

The `*` means the descriptor can generate multiple child addresses.

The two address-specific descriptors are:

```
.../0/4
.../0/5
```

The parent descriptor instead uses:

```
.../0/*
```

Think of it this way:

- Parent descriptor: The recipe for generating a sequence of addresses.
- Address-specific descriptor: The recipe for one particular address.
- Child index: Identifies the particular address within the sequence.

## 7. What do the other fields mean?

| Field                 | Meaning in your output                                                                                          |
| --------------------- | --------------------------------------------------------------------------------------------------------------- |
| `ischange: false`     | Bitcoin Core does not classify this address as a change address. It is an external address.                     |
| `timestamp`           | The wallet's recorded time associated with the address or descriptor. It is not the time a payment occurred.    |
| `hdmasterfingerprint` | `d09100b8`, an identifier used to help identify the originating master key.                                     |
| `hdseedid`            | An all-zero identifier in this output. Do not interpret it as a bitcoin balance or proof that a seed is absent. |
| `labels: [""]`        | The address has an empty label. You can generate labeled addresses with `getnewaddress "My label"`.             |
| `desc`                | The descriptor for the specific derived address.                                                                |
| `parent_desc`         | The descriptor that describes the broader range of addresses.                                                   |

## 8. How can you check whether these addresses have received bitcoin?

`getaddressinfo` describes the addresses, but it does not return their balances.

To check Omar's overall wallet balance:

```
bitcoin-cli -regtest -rpcwallet=omar getbalances
```

To check the wallet's transaction history:

```
bitcoin-cli -regtest -rpcwallet=omar listtransactions "*" 20
```

To inspect unspent outputs:

```
bitcoin-cli -regtest -rpcwallet=omar listunspent
```

`listunspent` returns UTXOs known to the wallet. If you need to check a particular address, examine the returned outputs' `address` fields and sum the relevant unspent values.

## 9. Final understanding

What you have demonstrated is that Omar's wallet derives multiple addresses from a shared HD wallet structure.

- The first address is at index `4`.
- The second address is at index `5`.
- Both use Native SegWit.
- Both are recognized by Omar's wallet.
- They have different public keys, witness programs, and addresses.
- Both can receive payments independently, while their spendable UTXOs contribute to Omar's combined wallet balance.

Try this next: Generate a third address with `getnewaddress`, then run `getaddressinfo` on it. Check whether the derivation path advances to index `6`. This will help you verify the relationship between address generation and HD derivation directly.



----------------------------------------------------------
# Lab 14 — Bitcoin Wallet Encryption & Security

Objective: Learn how Bitcoin Core protects wallet keys, how to encrypt and unlock a wallet, how to lock it again, and why RPC credentials must be protected.

We'll use your Bitcoin Core 31.1 installation and the `regtest` network on Ubuntu. All exercises are for your learning environment, not for a production wallet.

## 1. Understand the security model

Your Bitcoin wallet manages keys that authorize spending. Anyone who obtains usable private-key material may be able to spend the associated funds.

Bitcoin Core provides wallet encryption to protect private-key material stored in the wallet.

```
              Streamlit / Terminal
                      |
                      | JSON-RPC
                      v
                 Bitcoin Core
                      |
                      v
                  Omar Wallet
                      |
              +-------+-------+
              |               |
              v               v
        Private keys      Wallet data
              |
              v
       Sign transactions
```

There are two separate security mechanisms here:

- Wallet encryption: Protects sensitive wallet key material at rest using a wallet passphrase.
- RPC authentication: Controls who can send commands to Bitcoin Core's RPC interface.

They solve different problems. Encrypting the wallet does not automatically secure RPC access, and protecting RPC credentials does not encrypt the wallet file.

## 2. What does wallet encryption do?

When a wallet is encrypted, Bitcoin Core uses a passphrase to protect its private-key material.

The passphrase is not the same as a Bitcoin private key or a receiving address.

| Term                            | Purpose                                                |
| ------------------------------- | ------------------------------------------------------ |
| Private key                     | Authorizes spending under the corresponding conditions |
| Wallet passphrase               | Protects encrypted wallet key material                 |
| RPC username/password or cookie | Authenticates access to Bitcoin Core RPC               |
| Bitcoin address                 | Identifies a payment destination                       |

A wallet can still contain transaction history and public information while encrypted. Encryption primarily protects sensitive key material; it does not hide the wallet's transactions from the public blockchain.

Important: If you forget the wallet passphrase and have no usable recovery backup, you may permanently lose access to the encrypted keys. Use a disposable regtest wallet for this lab.

## 3. Encrypt a wallet — `encryptwallet`

For this exercise, use a dedicated test wallet named `securitylab`, rather than encrypting Omar's existing wallet. That avoids disrupting your current lab.

First, check your loaded wallets:

```
bitcoin-cli -regtest listwallets
```

Create the test wallet if it does not already exist:

```
bitcoin-cli -regtest createwallet "securitylab"
```

If it already exists but is not loaded, load it:

```
bitcoin-cli -regtest loadwallet "securitylab"
```

Generate a test address:

```
bitcoin-cli -regtest -rpcwallet=securitylab getnewaddress
```

Now encrypt the wallet:

```
bitcoin-cli -regtest -rpcwallet=securitylab encryptwallet "Use-A-Unique-Lab-Passphrase"
```

Replace the example passphrase with a strong, unique lab passphrase. Do not reuse a real password.

Bitcoin Core encrypts the wallet and shuts down the node as part of this operation. Wait for the process to stop, then restart Bitcoin Core using the same data directory and configuration.

For example, if you normally start it with:

```
/opt/bitcoin/bin/bitcoind -daemon
```

use your usual startup command.

Do not run `encryptwallet` on Omar's existing wallet unless you intentionally want to encrypt it and have securely saved the passphrase. Encryption cannot simply be undone by running the command again.

## 4. Unlock the wallet — `walletpassphrase`

After restarting Bitcoin Core, load the encrypted wallet if necessary:

```
bitcoin-cli -regtest loadwallet "securitylab"
```

Unlock it for 60 seconds:

```
bitcoin-cli -regtest -rpcwallet=securitylab walletpassphrase "YOUR-LAB-PASSPHRASE" 60
```

Replace the placeholder with the passphrase you used during encryption.

The final argument, `60`, is the unlock timeout in seconds.

During this period, Bitcoin Core can use the encrypted private keys for operations requiring them, such as signing a transaction.

Unlocking does not mean the passphrase becomes a public key, nor does it change the wallet's addresses.

### What happens when the timeout expires?

Bitcoin Core automatically locks the wallet again after the specified timeout, unless the timeout is reset or the wallet is explicitly locked sooner.

Avoid putting real passphrases directly into shell commands in a real environment: command arguments may be exposed through shell history or process inspection. The literal command above is for illustrating the RPC interface in a disposable lab.

## 5. Lock the wallet — `walletlock`

You can lock the wallet before the timeout expires:

```
bitcoin-cli -regtest -rpcwallet=securitylab walletlock
```

Locking prevents Bitcoin Core from using the encrypted private keys for operations that require an unlocked wallet.

For example, attempting to sign or send a transaction may fail because the wallet is locked.

However, locking does not prevent every wallet operation. You can generally still inspect addresses, transaction history, and balances.

### Compare the three states

| State                  | Can inspect wallet? | Can sign using encrypted keys?      |
| ---------------------- | ------------------- | ----------------------------------- |
| Unencrypted wallet     | Yes                 | Yes, subject to wallet capabilities |
| Encrypted and locked   | Yes                 | No                                  |
| Encrypted and unlocked | Yes                 | Yes                                 |

These are simplified descriptions; exact RPC behavior depends on the operation and wallet configuration.

## 6. RPC security — how does your application authenticate?

Your Streamlit application will communicate with Bitcoin Core using JSON-RPC over HTTP.

```
Browser
   |
   v
Streamlit (Python)
   |
   | HTTP + JSON-RPC authentication
   v
Bitcoin Core RPC server
   |
   v
Wallet operations
```

RPC authentication is separate from wallet encryption.

Bitcoin Core commonly supports two ways to authenticate RPC requests:

### Method A — RPC cookie authentication

Bitcoin Core can create a temporary cookie file containing an automatically generated authentication credential.

For example, the cookie may be located under the node's data directory, often at:

```
~/.bitcoin/regtest/.cookie
```

The actual location depends on your configuration and data directory.

A local `bitcoin-cli` process can read this cookie and use it to authenticate with the RPC server. When Bitcoin Core shuts down, the cookie is normally removed; a new one is created on startup.

Advantages:

- Convenient for local development.
- No manually configured permanent RPC password.
- Automatically managed by Bitcoin Core.

The cookie file is still a secret. Anyone who can read it may be able to authenticate to the corresponding RPC server.

### Method B — Configured RPC credentials

Bitcoin Core can also use configured RPC authentication settings.

A simplified example is:

```
rpcuser=bitcoinlab
rpcpassword=YOUR-STRONG-RANDOM-PASSWORD
```

Do not copy that example password into a real configuration. For an actual deployment, follow Bitcoin Core's recommended RPC authentication practices, including `rpcauth` where appropriate.

Store credentials in a protected configuration file or environment-specific secret location, not in your Git repository or Streamlit frontend.

### Why do RPC credentials matter?

A user who can authenticate to a Bitcoin Core RPC server may be able to do far more than inspect balances, depending on the permissions and methods available.

Potentially sensitive operations include:

- Inspecting wallet information.
- Generating receiving addresses.
- Creating and broadcasting transactions.
- Unlocking encrypted wallets if the user also knows the wallet passphrase.

RPC credentials are therefore powerful access credentials, not ordinary application settings.

## 7. Protect your RPC configuration

For your Streamlit learning app, the simplest safe setup is to run Streamlit and Bitcoin Core on the same Ubuntu host and connect through localhost.

Example Bitcoin Core configuration:

```
regtest=1
server=1
```

This enables regtest and the RPC server. Bitcoin Core still needs its supported authentication configuration; enabling `server=1` alone does not replace authentication.

Check the node's RPC-related settings:

```
bitcoin-cli -regtest getnetworkinfo
```

Check the location of your Bitcoin data directory and configuration rather than assuming that `/opt/bitcoin/bitcoin.conf` is the active file. The executable location and data directory are separate concepts.

For your project:

- Keep the RPC server bound to localhost unless remote access is specifically required.
- Never expose RPC credentials in `app.py`, browser code, GitHub, or screenshots.
- Restrict permissions on configuration files and cookie files.
- Do not expose Bitcoin Core RPC directly to the public internet.
- Require explicit confirmation before the Streamlit app sends a transaction.
- Keep this project on regtest and use test wallets.

If you later connect to Bitcoin Core running on another VM, configure the RPC server and firewall deliberately. The node's P2P port and RPC port are different services; opening the P2P port does not automatically enable RPC access.

## 8. Practical exercise — test the wallet's security states

After completing encryption and restarting Bitcoin Core, perform these checks.

A. Check wallet information

```
bitcoin-cli -regtest -rpcwallet=securitylab getwalletinfo
```

For an encrypted wallet, inspect the `unlocked_until` field when present. A value of `0` indicates that the wallet is locked.

B. Unlock the wallet

```
bitcoin-cli -regtest -rpcwallet=securitylab walletpassphrase "YOUR-LAB-PASSPHRASE" 60
```

Run `getwalletinfo` again and observe the unlock status.

C. Lock the wallet

```
bitcoin-cli -regtest -rpcwallet=securitylab walletlock
```

Run `getwalletinfo` again to confirm that the wallet is locked.

D. Inspect your RPC cookie file

On a typical Linux regtest setup, you can check whether the cookie file exists with:

```
ls -l ~/.bitcoin/regtest/.cookie
```

If your node uses a custom data directory, adjust the path. Do not print or share the cookie's contents.

## 9. What you should understand after Lab 14

By the end of this lab, you should be able to explain:

1. Why encrypting a wallet protects sensitive key material.
2. Why an encrypted wallet must be unlocked for operations that need its private keys.
3. Why locking a wallet reduces the period during which its keys can be used.
4. Why RPC authentication and wallet encryption protect different things.
5. Why exposing RPC credentials can put wallet funds at risk.

### Knowledge check

1. If Omar's wallet is encrypted and locked, can he still inspect its balance?
2. What is the difference between a wallet passphrase and an RPC password?
3. Why is a Bitcoin Core RPC cookie a secret even though it is not a private key?
4. What could happen if you commit your RPC credentials to a public GitHub repository?

The key lesson is that wallet encryption protects keys at rest, wallet locking limits their use, and RPC authentication controls access to the node's interface. All three are important, even in a learning lab.


# What does “Unlock a Bitcoin Wallet” mean?

When you encrypt a Bitcoin wallet, Bitcoin Core protects its private keys with a passphrase. Unlocking the wallet means temporarily allowing Bitcoin Core to use those protected private keys to sign transactions.

Think of it like a safe:

- Wallet encrypted and locked: The safe is closed. You can still inspect some information, but you cannot use the protected keys to authorize spending.
- Wallet unlocked: You enter the correct passphrase, and Bitcoin Core can use the private keys for operations that require them.
- Wallet locked again: Access to the protected keys for signing is restricted again.

## 1. Example with Omar's wallet

Suppose Omar has 5 BTC in his regtest wallet and wants to send 2 BTC to Sara.

```
Omar's wallet (encrypted and locked)
              |
              v
       Omar wants to send 2 BTC
              |
              v
       Wallet needs to sign
              |
              v
       Unlock with passphrase
              |
              v
       Bitcoin Core signs transaction
              |
              v
       Transaction can be broadcast
```

Unlocking does not transfer bitcoin, change the balance, or reveal the private key to Sara. It allows Bitcoin Core to use the necessary keys.

## 2. How to unlock the wallet

In your Bitcoin Core `regtest` lab, run:

```
bitcoin-cli -regtest -rpcwallet=omar walletpassphrase "YOUR_PASSPHRASE" 60
```

Replace `YOUR_PASSPHRASE` with the passphrase you chose when encrypting Omar's wallet.

The `60` means the wallet remains unlocked for approximately 60 seconds. After that, Bitcoin Core automatically locks it again unless the timeout is reset or you lock it sooner.

To lock it immediately:

```
bitcoin-cli -regtest -rpcwallet=omar walletlock
```

Important: These commands apply to an encrypted wallet. An unencrypted wallet does not need to be unlocked with `walletpassphrase`.

## 3. What can you do while the wallet is locked?

| Operation                                       | Encrypted and locked |
| ----------------------------------------------- | -------------------- |
| Check wallet balance                            | Usually yes          |
| View receiving addresses                        | Yes                  |
| Inspect transaction history                     | Yes                  |
| Generate a receiving address                    | Generally yes        |
| Sign a transaction using encrypted private keys | No                   |
| Send a transaction requiring those keys         | No, until unlocked   |

The exact behavior depends on the operation and wallet configuration.

## 4. The most important distinction

- Encryption protects private-key material stored in the wallet.
- Unlocking temporarily enables use of the protected keys.
- Locking disables that unlocked state.
- RPC authentication determines who can issue commands to Bitcoin Core.

### Practice questions

1. If Omar's wallet is locked, can he still check his balance?
2. Does unlocking the wallet automatically send bitcoin?
3. Why is it safer to lock an encrypted wallet when you finish using its keys?



---------------------------------------------------------------
# Lab 15 — Wallet Backup & Recovery

Environment: Ubuntu Server + Bitcoin Core + Regtest

Participants: Omar, Sara, Amine, Ahmed

Objective: Learn how Bitcoin Core wallets are backed up, restored, recovered, and how descriptor wallets manage the information needed to derive Bitcoin addresses and control funds.

We will use the traditional Markdown-friendly format so you can copy the entire lab directly into your `.md` file.

## 1. Introduction

A Bitcoin wallet does not actually store bitcoins inside a file. Bitcoins are recorded in the blockchain as unspent transaction outputs (UTXOs).

A wallet stores or manages the cryptographic information and metadata needed to control those funds, including private keys, scripts, addresses, and transaction information.

If Omar has 10 BTC in his wallet and his computer fails, the bitcoins do not disappear from the blockchain. However, Omar may lose the ability to spend them if he loses the necessary private keys and has no valid backup.

Wallet backup and recovery protect against this problem.

### 1.1 Learning objectives

By the end of this lab, you will be able to:

1. Create a Bitcoin Core wallet backup.
2. Understand what a wallet backup contains.
3. Restore a wallet from a backup.
4. Verify that the restored wallet can access its funds.
5. Understand the difference between wallet recovery and blockchain synchronization.
6. Understand descriptor wallets and their role in wallet recovery.
7. Apply basic wallet backup security practices.

### 1.2 Important concepts

| Concept           | Explanation                                                           |
| ----------------- | --------------------------------------------------------------------- |
| Wallet backup     | A copy of the wallet data needed for recovery                         |
| Private key       | Secret cryptographic information used to authorize spending           |
| Seed phrase       | Human-readable recovery words used by some wallet implementations     |
| Wallet encryption | Protects wallet data at rest using a passphrase                       |
| Restore           | Reopen or recover wallet data from a backup                           |
| Descriptor        | Describes how a wallet derives addresses and spending scripts         |
| Blockchain        | The shared ledger containing transactions and UTXOs                   |
| Rescan            | Re-examine blockchain transactions to find those relevant to a wallet |

Important: Bitcoin Core's native wallet backup is not necessarily a 12- or 24-word seed phrase. Bitcoin Core wallet recovery depends on the wallet type and the backup data available.

## 2. Understand the Wallet Backup Process

Consider the following example:

- Omar owns a Bitcoin Core wallet.
- Omar mined some blocks on the regtest network.
- His wallet received a spendable coinbase reward.
- Omar then sends 2 BTC to Sara.
- Later, Omar's machine fails.

The blockchain still contains the transactions, but Omar needs his wallet data to recover access to the funds that belong to him.

The general process is:

```
Bitcoin Core Wallet
        |
        v
Create Wallet Backup
        |
        v
Store Backup Securely
        |
        v
Wallet Data Lost
        |
        v
Restore Backup
        |
        v
Rescan Blockchain if Needed
        |
        v
Verify Addresses and Balance
```

A backup is only useful if it is valid, protected against unauthorized access, and restorable.

## 3. Lab Environment Preparation

We will use Omar's existing Bitcoin Core regtest wallet.

First, check that Bitcoin Core is running:

```
bitcoin-cli -regtest getblockchaininfo
```

Check the available wallets:

```
bitcoin-cli -regtest listwallets
```

List wallet files known to Bitcoin Core:

```
bitcoin-cli -regtest listwalletdir
```

If Omar's wallet is not loaded, load it:

```
bitcoin-cli -regtest loadwallet "omar"
```

If it is already loaded, do not load it again.

Check Omar's balance:

```
bitcoin-cli -regtest -rpcwallet=omar getbalance
```

Check the wallet information:

```
bitcoin-cli -regtest -rpcwallet=omar getwalletinfo
```

Record the following information in your lab notes:

- Wallet name
- Wallet balance
- Number of transactions
- Whether the wallet is encrypted
- Current blockchain height

For the blockchain height:

```
bitcoin-cli -regtest getblockcount
```

Note: The balance depends on your current lab state. Do not assume that Omar has a particular balance unless the command confirms it.

## 4. Lab 15.1 — Create a Wallet Backup

Bitcoin Core provides the `backupwallet` RPC command to create a wallet backup.

### Step 1 — Create a backup directory

Create a directory for your lab backups:

```
mkdir -p ~/bitcoin-lab/backups
chmod 700 ~/bitcoin-lab
chmod 700 ~/bitcoin-lab/backups
```

The permissions restrict access to the current Linux user.

### Step 2 — Create the backup

Run:

```
bitcoin-cli -regtest -rpcwallet=omar backupwallet "$HOME/bitcoin-lab/backups/omar-backup.dat"
```

If successful, Bitcoin Core confirms the backup destination.

The exact backup filename is not important. What matters is that you know which wallet it belongs to and when it was created.

### Step 3 — Verify the backup file

Run:

```
ls -lh ~/bitcoin-lab/backups/
```

Check the file type:

```
file ~/bitcoin-lab/backups/omar-backup.dat
```

Calculate a SHA-256 checksum:

```
sha256sum ~/bitcoin-lab/backups/omar-backup.dat
```

The checksum helps you detect whether the file changes later. It does not prove that the backup is valid or recoverable.

### Step 4 — Understand what was backed up

A Bitcoin Core wallet backup contains wallet data, including relevant key material and wallet metadata, depending on the wallet implementation.

It does not contain the entire Bitcoin blockchain.

The blockchain remains in Bitcoin Core's node data directory.

Therefore:

- Wallet backup = wallet recovery information.
- Blockchain data = transaction history and current ledger state.
- Both may be needed for a complete recovery workflow, but the blockchain can generally be downloaded or synchronized again.

## 5. Lab 15.2 — Restore a Wallet from a Backup

For this exercise, we will restore Omar's backup under a different wallet name so we do not overwrite his existing wallet.

Important: Use a new destination name. Never experiment with your only backup or overwrite the original wallet.

### Step 1 — Create a recovery directory

```
mkdir -p ~/bitcoin-lab/recovery
chmod 700 ~/bitcoin-lab/recovery
```

### Step 2 — Locate the Bitcoin Core wallet directory

Ask Bitcoin Core for its data directory:

```
bitcoin-cli -regtest getdatadir
```

On a typical Linux installation, the regtest wallet directory is under:

```
~/.bitcoin/regtest/wallets/
```

The exact location depends on your Bitcoin Core configuration and any custom `-datadir` setting.

If your wallet uses the default directory, inspect it with:

```
ls -la ~/.bitcoin/regtest/wallets/
```

### Step 3 — Restore the backup file

For this lab, copy the backup to a new wallet directory:

```
mkdir -p ~/.bitcoin/regtest/wallets/omar-recovered
chmod 700 ~/.bitcoin/regtest/wallets/omar-recovered
cp ~/bitcoin-lab/backups/omar-backup.dat ~/.bitcoin/regtest/wallets/omar-recovered/wallet.dat
chmod 600 ~/.bitcoin/regtest/wallets/omar-recovered/wallet.dat
```

Before running these commands, verify that `omar-recovered` does not already exist. If you configured a custom Bitcoin Core data directory, adjust the destination accordingly.

### Step 4 — Load the recovered wallet

```
bitcoin-cli -regtest loadwallet "omar-recovered"
```

If the wallet loads successfully, inspect it:

```
bitcoin-cli -regtest -rpcwallet=omar-recovered getwalletinfo
```

Check its balance:

```
bitcoin-cli -regtest -rpcwallet=omar-recovered getbalance
```

Compare the recovered wallet with the original:

```
bitcoin-cli -regtest -rpcwallet=omar getbalance
```

The balances should normally agree if the backup contains the relevant wallet data and no subsequent transactions have changed the original wallet's balance.

Important: Do not assume that a backup created earlier will automatically reflect transactions that occurred after the backup. Wallet recovery may require rescanning the blockchain, and the wallet may need to discover newer addresses or transactions depending on the wallet type and backup state.

## 6. Lab 15.3 — Recovery Concepts

Wallet recovery is not simply copying a file. Several different problems can occur.

### 6.1 Scenario A — The wallet file is lost

Omar loses his wallet file but has a valid backup.

Recovery process:

1. Install or start Bitcoin Core.
2. Ensure the node uses the correct network.
3. Restore the wallet backup.
4. Load the recovered wallet.
5. Verify the wallet's addresses and balance.
6. Rescan the blockchain if required.

### 6.2 Scenario B — The blockchain data is lost

Omar loses the node's local blockchain data, but his wallet backup remains safe.

Recovery process:

1. Install or start Bitcoin Core.
2. Restore the wallet backup if necessary.
3. Allow Bitcoin Core to synchronize or redownload blockchain data.
4. Verify that the node is on the intended network.
5. Verify the wallet's balance after synchronization and any required rescan.

The blockchain is replicated across nodes. Losing one node's local copy does not erase the network's ledger.

### 6.3 Scenario C — The wallet is encrypted

If Omar encrypted his wallet, restoring the backup does not remove the encryption.

He still needs the wallet passphrase to unlock the wallet for operations that require access to its private keys.

For an encrypted wallet:

```
bitcoin-cli -regtest -rpcwallet=omar-recovered walletpassphrase "YOUR_PASSPHRASE" 60
```

Replace the placeholder with your actual passphrase. Avoid placing real passphrases in shell history, scripts, screenshots, or shared lab notes.

After the exercise, lock the wallet again:

```
bitcoin-cli -regtest -rpcwallet=omar-recovered walletlock
```

If you do not know the passphrase and have no other usable copy of the necessary keys, a backup of the encrypted wallet may not be enough to recover spending access.

### 6.4 Scenario D — The backup is outdated

Suppose Omar creates a backup, then receives additional funds and generates more addresses.

An older backup might not contain all the information required to recover later wallet activity, depending on the wallet type, keypool state, descriptors, and derivation range.

This is one reason to understand how the specific wallet implementation handles backup and recovery.

### 6.5 Recovery terminology

| Term             | Meaning                                                              |
| ---------------- | -------------------------------------------------------------------- |
| Restore          | Reintroduce wallet data from a backup                                |
| Rescan           | Search blockchain history for wallet transactions                    |
| Synchronization  | Bring the node's blockchain state up to date                         |
| Unlock           | Make encrypted wallet keys available for authorized operations       |
| Recovery phrase  | A standardized sequence of words supported by certain wallet systems |
| Keypool          | A reserve of keys or addresses available for wallet use              |
| Descriptor range | The derivation index range a descriptor wallet tracks or scans       |

## 7. Lab 15.4 — Descriptor Wallets

Modern Bitcoin Core wallets use descriptors to describe how addresses and spending scripts are derived.

A descriptor can specify the type of script, the relevant public key or extended public key, and, when applicable, a derivation path.

For example, a simplified descriptor might look like:

```
pkh([fingerprint/44h/1h/0h]xpub.../0/*)
```

This is an illustrative example, not a complete descriptor you can use directly. The `xpub...` portion is a placeholder.

A descriptor tells the wallet how to derive a family of addresses. It does not, by itself, necessarily provide the private keys needed to spend funds.

### 7.1 Why descriptors matter

Descriptors make wallet structure more explicit.

They help Bitcoin Core identify:

- Which scripts the wallet controls or tracks.
- How addresses are derived.
- Which derivation paths are used.
- Whether a descriptor is associated with internal change addresses or external receiving addresses.

Descriptor information is particularly important when recovering a wallet or importing wallet data into another compatible wallet.

### 7.2 Check whether Omar uses a descriptor wallet

Run:

```
bitcoin-cli -regtest -rpcwallet=omar getwalletinfo
```

Look for a field such as:

```
"descriptors": true
```

The exact output depends on the wallet and Bitcoin Core version.

You can also list wallet descriptors:

```
bitcoin-cli -regtest -rpcwallet=omar listdescriptors
```

This RPC may require an unlocked wallet, depending on the descriptor data and wallet configuration. Be careful with its output: descriptors can contain sensitive wallet information, especially when private key material is included.

Never publish descriptor output or share it in a public repository without inspecting it for secrets.

### 7.3 Export descriptors

Bitcoin Core provides the `listdescriptors` RPC to inspect descriptors and the `importdescriptors` RPC to import descriptor data into a compatible wallet.

For example:

```
bitcoin-cli -regtest -rpcwallet=omar listdescriptors
```

Do not treat the output as a substitute for a proper backup. A descriptor that contains only public key material may allow address derivation and transaction monitoring but may not permit spending.

A descriptor that contains private key material is highly sensitive and must be protected accordingly.

### 7.4 Descriptor wallet recovery

For descriptor wallets, recovery requires preserving the relevant descriptor information and key material.

Depending on the wallet configuration, recovery may involve:

1. Restoring a native Bitcoin Core wallet backup.
2. Importing descriptors into a compatible wallet.
3. Specifying or extending the appropriate derivation ranges.
4. Rescanning blockchain history to find relevant transactions.

A native wallet backup is generally the simpler recovery method for your lab because it preserves the wallet's associated state rather than requiring you to reconstruct it manually.

## 8. Lab 15.5 — Verify the Recovered Wallet

A successful `loadwallet` command is not sufficient proof that recovery is complete.

Perform these checks.

### Check 1 — Wallet loads

```
bitcoin-cli -regtest -rpcwallet=omar-recovered getwalletinfo
```

### Check 2 — Wallet has expected addresses

```
bitcoin-cli -regtest -rpcwallet=omar getnewaddress
```

Compare this with the recovered wallet's existing addresses using the wallet history or known addresses from before the backup. Do not expect `getnewaddress` to return the same address on both wallets; it normally generates a new address.

### Check 3 — Check transaction history

```
bitcoin-cli -regtest -rpcwallet=omar-recovered listtransactions "*" 10
```

This checks recent wallet transaction history. The result depends on what the backup contained and whether the wallet has scanned the relevant blockchain history.

### Check 4 — Compare balances

```
bitcoin-cli -regtest -rpcwallet=omar getbalance
bitcoin-cli -regtest -rpcwallet=omar-recovered getbalance
```

If the values differ, investigate whether:

- The backup predates a transaction.
- The wallet needs a rescan.
- The node has not synchronized.
- The wallet's derivation range is incomplete.
- The original wallet has received or spent funds since the backup.

### Check 5 — Verify the blockchain state

```
bitcoin-cli -regtest getblockchaininfo
```

Confirm that the node is using `regtest`, not `main` or `test`.

A wallet backup is network-independent in the sense that wallet keys can be used on different Bitcoin networks, but balances and transaction history depend on the particular blockchain being examined.

## 9. Wallet Backup Security Best Practices

1. Keep multiple backups. Store copies on separate secure storage devices or locations.
2. Encrypt sensitive backups. Protect wallet files against theft, especially if they contain private keys.
3. Protect the encryption passphrase. A backup and its passphrase should not be stored together without appropriate safeguards.
4. Restrict file permissions. Use Linux permissions to prevent other local users from reading backup files.
5. Test recovery. Periodically restore a backup in an isolated environment.
6. Record the wallet type. Document whether the wallet is descriptor-based and which Bitcoin Core version was used.
7. Avoid overwriting the only backup. Keep dated versions when making new backups.
8. Never share private keys. Do not commit wallet files, seed phrases, private descriptors, or credentials to GitHub.
9. Separate lab and real funds. Use regtest for these exercises and never experiment with a wallet holding valuable real funds.
10. Understand the limits of a backup. A backup can be valid but outdated, incomplete for a particular recovery procedure, or unusable without the necessary passphrase.

## 10. Lab 15 — Final Checklist

Use this checklist as you complete the lab.

- Confirmed Omar's wallet was loaded.
- Recorded the original wallet balance.
- Created a wallet backup using `backupwallet`.
- Verified the backup file exists.
- Calculated a SHA-256 checksum.
- Restored the backup as a separate wallet.
- Loaded the recovered wallet.
- Checked the recovered balance.
- Reviewed wallet transaction history.
- Inspected descriptor-wallet information.
- Explained the difference between restoring a wallet and synchronizing a blockchain.
- Documented the limitations of the recovery test.

## 11. Knowledge Check

Question 1: If Omar loses his computer but has a valid wallet backup, are his bitcoins necessarily lost?

Question 2: What is the difference between a wallet backup and a blockchain backup?

Question 3: Why might an old wallet backup show a different balance from the original wallet?

Question 4: What information does a Bitcoin descriptor describe?

Question 5: Why is a descriptor containing only public key information not necessarily enough to spend bitcoins?

Question 6: If a wallet backup is encrypted, what else is needed to unlock the wallet?

Question 7: Why should you restore a backup under a different wallet name during this lab?

Question 8: What is the purpose of a blockchain rescan during wallet recovery?

## 12. Lab Completion Criteria

Lab 15 is complete when you can independently create a backup, restore it into a separate wallet, explain why the blockchain is separate from wallet data, and describe how descriptor information affects recovery.

The most important lesson is this: Bitcoin Core backups protect access to funds, but recovery must be verified rather than assumed. A wallet that loads successfully is a good start; confirming the relevant keys, addresses, transaction history, and balance is what makes the exercise meaningful.