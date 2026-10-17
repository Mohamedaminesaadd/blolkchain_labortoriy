# What is a script in Bitcoin?

In Bitcoin, a script is a small program that defines the conditions for spending a transaction output.

Bitcoin uses a scripting language called Bitcoin Script. It is stack-based and intentionally limited: it allows nodes to verify that a transaction satisfies the spending conditions without running arbitrary programs.

For example, when Amine sends 1 BTC to Sara, Bitcoin creates an output with conditions that Sara's wallet must satisfy to spend those funds.

## 1. Where does the script appear in a transaction?

In your Regtest lab, you saw this field in the transaction output:

```
{
  "value": 1.0,
  "n": 1,
  "scriptPubKey": {
    "asm": "0 11adbfd4804d9efd380193e508da5afb89d2d3f1",
    "hex": "001411adbfd4804d9efd380193e508da5afb89d2d3f1",
    "address": "bcrt1qzxkml4yqfk006wqpj0js3kj6lwya95l3pqax7a",
    "type": "witness_v0_keyhash"
  }
}
```

The `scriptPubKey` is the locking script, which defines the conditions for spending this output.

There are two important script-related fields:

- `scriptPubKey`: the spending conditions attached to an output.
- `scriptSig`: unlocking data provided by an input in legacy transactions. In your native SegWit transaction, it is empty, and the signature and public key are supplied in `txinwitness`.

## 2. How your native SegWit script works

Your output has the script:

```
001411adbfd4804d9efd380193e508da5afb89d2d3f1
```

This is a P2WPKH output, meaning Pay-to-Witness-Public-Key-Hash.

Locking script (`scriptPubKey`)

Stores a 20-byte public-key hash in a version-0 witness program

Spending input (`txinwitness`)

Provides a signature and public key

Validation

Bitcoin checks the public-key hash and verifies the signature

If the conditions are satisfied, the input can validly spend the UTXO. Other transaction rules must also be satisfied for the transaction to be valid.

## 3. What do the bytes mean?

Your script is:

```
00 14 11adbf...a5afb89d2d3f1
```

| Bytes              | Meaning                                |
| ------------------ | -------------------------------------- |
| `00`               | Witness version 0                      |
| `14`               | Push the following 20 bytes            |
| Remaining 20 bytes | The witness program: a public-key hash |

This is a standard SegWit output. The script does not directly contain Sara's private key or signature. Those are used when spending the output.

## 4. What happens when Sara spends this UTXO?

In your earlier transaction, you saw:

```
{
  "scriptSig": {
    "asm": "",
    "hex": ""
  },
  "txinwitness": [
    "3044...",
    "02d7..."
  ]
}
```

The witness contains two items:

1. A signature proving authorization to spend the output.
2. The public key whose hash must match the output's witness program.

Bitcoin validates the signature against the transaction being spent and checks that the public key matches the required hash.

This is why your `scriptSig` is empty: native SegWit P2WPKH uses the witness field for the signature and public key.

## 5. Inspect the script in your lab

You can retrieve a specific output directly:

```
bitcoin-cli -regtest gettxout \
  ad96aa0449defa5dc2955aa43aa51c5005a0217479b98a1a535ffe04eada0508 \
  1
```

Look at the returned `scriptPubKey` object. It describes the conditions attached to Sara's 1 BTC output.

Remember: the UTXO is the unspent amount plus its spending conditions. The script defines those conditions; the wallet uses its keys to satisfy them when creating a valid spending transaction.
------------------------------------------------------------

```
{
  "bestblock": "02de28fe056abe1c4aca26a9b6ce4bbf35c898bbd053bb46aa3593280289dfe7",
  "confirmations": 5,
  "value": 1.00000000,
  "scriptPubKey": {
    "asm": "0 11adbfd4804d9efd380193e508da5afb89d2d3f1",
    "desc": "addr(bcrt1qzxkml4yqfk006wqpj0js3kj6lwya95l3pqax7a)#3nnkg62x",
    "hex": "001411adbfd4804d9efd380193e508da5afb89d2d3f1",
    "address": "bcrt1qzxkml4yqfk006wqpj0js3kj6lwya95l3pqax7a",
    "type": "witness_v0_keyhash"
  },
  "coinbase": false
}

```


