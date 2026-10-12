# Bitcoin Lab — Wallets, Private Keys, Public Keys, and Addresses

In this lab, you will learn how Bitcoin addresses are generated, how to inspect them using `bitcoin-cli`, and how to distinguish the four main address types: P2PKH, P2SH, Bech32, and Bech32m.

We will use your Bitcoin Core 31.1 installation on Ubuntu with the `regtest` network.

## 1. Understand the relationship between keys and addresses

A Bitcoin wallet manages cryptographic keys and can generate addresses that others use to send bitcoin to you.

The basic relationship is:

```
Private Key
    |
    | Elliptic-curve cryptography
    v
Public Key
    |
    | Hashing and/or script construction
    v
Bitcoin Address
```

An address is not the bitcoin itself. It represents a destination to which a transaction can pay.

### 1.1. Private key

A private key is a secret number used to authorize spending bitcoin associated with the corresponding locking conditions.

- It must remain secret.
- It is used to generate a public key.
- In common single-key spending schemes, it enables you to produce the required digital signature.
- Anyone who obtains the private key may be able to spend the funds it controls.

Conceptually, a private key is a number selected from a very large valid range.

Never share a real wallet's private key or seed phrase. For this lab, use your regtest wallet and never reuse its test keys for real funds.

### 1.2. Public key

A public key is derived mathematically from the private key using the elliptic curve `secp256k1`.

- It can be shared publicly.
- It is used to verify signatures or participate in other Bitcoin spending conditions.
- It is not the same thing as a Bitcoin address.

For common ECDSA-based Bitcoin spending, a signature proves control of the private key without revealing that private key.

### 1.3. Bitcoin address

A Bitcoin address is a human-readable representation of a payment destination.

Depending on the address type, it can be derived from a public-key hash, a script hash, or a witness program.

For example, a wallet may generate an address and give it to another person, who uses it as the destination in a transaction.

The recipient's wallet can later recognize and spend outputs that satisfy the associated spending conditions.

Important: The simple private key → public key → address diagram is a useful introduction, but not every address directly encodes a public key. Some encode a hash or a witness program, and modern script-based wallets can have more complex spending conditions.

## 2. Lab setup — Open your Bitcoin wallet

First, check that Bitcoin Core is running in regtest mode:

```
/opt/bitcoin/bin/bitcoin-cli -regtest getblockchaininfo
```

List the wallets currently loaded:

```
/opt/bitcoin/bin/bitcoin-cli -regtest listwallets
```

If your wallet is named `amine`, use wallet-specific commands with `-rpcwallet=amine`:

```
/opt/bitcoin/bin/bitcoin-cli -regtest -rpcwallet=amine getwalletinfo
```

If the wallet is not loaded, load it using:

```
/opt/bitcoin/bin/bitcoin-cli -regtest loadwallet "amine"
```

The wallet must exist before you can load it.

## 3. Generate a Bitcoin address using `getnewaddress`

The `getnewaddress` RPC generates a new receiving address controlled by your wallet.

### 3.1. Generate a default address

Run:

```
/opt/bitcoin/bin/bitcoin-cli -regtest -rpcwallet=amine getnewaddress
```

Example output:

```
bcrt1qexample...
```

This is only an illustrative placeholder, not a real address.

Bitcoin Core will generate a new address using the wallet's default address type. For a standard modern wallet, this is generally a native SegWit address.

Save the address returned by your own command.

### 3.2. Generate an address with a label

You can associate an address with a label to identify its purpose:

```
/opt/bitcoin/bin/bitcoin-cli -regtest -rpcwallet=amine getnewaddress "Amine receiving address"
```

The label is wallet metadata. It does not change the cryptographic security of the address.

### 3.3. Generate each address type

Bitcoin Core allows you to request different address types explicitly:

```
# P2PKH — Legacy
/opt/bitcoin/bin/bitcoin-cli -regtest -rpcwallet=amine getnewaddress "Legacy" "legacy"

# P2SH-wrapped SegWit
/opt/bitcoin/bin/bitcoin-cli -regtest -rpcwallet=amine getnewaddress "Wrapped SegWit" "p2sh-segwit"

# Bech32 — Native SegWit
/opt/bitcoin/bin/bitcoin-cli -regtest -rpcwallet=amine getnewaddress "Native SegWit" "bech32"

# Bech32m — Taproot
/opt/bitcoin/bin/bitcoin-cli -regtest -rpcwallet=amine getnewaddress "Taproot" "bech32m"
```

Each command generates a different receiving address. Your wallet keeps the relevant key or script information.

