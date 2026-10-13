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

------------------------------------------------------------------------------------------------------------------------------------------------------------------

### the unite of the bitcoin 
# Understanding Your Bitcoin Core `listunspent` Output

This output represents unspent transaction outputs (UTXOs) belonging to your Bitcoin Core wallet. Each object describes a specific output from a transaction that your wallet can potentially spend.

The most important idea is:

Bitcoin does not store your balance as one single number. It tracks individual transaction outputs, and your wallet calculates its balance from the outputs it controls.

Your JSON contains 7 UTXOs. Let's analyze them step by step.

## 1. Summary of your UTXOs

Calculated from the seven entries you provided.

| UTXO  | Amount   | Confirmations | Address index |
| ----- | -------- | ------------- | ------------- |
| 1     | 3.0 BTC  | 4             | `/0/0`        |
| 2     | 1.2 BTC  | 1             | `/0/2`        |
| 3     | 1.0 BTC  | 1             | `/0/5`        |
| 4     | 1.0 BTC  | 4             | `/0/0`        |
| 5     | 2.0 BTC  | 3             | `/0/1`        |
| 6     | 1.0 BTC  | 1             | `/0/1`        |
| 7     | 1.2 BTC  | 2             | `/0/1`        |
| Total | 11.4 BTC |               |               |

Your listed UTXOs total:

\\[ 3+1.2+1+1+2+1+1.2=11.4\text{ BTC} \\]

In satoshis:

\\[ 11.4 \times 100,000,000 =1,140,000,000\text{ sats} \\]

This is the total of the outputs shown, not necessarily the wallet's entire balance: `listunspent` only displays outputs matching its filters, which by default include outputs with at least one confirmation.

## 2. What is a UTXO?

UTXO means Unspent Transaction Output.

Imagine that Omar receives 3 BTC from another transaction. Bitcoin Core records an output worth 3 BTC that Omar's wallet can spend.

Later, Omar sends Sara 1 BTC. Bitcoin generally does not edit the original 3 BTC output to make it 2 BTC. Instead, it consumes the original output and creates new outputs.

For example:

```
Before the transaction:

Omar owns a UTXO worth 3.0 BTC

After Omar sends Sara 1.0 BTC:

Input:
  Omar's previous UTXO       3.0 BTC

Outputs:
  Sara receives              1.0 BTC
  Omar receives change       1.9999 BTC
  Transaction fee            0.0001 BTC
```

The amounts above are illustrative. The actual change and fee depend on the transaction.

The original 3 BTC UTXO is now spent and cannot be spent again. Omar's new change output becomes a different UTXO.

## 3. Understanding each JSON field

Let's take your first entry as an example.

### `txid`

```
"txid": "5a8d20808236f6b3c7e4ff27c11ba0ca77ca3560ffeda3b04f25b1d5a538f8f7"
```

This is the transaction ID identifying the transaction that created this output.

Several UTXOs can have the same `txid` if they were created by different outputs of one transaction.

### `vout`

```
"vout": 0
```

`vout` is the index of the output within that transaction.

A UTXO is uniquely identified by the combination:

```
txid + vout
```

For example:

```
5a8d2080...a538f8f7 : output 0
```

This combination is called an outpoint.

Output indexes start at zero, so `vout: 0` means the first output, while `vout: 1` means the second output.

### `address`

```
"address": "bcrt1qn25rtxwz0wduv0rt0rcrp0qmmg33cqva6ytugn"
```

This is the Bitcoin address associated with the output.

The `bcrt1` prefix indicates a native SegWit address on your `regtest` network.

Notice that your first and fourth entries use the same address but have different transaction IDs:

- First entry: 3 BTC, `txid` begins `5a8d2080...`
- Fourth entry: 1 BTC, `txid` begins `e2f00767...`

One address can receive multiple payments. Each payment can create a separate UTXO, even when the receiving address is identical.

### `amount`

```
"amount": 3.00000000
```

The amount is expressed in BTC, not satoshis.

```
3 BTC = 300,000,000 satoshis
```

The second entry's `1.2 BTC` equals `120,000,000 satoshis`.

### `confirmations`

```
"confirmations": 4
```

This indicates how many confirmations the output has, including its containing block.

- `0`: unconfirmed output, generally still in the mempool or otherwise not included in the active chain.
- `1`: included in a block.
- `4`: included in a block with three additional blocks built on top of it.

In your example, the first UTXO has 4 confirmations, whereas the second has 1.

On `regtest`, you control block production, so you can observe confirmation counts change as you mine more blocks.

### `spendable`

```
"spendable": true
```

Bitcoin Core considers this output spendable by the wallet, assuming the required conditions are met.

This normally means the wallet has the necessary signing capability and the output is eligible under the wallet's current rules. It does not mean that the output has already been spent.

### `solvable`

```
"solvable": true
```

Bitcoin Core understands how the output could be spent. For example, it knows the spending script and the required conditions.

An output can be solvable without the wallet having the private keys required to spend it. In your entries, both `solvable` and `spendable` are `true`.

### `safe`

```
"safe": true
```

Bitcoin Core considers the output safe to use for spending under its wallet safety rules. This commonly depends on whether the transaction is confirmed or otherwise considered safe by the wallet.

It is not a guarantee against every possible reorganization or other network event.