Let's simplify it using your Bitcoin Regtest lab with Amine and Sara.

# 1. What is the Bitcoin Script?

Imagine Amine wants to send 1 BTC to Sara. Bitcoin must record not only the amount but also the conditions under which that money can be spent.

For example:

> "This 1 BTC can be spent only by someone who can provide the correct public key and a valid signature."

That rule is encoded in a Bitcoin Script called the locking script (`scriptPubKey`).

## 2. How it works

Step 1 — Amine sends 1 BTC

Bitcoin creates a transaction output.

Step 2 — Bitcoin locks the output

The locking script specifies the spending conditions.

Step 3 — Sara wants to spend it

Her wallet supplies a signature and public key in the witness.

Step 4 — Bitcoin validates the spend

If the required conditions and other transaction rules are satisfied, the spend is valid.

## 3. Connect this to your real transaction

You previously captured this script in Sara's transaction:

```
001411adbfd4804d9efd380193e508da5afb89d2d3f1
```

This is a native SegWit P2WPKH locking script.

- `00` indicates witness version 0.
- `14` indicates that the following data contains 20 bytes.
- The remaining 20 bytes are the public-key hash that the spending public key must match.

The script doesn't contain Sara's private key. Her wallet uses the private key to generate a signature when spending the output.

## 4. Why did your transaction have `scriptSig` and `txinwitness`?

Your decoded transaction showed:

```
{
  "scriptSig": {
    "asm": "",
    "hex": ""
  },
  "txinwitness": [
    "signature...",
    "public_key..."
  ]
}
```

Because your output uses native SegWit, the signature and public key are supplied in `txinwitness`, while `scriptSig` is empty.

The essential difference:

- `scriptPubKey` defines the conditions for spending an output.
- `txinwitness` supplies the data needed to satisfy those conditions for your SegWit input.
- `vin` identifies the previous output being spent.
- `vout` creates the new outputs.

One final point: Bitcoin Script is not a general-purpose language like Python. It is designed to validate spending conditions, such as signatures, hashes, and certain spending constraints.


You can do this in your Bitcoin Regtest lab, but there is an important distinction: Bitcoin Script cannot directly require Sara to send you an image. Bitcoin nodes do not inspect images or verify that someone has sent one through a messaging app.

You can, however, build a lab where Sara's Bitcoin is locked until a specified condition is met, and use a Python application to check whether the image has been received before allowing a transaction to proceed.

## 1. Two possible designs

Option A — Bitcoin-native condition

Lock BTC using a script that requires a secret or a valid signature. You release the secret only after receiving the image. Sara uses it to spend the output.

Bitcoin can verify the secret or signature, but cannot verify the image itself.

Option B — Python application + Bitcoin Core

Your application receives the image, verifies that it meets your criteria, and then authorizes the next step in the Bitcoin transaction workflow.

The image check is performed by your application, not by Bitcoin consensus rules.

## 2. Recommended architecture for your Regtest lab

Sara

Sends the image to your application

Python verification service

Checks image receipt and the required criteria

Authorization condition

If satisfied, your application enables the next step

Bitcoin Core — Regtest

Broadcast or confirm the authorized transaction

## 3. What if you want the Bitcoin output itself to enforce the condition?

You can use a hashlock. The output is locked to a cryptographic hash, and spending it requires revealing a secret whose hash matches the one specified in the script.

Conceptually:

```
IF SHA256(secret) == expected_hash:
    allow spending
```

This is only a conceptual description, not valid Bitcoin Script syntax. A real script must use Bitcoin Script opcodes and correctly handle the spending stack.

The important limitation is that the secret proves knowledge of a value, not that Sara sent an image. Your application could release the secret after verifying the image.

## One question before we implement it

Do you want to build:

- A. A Bitcoin Script experiment using a hashlock and a secret.
- B. A Python application that checks whether Sara has sent an image and then controls the transaction workflow.
- C. Both, combining Bitcoin Script with Python verification.

I recommend C for your Regtest lab because it demonstrates both on-chain spending conditions and off-chain application logic.