## 4. Inspect an address using `getaddressinfo`

The `getaddressinfo` RPC returns information about an address, including whether your wallet recognizes it and whether it has associated private-key information.

Run:

```
/opt/bitcoin/bin/bitcoin-cli -regtest -rpcwallet=amine getaddressinfo "YOUR_ADDRESS"
```

Replace `YOUR_ADDRESS` with the complete address returned by `getnewaddress`.

Important fields include:

| Field          | Meaning                                                                                                                                      |
| -------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| `address`      | The address being inspected.                                                                                                                 |
| `scriptPubKey` | The locking script associated with the address.                                                                                              |
| `ismine`       | Whether the wallet considers the address's spending conditions to be under its control.                                                      |
| `iswatchonly`  | Whether the wallet watches the address without having the necessary spending authority.                                                      |
| `solvable`     | Whether the wallet knows enough about the spending conditions to construct a spending transaction, possibly without having the signing keys. |
| `ischange`     | Whether the wallet identifies the address as a change address.                                                                               |
| `pubkey`       | Public key, when available for that address.                                                                                                 |
| `iscompressed` | Whether the reported public key uses compressed encoding, when applicable.                                                                   |
| `desc`         | Output descriptor describing the address's spending conditions, when available.                                                              |

Not every field appears for every address type or wallet configuration.

For example, `pubkey` may be absent for an address that represents a script hash. Also, `ismine: true` does not mean the address currently contains bitcoin; it indicates wallet ownership of the relevant spending conditions.

## 5. Bitcoin address types

Bitcoin has several address formats. They differ in how spending conditions are represented, how addresses are encoded, and which transaction output scripts they correspond to.

### 5.1. P2PKH — Pay to Public Key Hash

P2PKH is the traditional Bitcoin address format.

- Mainnet addresses usually begin with `1`.
- Regtest addresses usually begin with `m` or `n`.
- The address represents a hash of a public key.
- Spending typically requires a public key and a valid signature.

Example structure:

```
Mainnet:  1...
Regtest:  m... or n...
```

The corresponding output script typically looks like:

```
OP_DUP OP_HASH160 <public-key-hash>
OP_EQUALVERIFY OP_CHECKSIG
```

P2PKH is commonly called a Legacy address.

### 5.2. P2SH — Pay to Script Hash

P2SH allows bitcoin to be locked to the hash of a script rather than directly to a public-key hash.

- Mainnet addresses usually begin with `3`.
- Regtest addresses usually begin with `2`.
- The spending transaction must provide the script and satisfy its conditions.
- It can support multisignature arrangements and wrapped SegWit.

Example structure:

```
Mainnet:  3...
Regtest:  2...
```

A P2SH address does not necessarily mean multisignature. It can represent different kinds of scripts.

In Bitcoin Core, the address type `p2sh-segwit` specifically generates a P2SH-wrapped SegWit address.

### 5.3. Bech32 — Native SegWit

Bech32 is the encoding used for native SegWit version 0 addresses.

- Mainnet addresses begin with `bc1q`.
- Regtest addresses begin with `bcrt1q`.
- It supports SegWit v0 outputs, including P2WPKH and P2WSH.
- SegWit can reduce transaction weight and improve transaction efficiency.

Example structure:

```
Mainnet:  bc1q...
Regtest:  bcrt1q...
```

A P2WPKH address represents a witness program containing a public-key hash. The spending transaction provides the required signature and public key through the witness data.

### 5.4. Bech32m — Taproot

Bech32m is the address encoding introduced for SegWit witness version 1 and later versions.

For Bitcoin's Taproot addresses:

- Mainnet addresses begin with `bc1p`.
- Regtest addresses begin with `bcrt1p`.
- Taproot uses SegWit version 1.
- A typical Taproot output locks funds to a 32-byte witness program representing a Taproot output key.

Example structure:

```
Mainnet:  bc1p...
Regtest:  bcrt1p...
```

Taproot supports key-path spending and script-path spending. It can improve privacy and efficiency for certain spending conditions.

Important distinction: Bech32 and Bech32m are encoding formats, whereas P2PKH and P2SH describe output-script types. They are related concepts, but they are not all the same kind of classification.

## 6. Compare the four address types