## 4. Understanding `scriptPubKey`

For your first UTXO:

```
"scriptPubKey": "00149aa83599c27b9bc63c6b78f030bc1bda231c019d"
```

This is the locking script, represented as hexadecimal.

Your output starts with:

```
00 14 ...
```

For a native SegWit version 0 P2WPKH output:

- `00` indicates witness version 0.
- `14` means the following witness program is 20 bytes long.
- The remaining 20 bytes contain the witness program, derived from a public-key hash.

The locking script defines the conditions required to spend the output. For this address type, the spending transaction normally supplies a matching public key and a valid signature.

## 5. Understanding `desc` and `parent_descs`

These fields are particularly important for your wallet descriptor lab.

Your first entry has:

```
wpkh([d09100b8/84h/1h/0h/0/0]02de7bc9... )
```

This descriptor describes the specific output's spending conditions.

| Component     | Meaning                                             |
| ------------- | --------------------------------------------------- |
| `wpkh(...)`   | Native SegWit pay-to-witness-public-key-hash output |
| `d09100b8`    | Master key fingerprint                              |
| `84h`         | BIP84 derivation purpose                            |
| `1h`          | Test-network coin type                              |
| `0h`          | Account index 0                                     |
| `/0/0`        | External receiving branch, address index 0          |
| `02de7bc9...` | Public key associated with this output              |

The `h` suffix means hardened derivation.

Your `parent_descs` field contains the broader derivation template:

```
wpkh([d09100b8/84h/1h/0h]tpub.../0/*)
```

The wildcard `*` represents a sequence of child indexes. Bitcoin Core can use this template to derive multiple receiving addresses.

The two descriptors have different purposes:

- `desc` identifies the specific output's spending conditions.
- `parent_descs` identifies the broader descriptor that generated or tracks the output.

The `tpub` is an extended public key for a test-network derivation. It does not itself contain the private key.

## 6. Why do several UTXOs share the same address?

Look at these entries:

```
Address: bcrt1qdnv28jtdl9tsklvusn6890sdm50s6cwj4c7mrq

UTXO A: 2.0 BTC, 3 confirmations
UTXO B: 1.0 BTC, 1 confirmation
UTXO C: 1.2 BTC, 2 confirmations
```

They all refer to the same receiving address, but each has its own `txid` and `vout`.

If these are all the relevant outputs and they remain unspent, the total associated with this address is:

\\[ 2+1+1.2=4.2\text{ BTC} \\]

That is three separate UTXOs, not one 4.2 BTC UTXO.

Likewise, your address `bcrt1qn25...` appears twice, with 3 BTC and 1 BTC, for a combined 4 BTC across those two outputs.

The descriptor paths also reveal that different addresses are being used:

- `/0/0`: external address index 0
- `/0/1`: external address index 1
- `/0/2`: external address index 2
- `/0/5`: external address index 5

These are derivation indexes, not transaction indexes or block heights.

## 7. Verify this directly in Bitcoin Core

Run these commands on the machine hosting your Bitcoin Core regtest node.

### List your UTXOs

```
bitcoin-cli -regtest -rpcwallet=omar listunspent
```

### Calculate the total shown by the command

You can calculate the sum of the default `listunspent` results with Python, using `Decimal` for exact monetary arithmetic:

```
from decimal import Decimalamounts = [    Decimal("3.0"),    Decimal("1.2"),    Decimal("1.0"),    Decimal("1.0"),    Decimal("2.0"),    Decimal("1.0"),    Decimal("1.2"),]total_btc = sum(amounts, Decimal("0"))total_sats = int(total_btc * Decimal("100000000"))print("Total BTC:", total_btc)print("Total satoshis:", total_sats)
```

Expected output:

```
Total BTC: 11.4
Total satoshis: 1140000000
```

This calculation uses the seven entries you pasted. To calculate the live total from Bitcoin Core, retrieve the current RPC response and sum its `amount` fields.

### Inspect one specific transaction

Use the actual transaction ID from your output:

```
bitcoin-cli -regtest getrawtransaction \
  5a8d20808236f6b3c7e4ff27c11ba0ca77ca3560ffeda3b04f25b1d5a538f8f7 \
  true
```

If the transaction is available to the node, this returns its decoded transaction details, including inputs and outputs. If Bitcoin Core reports that the transaction is not found, you may need to query the wallet transaction or use a node with the transaction available.

### Check wallet balance

```
bitcoin-cli -regtest -rpcwallet=omar getbalance
```

The wallet balance and the total of your pasted UTXOs may differ if there are additional outputs, unconfirmed transactions, immature coinbase rewards, or different RPC filters.

## 8. Key Takeaways

1. A UTXO is an individual transaction output that has not yet been spent.
2. `txid` plus `vout` uniquely identifies an output.
3. The `amount` field is denominated in BTC.
4. An address can have multiple UTXOs.
5. `confirmations` measures how deeply the output is included in the active blockchain.
6. Descriptors explain the spending conditions and how wallet addresses are derived.
7. Your seven supplied entries total 11.4 BTC, or 1,140,000,000 satoshis.

## Practice questions

1. What uniquely identifies a UTXO?
2. Why can the same Bitcoin address appear in multiple UTXOs?
3. What is the difference between `spendable` and `solvable`?
4. If you spend a 3 BTC UTXO to pay 1 BTC, what happens to the original output?
5. What does `/0/5` mean in a descriptor derivation path?


-----------------------------------------------------------------------------------------------------------------------------------------------------------------

### wallets transaction history 
# Lab 17 — Wallet Transaction History

Environment: Ubuntu Server + Bitcoin Core + Regtest

Participants: Omar, Sara, Amine, Ahmed

Objective: Learn how to inspect wallet transactions, understand confirmations, identify received and sent funds, and distinguish immature coinbase rewards from spendable bitcoins.

## 1. Introduction

In Bitcoin, the wallet does not simply store a number representing the user's money. It tracks transactions and the unspent transaction outputs (UTXOs) that the wallet can spend.

Bitcoin Core provides RPC commands that allow us to inspect the transaction history associated with a wallet.

In this lab, we will use Omar's wallet as an example. Omar is a miner, Sara receives payments, and Amine sends bitcoins.

### Learning objectives

By the end of this lab, you will be able to:

1. Retrieve wallet transaction history using `listtransactions`.
2. Identify transactions received and sent.
3. Understand transaction confirmations.
4. Inspect transactions since a particular block using `listsinceblock`.
5. Explain immature coinbase rewards.
6. Distinguish wallet transaction history from the current spendable balance.

## 2. Prepare the Bitcoin Core environment

Check the blockchain network:

```
bitcoin-cli -regtest getblockchaininfo
```

Check the loaded wallets:

```
bitcoin-cli -regtest listwallets
```

Check Omar's balance:

```
bitcoin-cli -regtest -rpcwallet=omar getbalance
```

Check the current block height:

```
bitcoin-cli -regtest getblockcount
```

If Omar's wallet is not loaded, load it:

```
bitcoin-cli -regtest loadwallet "omar"
```

If it is already loaded, do not load it again.

## 3. Lab 17.1 — Inspect Wallet Transactions with `listtransactions`

The `listtransactions` RPC returns recent transactions associated with a wallet.

Basic syntax:

```
bitcoin-cli -regtest -rpcwallet=omar listtransactions
```

To display the last 10 entries:

```
bitcoin-cli -regtest -rpcwallet=omar listtransactions "*" 10
```

To display the last 20 entries:

```
bitcoin-cli -regtest -rpcwallet=omar listtransactions "*" 20
```

The command may return JSON entries containing fields such as:

```
[
  {
    "address": "bcrt1...",
    "category": "receive",
    "amount": 2.0,
    "confirmations": 6,
    "txid": "example_transaction_id",
    "time": 1790000000
  }
]
```

This is an illustrative example, not actual output from your node.

### Important fields

| Field           | Meaning                                                              |
| --------------- | -------------------------------------------------------------------- |
| `address`       | Address associated with the wallet transaction, when applicable      |
| `category`      | Transaction classification, such as `receive`, `send`, or `generate` |
| `amount`        | Amount attributed to that wallet entry                               |
| `confirmations` | Number of confirmations associated with the transaction              |
| `txid`          | Transaction identifier                                               |
| `time`          | Transaction timestamp recorded by the wallet                         |

A transaction may generate multiple entries, particularly when a payment has change outputs or involves several wallet outputs. Therefore, do not assume that every entry corresponds to a separate transaction.

### Example: Omar receives 2 BTC

Suppose Amine sends 2 BTC to an address belonging to Omar.

The transaction is included in a block, and Omar's wallet recognizes the output.

Omar runs:

```
bitcoin-cli -regtest -rpcwallet=omar listtransactions "*" 10
```

He sees a `receive` entry with an amount of 2 BTC.

That entry tells Omar that the wallet recognizes a received output. It does not, by itself, establish that every other condition for spending the output has been satisfied.

## 4. Lab 17.2 — Understand Received and Sent Transactions

Bitcoin Core commonly uses transaction categories to describe how an entry relates to a wallet.

### Received transactions

A received entry represents funds received by the wallet.

For example:

- Amine sends 2 BTC to Sara.
- Sara controls the destination address.
- Sara's wallet recognizes the transaction.
- Sara's wallet records the received amount.

Inspect Sara's history:

```
bitcoin-cli -regtest -rpcwallet=sara listtransactions "*" 10
```

### Sent transactions

A sent entry represents funds sent from the wallet.

Suppose Amine sends 2 BTC to Sara and pays a transaction fee.

The transaction could contain:

- An output of 2 BTC to Sara.
- A change output returning the remainder to Amine.
- A transaction fee paid to the miner.

For example, assume Amine spends an input worth 5 BTC, sends 2 BTC to Sara, and receives 2.999 BTC as change.

The transaction fee is:

\\[ 5 - 2 - 2.999 = 0.001\ \text{BTC} \\]

Amine's wallet records the outgoing payment and accounts for the change and fee according to its transaction accounting.

Sara's wallet records the incoming payment.

The same transaction can therefore appear differently in different wallets.

### Important distinction

The amount shown for a sent entry is not necessarily the total amount removed from the wallet's spendable funds. Change outputs may still belong to the sender, and transaction fees must also be considered.

## 5. Lab 17.3 — Understand Confirmations

A Bitcoin transaction begins in the mempool after a node accepts it for relay, assuming it has not yet been confirmed in a block.