| Feature             | P2PKH       | P2SH              | Bech32         | Bech32m               |
| ------------------- | ----------- | ----------------- | -------------- | --------------------- |
| Common name         | Legacy      | Script Hash       | Native SegWit  | Taproot encoding      |
| Mainnet prefix      | `1`         | `3`               | `bc1q`         | `bc1p`                |
| Regtest prefix      | `m` / `n`   | `2`               | `bcrt1q`       | `bcrt1p`              |
| Typical output type | P2PKH       | P2SH              | P2WPKH / P2WSH | P2TR                  |
| Witness version     | None        | Depends on script | Version 0      | Version 1 for Taproot |
| Encoding            | Base58Check | Base58Check       | Bech32         | Bech32m               |

## 7. How the address is used in a Bitcoin transaction

Suppose Amine wants Sara to receive 2 BTC on a network where those amounts are available.

The process is conceptually:

```
1. Sara generates a receiving address
                 |
                 v
2. Sara sends the address to Amine
                 |
                 v
3. Amine creates a transaction paying that address
                 |
                 v
4. The transaction creates a new UTXO
   with a scriptPubKey matching the destination
                 |
                 v
5. Sara's wallet recognizes the output
                 |
                 v
6. Sara later spends the UTXO by satisfying
   its spending conditions
```

In your regtest lab, you can inspect the address, send test bitcoin, and inspect the resulting transaction. Remember that regtest bitcoin has no real-world monetary value.

## 8. Practice exercises

1. Generate one address of each type using `getnewaddress`.
2. Run `getaddressinfo` on each address and compare `scriptPubKey`, `ismine`, and `desc`.
3. Why is a Bitcoin address not the same thing as a public key?
4. What is the difference between a P2SH-wrapped SegWit address and a native SegWit address?
5. Why does Bitcoin use Bech32m for Taproot addresses instead of Bech32?


----------------------------------------------------------------------------
Yes. The address type you use depends on the situation, but for most new Bitcoin transactions, you should generally prefer a native SegWit address (Bech32) or a Taproot address (Bech32m).

The best choice depends on compatibility, transaction fees, wallet support, and the spending conditions you need.

## 1. When should you use each address type?

### P2PKH — Legacy

Address prefix: `1` on mainnet.

Use it when:

- You need compatibility with older Bitcoin wallets or services.
- An application does not support SegWit addresses.

Advantages: Widely supported.

Disadvantages: Generally larger and more expensive transactions than equivalent native SegWit transactions.

### P2SH — Script Hash

Address prefix: `3` on mainnet.

Use it when:

- You need a script-based spending arrangement, such as multisignature.
- You need compatibility with P2SH-wrapped SegWit wallets.

Advantages: Supports flexible scripts and wrapped SegWit.

Disadvantages: Wrapped SegWit is generally less efficient than native SegWit.

### Bech32 — Native SegWit

Address prefix: `bc1q` on mainnet.

Use it when:

- You want a good default for ordinary Bitcoin payments.
- You want efficient transaction sizes and broad modern-wallet compatibility.

Advantages: Lower transaction weight than equivalent Legacy transactions and native SegWit support.

Disadvantages: Some older wallets and services may not support it.

### Bech32m — Taproot

Address prefix: `bc1p` on mainnet.

Use it when:

- You want to use Taproot-compatible spending conditions.
- Your wallet or application supports Taproot.
- You need Taproot features, such as key-path spending or more advanced script conditions.

Advantages: Supports Taproot features and can improve efficiency or privacy for certain spending arrangements.

Disadvantages: Compatibility can be less universal than native SegWit, and Taproot is not automatically cheaper for every transaction.

## 2. Quick decision table

| Situation                                           | Recommended choice                          |
| --------------------------------------------------- | ------------------------------------------- |
| Ordinary payment between modern wallets             | Bech32                                      |
| Older wallet or service                             | P2PKH, if required                          |
| Existing P2SH-wrapped SegWit setup                  | P2SH                                        |
| Taproot-specific application or spending conditions | Bech32m                                     |
| Unsure which type to choose                         | Use your wallet's default receiving address |

## 3. What happens in your Bitcoin lab?

With Bitcoin Core on your `regtest` network, you can generate different address types for experimentation:

```
bitcoin-cli -regtest -rpcwallet=amine getnewaddress "Legacy" "legacy"
bitcoin-cli -regtest -rpcwallet=amine getnewaddress "Wrapped SegWit" "p2sh-segwit"
bitcoin-cli -regtest -rpcwallet=amine getnewaddress "Native SegWit" "bech32"
bitcoin-cli -regtest -rpcwallet=amine getnewaddress "Taproot" "bech32m"
```

Then you can send test bitcoin to each address and inspect the resulting output script using `getaddressinfo` and `getrawtransaction`.