When a miner includes the transaction in a block, the transaction receives its first confirmation.

Each additional block built on top of that block increases its confirmation count.

If a transaction is included in block 100:

| Current chain height | Confirmations                        |
| -------------------- | ------------------------------------ |
| 99                   | Not yet included in the active chain |
| 100                  | 1                                    |
| 101                  | 2                                    |
| 102                  | 3                                    |
| 105                  | 6                                    |

For a transaction included in an active-chain block at height \\(H_t\\), when the current tip is \\(H_c\\):

\\[ \text{Confirmations} = H_c - H_t + 1 \\]

This formula assumes the transaction's block is still in the active chain.

### Check confirmations

Use:

```
bitcoin-cli -regtest -rpcwallet=sara listtransactions "*" 10
```

Find the transaction and inspect its `confirmations` field.

You can also inspect a known transaction with:

```
bitcoin-cli -regtest getrawtransaction "TXID" true
```

Replace `TXID` with the actual transaction ID. This RPC requires the transaction to be available to the node, for example through its mempool or transaction index/block context.

### What happens if a transaction has zero confirmations?

It may be in the mempool, waiting to be mined. However, zero confirmations alone do not guarantee that the transaction will be mined, and a wallet may show an unconfirmed transaction before it is included in a block.

On regtest, you can mine a block manually:

```
bitcoin-cli -regtest -rpcwallet=omar getnewaddress
```

Copy the returned address, then mine one block to it:

```
bitcoin-cli -regtest generatetoaddress 1 "YOUR_MINER_ADDRESS"
```

Check the block height again:

```
bitcoin-cli -regtest getblockcount
```

Note: Mining one block does not guarantee that a particular transaction will be included unless that transaction is eligible and selected from the mempool.

## 6. Lab 17.4 — Inspect Transactions Since a Block with `listsinceblock`

The `listsinceblock` RPC helps identify wallet transactions that have occurred since a specified block.

Basic syntax:

```
bitcoin-cli -regtest -rpcwallet=omar listsinceblock
```

You can also provide a block hash:

```
bitcoin-cli -regtest -rpcwallet=omar listsinceblock "BLOCK_HASH"
```

Replace `BLOCK_HASH` with the hash of a block known to the node.

To retrieve a block hash at a specific height:

```
bitcoin-cli -regtest getblockhash 100
```

Use the actual height available on your chain.

Then inspect wallet transactions since that block:

```
bitcoin-cli -regtest -rpcwallet=omar listsinceblock "YOUR_BLOCK_HASH"
```

The response includes fields such as `transactions` and `lastblock`. Depending on the command options and Bitcoin Core version, it may also include removed transactions or other metadata.

### Example

Suppose the current block height is 105, and you want to inspect Omar's wallet activity since block 100.

You obtain the block hash for height 100:

```
bitcoin-cli -regtest getblockhash 100
```

You then pass that hash to `listsinceblock`.

This is useful for monitoring wallet activity over a range of blocks without manually reviewing every historical transaction.

Important: `listsinceblock` is a wallet-history query, not a general-purpose list of every transaction in the blockchain.

## 7. Lab 17.5 — Understand Immature Coinbase Rewards

A coinbase transaction is a special transaction created by a miner to claim the block subsidy and, where applicable, transaction fees.

For example, on regtest, Omar mines a block and receives a coinbase reward.

Initially, the reward is immature.

Bitcoin Core requires a coinbase output to reach 100 confirmations before it can be spent. This maturity rule applies to regtest as well as the other standard Bitcoin networks.

### Why does coinbase maturity exist?

It helps protect against the consequences of reorganizations affecting recently mined blocks.

If a recently mined block is removed from the active chain, the coinbase reward associated with that block cannot simply remain spendable as if the block had never been invalidated.

### Check immature coinbase funds

Run:

```
bitcoin-cli -regtest -rpcwallet=omar getbalances
```

An example response may contain:

```
{
  "mine": {
    "trusted": 0.0,
    "untrusted_pending": 0.0,
    "immature": 50.0
  }
}
```

This is an illustrative example. Your actual values depend on the blocks mined, the wallet's coinbase outputs, and the current chain state.

The `immature` amount represents mining rewards that are not yet spendable because they have not matured.

### Mine enough blocks

If Omar mines a coinbase reward, he must wait until it has 100 confirmations before spending it.

In regtest, this can be simulated quickly:

```
bitcoin-cli -regtest generatetoaddress 101 "YOUR_MINER_ADDRESS"
```

Use an address controlled by Omar's miner wallet.

Then check:

```
bitcoin-cli -regtest -rpcwallet=omar getbalances
```

The exact number of spendable bitcoins depends on which blocks were mined, which rewards belong to Omar, and whether he already spent any outputs.

### Important distinction

- A mined reward can appear in the wallet before it is spendable.
- An immature coinbase reward is not equivalent to an ordinary confirmed payment.
- A mature coinbase reward becomes eligible for spending, provided the wallet controls the output and all other transaction rules are satisfied.

## 8. Lab 17.6 — Compare Wallet History and Wallet Balance

Use the following commands:

```
bitcoin-cli -regtest -rpcwallet=omar listtransactions "*" 20
```

```
bitcoin-cli -regtest -rpcwallet=omar getbalance
```

```
bitcoin-cli -regtest -rpcwallet=omar getbalances
```

These commands answer different questions.

| Command            | Purpose                                                                             |
| ------------------ | ----------------------------------------------------------------------------------- |
| `listtransactions` | Shows recent wallet transaction entries                                             |
| `getbalance`       | Reports the wallet's balance according to the RPC's parameters and accounting rules |
| `getbalances`      | Separates balance categories, including trusted, pending, and immature amounts      |

Wallet history is not the same thing as current spendable funds. A wallet may have received bitcoins in the past and later spent them.

### Lab 17 checklist

- Inspected transaction history using `listtransactions`.
- Identified `receive` and `send` entries.
- Checked transaction confirmations.
- Queried history with `listsinceblock`.
- Examined immature coinbase rewards.
- Compared transaction history with the wallet's current balance.

# Lab 18 — Wallet Security Model

Objective: Understand the fundamental Bitcoin concepts that are frequently misunderstood:

```
Address ≠ account
Private key ≠ address
UTXO ≠ balance stored on blockchain
```

These distinctions explain how Bitcoin ownership, payments, and wallet balances actually work.

## 1. Address ≠ Account

### 1.1 What is a Bitcoin address?

A Bitcoin address is an identifier used to specify where a transaction output should be sent.

For example, Sara generates a receiving address:

```
bcrt1qexample...
```

This is a placeholder, not a valid address.

Amine can use Sara's address as the destination of a transaction.

However, the address is not an account in the traditional banking sense.

### 1.2 Why is an address not an account?

In a traditional bank, an account is generally associated with a maintained balance and a transaction ledger managed by the bank.

Bitcoin works differently.

A Bitcoin address does not contain a balance. Instead, the blockchain records transaction outputs, and wallet software identifies which outputs are associated with its keys and scripts.

A single wallet can control many addresses.

For example:

```
                 Sara's Wallet
                       |
          +------------+------------+
          |            |            |
       Address A    Address B    Address C
          |            |            |
       UTXO 1       UTXO 2       UTXO 3
```

Sara might use one address to receive a payment from Amine and another address for a later payment from Omar.

Her wallet can track funds associated with all these addresses.

### 1.3 Why does Bitcoin use multiple addresses?

Using separate receiving addresses can improve privacy by making it harder for outside observers to associate every payment with the same identity.

However, address reuse is technically possible, and using different addresses does not guarantee complete privacy.

### 1.4 Verify it in Bitcoin Core

Generate two receiving addresses:

```
bitcoin-cli -regtest -rpcwallet=sara getnewaddress
```

```
bitcoin-cli -regtest -rpcwallet=sara getnewaddress
```

The addresses will normally be different.

Yet both can belong to the same wallet.

Check the wallet's balance:

```
bitcoin-cli -regtest -rpcwallet=sara getbalance
```

The wallet balance aggregates the funds recognized by the wallet; it is not a balance stored inside either individual address.

Conclusion: An address is a destination identifier for a transaction output, not a bank account.

## 2. Private Key ≠ Address

### 2.1 What is a private key?

A private key is a secret number used in Bitcoin's cryptographic system to authorize spending under the corresponding spending conditions.

A Bitcoin address is a different kind of object: an identifier derived through a process involving public keys and, depending on the address type, scripts and hashes.

A simplified relationship is:

```
Private Key
     |
     v
Public Key
     |
     v
Script / Address Derivation
     |
     v
Bitcoin Address
```

The exact process varies by address type. For example, modern SegWit addresses can represent different script constructions, and not all addresses are derived from a public key using one universal formula.

### 2.2 Why are they different?

The private key must remain secret.

The address can be shared publicly to receive funds.

If Sara wants Amine to send her bitcoins, she can share a receiving address. She should never need to give Amine her private key.

If Amine knows Sara's address, he can create a transaction paying that address. He cannot thereby spend Sara's funds.

If Amine obtains Sara's private key or equivalent spending credentials, he may be able to authorize spending of funds controlled by that key.

### 2.3 Example

Suppose Sara receives 2 BTC at an address associated with her wallet.

Amine can see the address and the transaction on the blockchain, but he cannot spend the 2 BTC merely because he knows the address.

Sara's wallet can authorize spending because it has access to the necessary private key or other required signing credentials.

### 2.4 Verify the concept

Generate a receiving address:

```
bitcoin-cli -regtest -rpcwallet=sara getnewaddress
```

Inspect the address:

```
bitcoin-cli -regtest -rpcwallet=sara getaddressinfo "SARA_ADDRESS"
```

Replace `SARA_ADDRESS` with the actual address returned earlier.

Depending on the address and wallet configuration, `getaddressinfo` can show information such as whether the address is associated with the wallet and whether the wallet has the corresponding private key.

Do not export private keys merely to prove that this relationship exists. The RPC output is sufficient to investigate address ownership metadata.

Conclusion: A public address can be shared. A private key must be protected because it can provide the authority needed to spend associated funds.

## 3. UTXO ≠ Balance Stored on Blockchain

This is one of the most important concepts in Bitcoin.

### 3.1 What is a UTXO?

UTXO means Unspent Transaction Output.

When a Bitcoin transaction creates an output, that output can later be used as an input to another transaction, provided it is still unspent and the spending conditions are satisfied.