One important point: the sender's wallet does not normally choose the recipient's address type. The recipient provides an address, and the sender's wallet creates a transaction that pays to it. The sender's wallet must support that destination type.

## 4. My recommendation

For your learning lab, generate all four types so you can compare them. For ordinary real-world payments, use a modern wallet's default address unless you have a specific compatibility or technical reason to choose another type.

### Practice questions

1. Why might a Legacy transaction cost more in fees than an equivalent native SegWit transaction?
2. Can you send bitcoin from a Legacy address to a Bech32 address?
3. Does using a Taproot address automatically make every transaction cheaper or more private?

------------------------------------------------------------------------------------------------------------------------
# Bitcoin Address Types — Detailed Explanation with Examples

Let's answer the three questions step by step using examples from your Bitcoin lab with Amine, Sara, and Omar.

## 1. Why might a Legacy transaction cost more in fees than an equivalent Native SegWit transaction?

The main reason is transaction size and how Bitcoin calculates transaction fees.

### 1.1. How Bitcoin transaction fees work

When Amine sends bitcoin to Sara, his transaction contains information such as:

- The UTXO Amine wants to spend.
- The amount sent to Sara.
- Sara's receiving address, represented in the transaction by a locking script.
- A digital signature proving that Amine is authorized to spend the input.

Bitcoin fees are usually calculated using the transaction's virtual size (vB) and the fee rate.

\\[ \text{Transaction fee}=\text{Virtual size (vB)}\times\text{Fee rate (sat/vB)} \\]

A satoshi is the smallest unit of bitcoin:

\\[ 1\ \text{BTC}=100{,}000{,}000\ \text{satoshis} \\]

### 1.2. Why does Legacy cost more?

A Legacy P2PKH transaction includes its signature and public key in the transaction's traditional input data.

With SegWit, signature-related witness data is stored separately and receives a discount when calculating transaction weight. This often reduces the virtual size of a transaction.