For example, Amine sends Sara 2 BTC.

The transaction creates an output of 2 BTC to a script associated with Sara's address.

Conceptually:

```
Transaction A
     |
     v
Output: 2 BTC
     |
     v
Sara's Wallet Can Spend It
```

If that output has not yet been spent, it is a UTXO.

### 3.2 Where is the balance?

The blockchain does not maintain a bank-style balance field for every Bitcoin address or wallet.

Instead, the blockchain contains transaction outputs and records which outputs have been spent.

Wallet software determines which unspent outputs it can control and sums their values to calculate a balance.

For example, Sara has three unspent outputs:

| UTXO   | Value    |
| ------ | -------- |
| UTXO 1 | 2 BTC    |
| UTXO 2 | 0.5 BTC  |
| UTXO 3 | 1.25 BTC |
| Total  | 3.75 BTC |

Sara's wallet can report a balance of 3.75 BTC, assuming all three outputs are recognized by the wallet and meet the applicable balance criteria.

The 3.75 BTC is a calculation over relevant outputs, not a balance number stored in a single blockchain account record.

### 3.3 What happens when Sara spends 2 BTC?

Suppose Sara wants to pay Omar 2 BTC and the transaction fee is 0.001 BTC.

She uses the 2 BTC UTXO as an input.

The transaction creates two outputs:

- 1.5 BTC to Omar.
- 0.499 BTC back to Sara as change.

The accounting is:

\\[ 2 = 1.5 + 0.499 + 0.001 \\]

The original 2 BTC UTXO is consumed, and two new UTXOs are created.

```
Before:
Sara's UTXO = 2 BTC

          |
          v

Transaction Input:
        2 BTC

          |
          v

Transaction Outputs:
   +------------------+
   | Omar: 1.500 BTC  |
   | Sara: 0.499 BTC  |
   | Fee:  0.001 BTC  |
   +------------------+
```

The fee is the difference between the total inputs and the total outputs. It is not a separate transaction output.

After the transaction confirms, the original UTXO is no longer available to spend. The new outputs become part of the UTXO set.

### 3.4 Verify UTXOs using Bitcoin Core

Inspect Sara's spendable outputs:

```
bitcoin-cli -regtest -rpcwallet=sara listunspent
```

The response can contain fields such as:

- `txid`: transaction containing the output.
- `vout`: index of the output within that transaction.
- `address`: associated address, when applicable.
- `amount`: output value.
- `confirmations`: number of confirmations.
- `spendable`: whether the wallet considers the output spendable.
- `solvable`: whether the wallet knows how to satisfy the spending conditions, which does not necessarily mean it has the private keys needed to sign.

Each UTXO is identified by the combination of its transaction ID and output index:

```
(txid, vout)
```

Two outputs in the same transaction can have different `vout` values and therefore represent distinct UTXOs.

### 3.5 Verify the wallet's aggregate balance

Run:

```
bitcoin-cli -regtest -rpcwallet=sara getbalances
```

Compare the reported balance categories with the outputs returned by `listunspent`.

Do not expect a simple sum of every listed output to match every wallet balance field in every situation. Confirmations, trust status, immature coinbase outputs, locked outputs, and other wallet accounting rules can affect the comparison.

Conclusion: Bitcoin records transaction outputs and their spending status. A wallet calculates its balance from the outputs it recognizes and can control.

## 4. How the Three Concepts Fit Together

Let's connect the three concepts using a single transaction.

Amine sends 2 BTC to Sara.

1. Sara gives Amine a receiving address.
2. Amine creates a transaction paying that address.
3. The transaction creates an output worth 2 BTC.
4. Once included in the active blockchain, that output can become a UTXO.
5. Sara's wallet recognizes the output and includes it in its balance according to the wallet's accounting rules.
6. Sara can spend it if she has the necessary signing authority and the output is eligible to spend.

The key distinctions are:

| Concept        | What it represents                                                      | What it does not represent                                          |
| -------------- | ----------------------------------------------------------------------- | ------------------------------------------------------------------- |
| Address        | A destination identifier associated with spending conditions            | A bank account with its own stored balance                          |
| Private key    | Secret cryptographic material used to authorize spending                | A public receiving address                                          |
| UTXO           | An unspent transaction output recorded on the blockchain                | A wallet's total balance                                            |
| Wallet balance | An amount calculated by wallet software under specific accounting rules | A single balance field maintained by the blockchain for that wallet |

## 5. Lab 18 — Practical Security Exercises

### Exercise 1 — Address ownership

Generate two addresses in Sara's wallet:

```
bitcoin-cli -regtest -rpcwallet=sara getnewaddress
bitcoin-cli -regtest -rpcwallet=sara getnewaddress
```

Explain why two different addresses can belong to the same wallet.

### Exercise 2 — Address metadata

Run:

```
bitcoin-cli -regtest -rpcwallet=sara getaddressinfo "SARA_ADDRESS"
```

Identify the fields that help establish whether the wallet recognizes the address and has the necessary private key information.

### Exercise 3 — Inspect UTXOs

Run:

```
bitcoin-cli -regtest -rpcwallet=sara listunspent
```

Record the transaction ID, output index, amount, confirmations, and spendability status of each output.

### Exercise 4 — Compare with the wallet balance

Run:

```
bitcoin-cli -regtest -rpcwallet=sara getbalances
```

Explain why the wallet balance is not simply a value stored inside a Bitcoin address.

### Exercise 5 — Analyze a payment

Suppose Sara has one UTXO worth 3 BTC. She sends Omar 1 BTC and pays a 0.001 BTC fee.

Calculate the change output:

\\[ \text{Change} = 3 - 1 - 0.001 \\]

The change is 1.999 BTC.

Explain why the original 3 BTC UTXO is consumed and why the change is represented by a new output.

## 6. Final Knowledge Check

1. Can one Bitcoin wallet control multiple receiving addresses?
2. Why can someone who knows a receiving address not automatically spend the associated funds?
3. What information identifies a particular UTXO?
4. What happens to an input UTXO after a transaction spends it?
5. Why can a wallet's reported balance differ from the sum of all outputs visible in a basic transaction-history query?
6. What is the difference between a transaction confirmation and a UTXO?
7. Why is a change output not the same as returning money to a bank account?
8. Why should private keys never be shared when requesting a payment?

Final takeaway: Bitcoin uses keys and spending conditions to authorize transactions, addresses to identify destinations, and UTXOs to represent spendable outputs. Wallets interpret those outputs and calculate balances; the blockchain does not maintain conventional bank accounts.

# Understanding Your Bitcoin Core `listtransactions` Output

Your output is an excellent example for Lab 17 because it shows three important things happening in your regtest wallet:

- Three outgoing payments (`send`).
- One immature mining reward (`immature`).
- Three confirmations for all four entries, meaning they are associated with block 104, which currently has three confirmations.

Let's analyze each part and connect it to Bitcoin's UTXO model.

## 1. Overview of your transactions

| Entry | Category   | Amount           | Confirmations | Meaning                                  |
| ----- | ---------- | ---------------- | ------------- | ---------------------------------------- |
| 1     | `send`     | −1 BTC           | 3             | Outgoing payment                         |
| 2     | `send`     | −1 BTC           | 3             | Outgoing payment                         |
| 3     | `send`     | −2 BTC           | 3             | Outgoing payment                         |
| 4     | `immature` | +50.00000425 BTC | 3             | Coinbase mining reward not yet spendable |

The three outgoing entries represent 4 BTC in total payments, excluding fees. The recorded fees add another small cost.

The immature reward is separate from those payments. Even though the wallet recognizes it, you cannot spend it yet.

One important detail: the first three entries have different transaction IDs (`txid`), so they represent three distinct transactions, not three outputs of the same transaction.

## 2. Understand the `send` entries

Let's examine your first transaction:

```
{
  "address": "bcrt1qzxkml4yqfk006wqpj0js3kj6lwya95l3pqax7a",
  "category": "send",
  "amount": -1.00000000,
  "vout": 1,
  "fee": -0.00000141,
  "confirmations": 3,
  "blockheight": 104,
  "txid": "ad96aa0449defa5dc2955aa43aa51c5005a0217479b98a1a535ffe04eada0508"
}
```

### What does each field mean?

- `category: send` — Bitcoin Core classifies this wallet entry as an outgoing payment.
- `amount: -1.00000000` — The wallet sent 1 BTC to the associated destination.
- `fee: -0.00000141` — The transaction fee was 0.00000141 BTC, or 141 satoshis.
- `vout: 1` — The associated output has index 1 in the transaction. This is an output index, not a confirmation count.
- `confirmations: 3` — The transaction has three confirmations.
- `blockheight: 104` — The transaction was included in block 104.
- `blockhash` — Identifies the block containing the transaction.
- `txid` — Identifies the transaction.
- `wtxid` — Identifies the transaction including its witness data, where applicable.
- `bip125-replaceable: no` — Bitcoin Core does not currently classify this transaction as BIP125-replaceable.

### How much did the wallet spend?

For this transaction:

\\[ \text{Wallet cost}=1+0.00000141 \\]

\\[ \boxed{1.00000141\ \text{BTC}} \\]

The recipient receives 1 BTC, while the fee is paid to the miner who includes the transaction in a block.

Your other two outgoing entries follow the same principle.

| Payment       | Amount sent | Fee            | Total wallet cost |
| ------------- | ----------- | -------------- | ----------------- |
| Transaction 1 | 1 BTC       | 0.00000141 BTC | 1.00000141 BTC    |
| Transaction 2 | 1 BTC       | 0.00000143 BTC | 1.00000143 BTC    |
| Transaction 3 | 2 BTC       | 0.00000141 BTC | 2.00000141 BTC    |
| Total         | 4 BTC       | 0.00000425 BTC | 4.00000425 BTC    |

These totals assume the three entries are distinct outgoing transactions as shown in your data.

Notice that `amount` and `fee` are both negative in the wallet history. This is how Bitcoin Core represents their effects on the sending wallet; the fee is not included in the displayed payment amount.

## 3. Why do all transactions have three confirmations?

Your transactions contain:

```
{
  "blockheight": 104,
  "confirmations": 3
}
```

The confirmation formula is:

\\[ C=H\_{\text{current}}-H\_{\text{transaction}}+1 \\]

Therefore:

\\[ 3=H\_{\text{current}}-104+1 \\]

\\[ H\_{\text{current}}=106 \\]