[Introduction to Bitcoin](https://images.openai.com/static-rsc-4/M7gyOCEbRIDNnJHnuYMLgEBnoItNC-yJdQf2mZfVGDKM7zi4OYngillwekbIbxgKiVv3I6GyrZe9Mta_WgFgSXpl35ADtCcDjXi6ukuasZW_flq7hX9mNLNluq0RtRQBrGxh4Vdnc8nnqllotzJaQU_Ea6avZjVw06LZ_OMVGVA?purpose=inline)

Legacy — P2PKH

Signature and public key are included in the input's script data.

Typically larger virtual size for an equivalent single-input, single-output payment.

[Bitcoin Mempool: How It Works & Speed Up Transactions | Bitsgap blog](https://images.openai.com/static-rsc-4/hHddPl39pUlsUuPUkp7O4bYoL9BbUSrDQqo_cZipkTvt6iKeKapBEvo2Ak9COc6_xDxWc_48OkNShCj76BMxJSO5yW7MEiRe_uN2c0c2yLMilF7lZPutR3BClEYeLVpPUxUgX5SNfFVfSWTzcg9fOp6C6RuX-yM-LXrfvo77usM?purpose=inline)

Native SegWit — P2WPKH

Signature and public key are carried in the witness.

Witness data receives a weight discount, often reducing transaction fees.

### 1.3. Numerical example

Suppose Amine sends bitcoin to Sara, and both transactions use a fee rate of 20 sat/vB.

| Transaction   | Illustrative virtual size | Fee rate  | Fee        |
| ------------- | ------------------------- | --------- | ---------- |
| Legacy        | 200 vB                    | 20 sat/vB | 4,000 sats |
| Native SegWit | 140 vB                    | 20 sat/vB | 2,800 sats |

The difference is:

\\[ 4{,}000-2{,}800=1{,}200\text{ sats} \\]

The Native SegWit transaction costs 30% less in this example.

These sizes are illustrative, not fixed values. Actual transaction size depends on the number and types of inputs and outputs.

Important: The recipient's address type also affects the output size. To compare fairly, we assume equivalent payment conditions and transaction structures.

## 2. Can you send bitcoin from a Legacy address to a Bech32 address?

Yes. Legacy and Native SegWit addresses are compatible as payment destinations. They do not need to use the same address format.

### 2.1. Example: Amine sends 2 BTC to Sara

Suppose Amine controls a Legacy UTXO and Sara gives him a Native SegWit receiving address.

Amine — Sender

Spends a UTXO controlled by a Legacy address

Input: 2.001 BTC

Amine signs and broadcasts a transaction

Sara — Recipient

Receives bitcoin at a Native SegWit address

Payment: 2.000 BTC

Illustrative transaction fee

## 0.001 BTC

Input = outputs + fee

The example assumes Amine spends one UTXO worth 2.001 BTC. The transaction creates two outputs:

- 2.000 BTC to Sara.
- 0.000 BTC to Amine as change in this simplified example? No — because the remaining 0.001 BTC is paid as the fee, there is no change output.

The accounting is:

\\[ 2.001=2.000+0.001\text{ BTC} \\]

### 2.2. What happens technically?

1. Sara generates a Bech32 address, usually beginning with `bc1q` on mainnet.
2. Amine selects a spendable UTXO in his wallet.
3. His wallet constructs a transaction with an output script matching Sara's address.
4. Amine's wallet signs the input according to the Legacy UTXO's spending conditions.
5. The transaction is broadcast to the Bitcoin network.
6. Nodes validate the transaction, and miners may include it in a block.
7. Sara's wallet recognizes the output and can later spend it using the corresponding private key and spending conditions.

Notice the key distinction: the input's format determines how Amine spends his existing UTXO; the output's format determines how the bitcoin is locked for Sara.

### 2.3. Try it in your regtest lab

Generate a Native SegWit address for Sara:

```
bitcoin-cli -regtest -rpcwallet=sara getnewaddress "Sara SegWit" "bech32"
```

Copy the returned address. Then, from Amine's wallet, send a test payment:

```
bitcoin-cli -regtest -rpcwallet=amine sendtoaddress "SARA_ADDRESS" 2
```

Replace `SARA_ADDRESS` with the actual address returned by Sara's wallet.

This requires Amine to have sufficient spendable regtest funds and a suitable fee configuration. The transaction may initially remain unconfirmed until a block includes it.

## 3. Does using a Taproot address automatically make every transaction cheaper or more private?

No. Taproot provides capabilities, not automatic guarantees.

Taproot introduced improvements to Bitcoin's spending conditions through Schnorr signatures, Taproot output keys, and more flexible script spending.

### 3.1. Fees: Taproot is not always cheaper

Taproot key-path spending can be efficient because it can use a single Schnorr signature in the witness.

However, transaction fees depend on the whole transaction:

- Number of inputs.
- Number of outputs.
- Input and output types.
- Whether spending uses the key path or script path.
- Current fee rate.

A Taproot transaction involving complex script-path spending may be larger than a simple Native SegWit transaction.

Therefore, you cannot conclude that every Taproot payment costs less than every Bech32 payment.

### 3.2. Privacy: what Taproot does and does not hide

Taproot can improve privacy for certain spending arrangements. For example, a key-path spend does not reveal the alternative script conditions that could have been used.

But Bitcoin remains a public ledger.

Taproot does not automatically hide:

- Transaction amounts.
- Transaction inputs and outputs.
- The history of confirmed transactions.
- All links between addresses and real-world identities.

An observer may still analyze transaction patterns and other public information.

### 3.3. Example: multisignature spending

Imagine Amine and Sara manage funds that require two signatures out of three possible participants.

Without Taproot, certain script arrangements can reveal more about the spending conditions when funds are spent.

With an appropriately designed Taproot arrangement, a cooperative spend may use the key path and appear similar to an ordinary Taproot key-path spend on-chain. If the script path is used instead, the relevant script and proof are revealed, while other unexecuted script branches can remain hidden.

This benefit depends on the wallet design and spending path; merely generating a `bc1p` address does not guarantee that a transaction uses these privacy features.

## 4. Final comparison: Which address should you choose?

| Your situation                                       | Practical choice                                                                             |
| ---------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| Ordinary payment between modern wallets              | Native SegWit (Bech32) is a good default.                                                    |
| Older wallet or service requires Legacy              | P2PKH, if necessary.                                                                         |
| Existing wrapped SegWit or compatibility requirement | P2SH-wrapped SegWit.                                                                         |
| Taproot-specific features or spending conditions     | Taproot (Bech32m), if supported.                                                             |
| Lowest fee is your main concern                      | Compare the actual transaction's estimated virtual size and fee rate.                        |
| Privacy is your main concern                         | Understand the complete transaction and wallet behavior; address type alone is insufficient. |

## 5. Test your understanding

1. If Amine spends a Legacy UTXO to pay Sara's Bech32 address, which address type determines the signature and witness requirements of Amine's input?
2. If two transactions pay the same amount but one has more inputs, why might its fee be higher?
3. If a Taproot transaction uses script-path spending, what information might become visible on-chain that a key-path spend would not reveal?