Assuming block 104 is still in the active chain, your node's current tip is therefore block 106.

The sequence is:

```
Block 104: Transaction included — 1 confirmation
Block 105: Next block mined      — 2 confirmations
Block 106: Next block mined      — 3 confirmations
```

Your payments are confirmed. In regtest, you can mine additional blocks manually, unlike waiting for natural block production on Bitcoin mainnet.

## 4. The most interesting entry: `immature`

Now examine your mining reward:

```
{
  "address": "bcrt1qx0nzng3t24l8e6kj0xqv845d23wl6mghrlzlnl",
  "category": "immature",
  "amount": 50.00000425,
  "confirmations": 3,
  "generated": true,
  "blockheight": 104,
  "blockindex": 0,
  "parent_descs": [
    "wpkh([7bdf6d3c/84h/1h/0h]tpub.../0/*)#6mfnu2jl"
  ]
}
```

This is a coinbase transaction, created by the miner of block 104.

### Why is the amount 50.00000425 BTC rather than exactly 50 BTC?

Look at the fees from your three outgoing transactions:

\\[ 0.00000141+0.00000143+0.00000141 =0.00000425\ \text{BTC} \\]

Now compare that with the mining reward:

\\[ 50+0.00000425=50.00000425\ \text{BTC} \\]

The amounts match exactly!

Your miner's coinbase output contains:

- 50 BTC — the block subsidy under the current regtest subsidy schedule.
- 0.00000425 BTC — the transaction fees collected from the transactions included in that block.

The miner claims the subsidy and transaction fees through the coinbase transaction.

This is a useful example of how transaction fees flow through the Bitcoin system.

### Why is the reward still immature?

The entry has:

```
"category": "immature",
"confirmations": 3,
"generated": true
```

Bitcoin Core enforces a coinbase maturity requirement of 100 confirmations before a coinbase output can be spent.

Your reward has only three confirmations, so it is not yet spendable.

\\[ 100-3=97 \\]

You need 97 additional confirmations for this particular reward to reach 100 confirmations, assuming it remains in the active chain.

On regtest, you can mine the required additional blocks to an address controlled by your miner wallet:

```
bitcoin-cli -regtest generatetoaddress 97 "YOUR_MINER_ADDRESS"
```

Replace the placeholder with an actual address belonging to your miner wallet. Then check:

```
bitcoin-cli -regtest -rpcwallet=omar getbalances
```

Use the actual wallet name associated with this coinbase output if it is not Omar's.

Important: The reward is not lost or invalid. It is simply subject to the coinbase maturity rule. Reaching 100 confirmations makes it eligible to be spent, assuming the output is otherwise valid and spendable.

## 5. What does `parent_descs` mean?

Your coinbase entry contains a descriptor:

```
wpkh([7bdf6d3c/84h/1h/0h]tpub.../0/*)#6mfnu2jl
```

This provides information about how the wallet derives the relevant address.

- `wpkh(...)` — Describes a native SegWit pay-to-witness-public-key-hash script.
- `7bdf6d3c` — An example of a key-origin fingerprint identifying the originating key hierarchy.
- `84h/1h/0h` — A derivation path associated with the BIP84 convention, using hardened derivation levels.
- `tpub...` — A placeholder for an extended public key used for deriving addresses on a test network.
- `/0/*` — Represents an external address derivation branch and a wildcard for successive address indexes.
- `#6mfnu2jl` — The descriptor checksum.

The actual output contains a complete extended public key, but it has been shortened above for explanation.

This connects directly to Lab 15: descriptors help Bitcoin Core understand how wallet addresses and scripts are derived. An extended public key can support address derivation without providing the private key needed to spend the funds.

## 6. Verify the transactions directly

You can inspect the block that contains all these entries:

```
bitcoin-cli -regtest getblock \
"1112fab8d459c3d89d2ca17da4e6a37502bc200d5a9966c5c9cefd912da31c83" 2
```

The `2` requests decoded transaction details in the block output.

To check the current chain height:

```
bitcoin-cli -regtest getblockcount
```

To inspect the miner wallet's balance categories:

```
bitcoin-cli -regtest -rpcwallet=omar getbalances
```

To inspect individual spendable outputs:

```
bitcoin-cli -regtest -rpcwallet=omar listunspent
```

These commands let you compare transaction history, coinbase maturity, and the wallet's current spendable outputs.

## 7. Final conclusions

Your output demonstrates three fundamental Bitcoin mechanisms:

1. Outgoing payments: A wallet records the payment amount and the transaction fee separately.
2. Confirmations: A transaction included in block 104 has three confirmations if the active chain tip is block 106.
3. Coinbase maturity: The miner receives the block subsidy and transaction fees through a coinbase transaction, but the reward cannot be spent until it reaches 100 confirmations.

The particularly useful observation is that your three transaction fees total exactly `0.00000425 BTC`, which explains why the coinbase amount is `50.00000425 BTC`.

### Practice questions

1. Why is the fee negative in the wallet's `send` entry?
2. If the chain tip advances from block 106 to block 110, how many confirmations will the transactions in block 104 have?
3. Why can the miner see a 50.00000425 BTC reward without being able to spend it immediately?
4. What is the difference between the transaction's `vout` and its `blockindex`?
5. Why does an extended public key not, by itself, give the miner the ability to spend the funds?