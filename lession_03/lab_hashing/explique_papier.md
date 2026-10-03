Let's take a complete example of SHA-256 processing a message that produces exactly 3 blocks, and follow the process from the original message to the final digest.

We will use:

```
message = b"A" * 120
```

This means the message contains 120 bytes, each equal to the ASCII character `A`.

We will understand:

1. How padding produces 3 blocks.
2. How each block is divided into 16 words.
3. How the first block is processed.
4. How the result of Block 1 becomes the input of Block 2.
5. How Block 3 produces the final digest.

The SHA-256 algorithm and terminology follow NIST FIPS 180-4, Section 6.2.&#x20;

SHA_Documentation_nist.fips.180-4.pdf



# Part 1 — Understand the original message

Our message:

```
AAAAAAAAAAAAAAAAAAAAAAAA...
```

It contains:

\\[ L=120\times8=960\text{ bits} \\]

Remember:

- 1 byte = 8 bits
- 1 SHA-256 block = 512 bits
- 1 SHA-256 block = 64 bytes
- 1 block = 16 words of 32 bits

Therefore, the original message occupies:

\\[ \frac{120}{64}=1.875\text{ blocks} \\]

We cannot process a partial block directly. We must apply SHA-256 padding.

# Part 2 — Apply SHA-256 padding

The padding format is:

\\[ M\\; ||\\; 1\\; ||\\; 0^k\\; ||\\; [L]\_{64} \\]

Where:

- \\(M\\): original message
- \\(1\\): one appended bit
- \\(0^k\\): zero bits
- \\([L]\_{64}\\): original message length encoded using 64 bits

The condition is:

\\[ L+1+k\equiv448\pmod{512} \\]

For our example:

\\[ 960+1+k\equiv448\pmod{512} \\]

The next suitable value is:

\\[ 960+1+511=1472 \\]

Therefore:

\\[ k=511 \\]

Then append the 64-bit length:

\\[ 1472+64=1536\text{ bits} \\]

Finally:

\\[ \frac{1536}{512}=\boxed{3\text{ blocks}} \\]

## Visual representation

## Padded message: 192 bytes

Block 1

64 bytes

Original message — bytes 0–63

Block 2

64 bytes

56 message bytes

1

0s

Bytes 64–119 are message data; byte 120 is 0x80; then seven zero bytes.

Block 3

64 bytes

56 zero bytes

64-bit length

Last 8 bytes encode 960 bits.

The final length field is:

```
00000000000003C0
```

Because:

\\[ 960\_{10}=3C0\_{16} \\]

# Part 3 — Parse each block into 16 words

Each block is divided into 16 words:

\\[ M_0,M_1,\ldots,M\_{15} \\]

Each word contains 32 bits = 4 bytes.

## Block 1

Our ASCII character `A` has hexadecimal value:

```
A = 0x41
```

Four consecutive `A` characters produce:

```
0x41414141
```

Therefore, Block 1 starts like this:

| Word          | Value      |
| ------------- | ---------- |
| \\(M_0\\)     | `41414141` |
| \\(M_1\\)     | `41414141` |
| \\(M_2\\)     | `41414141` |
| \\(M_3\\)     | `41414141` |
| \\(M_4\\)     | `41414141` |
| ...           | ...        |
| \\(M\_{15}\\) | `41414141` |

All 16 words are identical because the first 64 bytes are all `A`.

## Block 2

Block 2 contains:

- 56 bytes of `A`
- One byte `80`
- Seven zero bytes

Its first words are:

| Word          | Value      |
| ------------- | ---------- |
| \\(M_0\\)     | `41414141` |
| \\(M_1\\)     | `41414141` |
| ...           | ...        |
| \\(M\_{13}\\) | `41414141` |
| \\(M\_{14}\\) | `80000000` |
| \\(M\_{15}\\) | `00000000` |

Why is \\(M\_{14}\\) equal to `80000000`?

Because the last four bytes of the original message are followed by the padding byte `80`.

## Block 3

Block 3 contains 56 zero bytes followed by the length field.

| Word                            | Value      |
| ------------------------------- | ---------- |
| \\(M_0\\) through \\(M\_{13}\\) | `00000000` |
| \\(M\_{14}\\)                   | `00000000` |
| \\(M\_{15}\\)                   | `000003C0` |

Now all three blocks are ready for SHA-256 computation.

# Part 4 — Initialize the hash state

SHA-256 begins with these eight 32-bit initial values:

| Variable  | Initial value |
| --------- | ------------- |
| \\(H_0\\) | `6a09e667`    |
| \\(H_1\\) | `bb67ae85`    |
| \\(H_2\\) | `3c6ef372`    |
| \\(H_3\\) | `a54ff53a`    |
| \\(H_4\\) | `510e527f`    |
| \\(H_5\\) | `9b05688c`    |
| \\(H_6\\) | `1f83d9ab`    |
| \\(H_7\\) | `5be0cd19`    |

We will call this state:

\\[ H^{(0)} \\]

The superscript indicates the state before processing the first block.

# Part 5 — Process Block 1

## Step 1: Prepare the message schedule

Initially:

\\[ W_0=M_0,\ldots,W\_{15}=M\_{15} \\]

So:

```
W0 = 41414141
W1 = 41414141
...
W15 = 41414141
```

Then calculate:

\\[ W_t= \sigma_1(W\_{t-2})+ W\_{t-7}+ \sigma_0(W\_{t-15})+ W\_{t-16} \pmod{2^{32}} \\]

For example:

\\[ W\_{16}= \sigma_1(W\_{14})+ W_9+ \sigma_0(W_1)+ W_0 \\]

We repeat this until:

\\[ W\_{63} \\]

The result is a schedule of 64 words.

## Step 2: Initialize working variables

Copy the current hash state:

\\[ (a,b,c,d,e,f,g,h)=H^{(0)} \\]

Thus:

```
a = 6a09e667
b = bb67ae85
c = 3c6ef372
d = a54ff53a
e = 510e527f
f = 9b05688c
g = 1f83d9ab
h = 5be0cd19
```

## Step 3: Execute 64 rounds

For every round \\(t=0,\ldots,63\\):

\\[ T_1=h+\Sigma_1(e)+Ch(e,f,g)+K_t+W_t \\]

\\[ T_2=\Sigma_0(a)+Maj(a,b,c) \\]

All additions are modulo \\(2^{32}\\).

Then update:

```
h = g
g = f
f = e
e = d + T1
d = c
c = b
b = a
a = T1 + T2
```

This is repeated 64 times.

At the end, the working variables have changed.

Let's call their final values:

\\[ a_1,b_1,c_1,d_1,e_1,f_1,g_1,h_1 \\]

## Step 4: Update the hash state

Now comes the critical operation:

\\[ H_0^{(1)}=(H_0^{(0)}+a_1)\bmod2^{32} \\]

\\[ H_1^{(1)}=(H_1^{(0)}+b_1)\bmod2^{32} \\]

Continue through \\(H_7\\).

The resulting state is:

\\[ \boxed{H^{(1)}} \\]

This is the output state after Block 1.

Important: We do not reset the hash to its original initial values for Block 2.

# Part 6 — Process Block 2

This is where the chaining mechanism becomes clear.

We now take:

\\[ H^{(1)} \\]

and copy its eight words into the working variables:

\\[ (a,b,c,d,e,f,g,h)=H^{(1)} \\]

Then:

- Build the 64-word schedule from Block 2.
- Execute 64 rounds.
- Add the final working variables to \\(H^{(1)}\\).

The result is:

\\[ \boxed{H^{(2)}} \\]

Notice the relationship:

\\[ H^{(0)} \xrightarrow{Block\\,1} H^{(1)} \xrightarrow{Block\\,2} H^{(2)} \\]

The hash state carries information from the previous block into the next block.

# Part 7 — Process Block 3

We repeat exactly the same procedure.

Initialize:

\\[ (a,b,c,d,e,f,g,h)=H^{(2)} \\]

Use the third block's message schedule, including the final length word:

\\[ W\_{15}=\texttt{000003C0} \\]

Execute 64 rounds.

Then perform the final state addition:

\\[ H_0^{(3)}=(H_0^{(2)}+a_3)\bmod2^{32} \\]

Continue for all eight words.

We obtain:

\\[ \boxed{H^{(3)}} \\]

This is the final hash state.

# Part 8 — Produce the final digest

Concatenate the eight 32-bit words:

\\[ Digest= H_0^{(3)}||H_1^{(3)}||\cdots||H_7^{(3)} \\]

The result is:

\\[ 8\times32=256\text{ bits} \\]

Or:

\\[ \boxed{64\text{ hexadecimal characters}} \\]

## Complete process recap

Original message

# 120 bytes

960 bits

Padding

## Block 1

512 bits

64 rounds

## Block 2

512 bits

64 rounds

## Block 3

512 bits

64 rounds

Final hash state

# 256 bits

64 hexadecimal characters

Total number of compression rounds:

\\[ 3\times64=\boxed{192\text{ rounds}} \\]

But remember: each block's rounds depend on the state produced by the preceding block.

## Python structure to understand the chaining

Here is the high-level structure of SHA-256 processing:

```
H = INITIAL_HASH.copy()for block in blocks:    W = prepare_schedule(block)    a, b, c, d, e, f, g, h = H    for t in range(64):        # Calculate T1 and T2        # Update a, b, c, d, e, f, g, h    H[0] = (H[0] + a) & 0xFFFFFFFF    H[1] = (H[1] + b) & 0xFFFFFFFF    H[2] = (H[2] + c) & 0xFFFFFFFF    H[3] = (H[3] + d) & 0xFFFFFFFF    H[4] = (H[4] + e) & 0xFFFFFFFF    H[5] = (H[5] + f) & 0xFFFFFFFF    H[6] = (H[6] + g) & 0xFFFFFFFF    H[7] = (H[7] + h) & 0xFFFFFFFF
```

The `for block in blocks` loop is what makes the same SHA-256 compression algorithm work for messages of arbitrary length.

The most important concept to retain: SHA-256 does not independently hash each block and concatenate the results. It processes each block using the hash state left by the previous block.



### how the ki values are used in the 64 rounds
Let's apply the SHA-256 constant generation process to 17, step by step.

First, understand the rule from NIST FIPS 180-4:

\\[ K_i = \left\lfloor 2^{32} \times \operatorname{frac}(\sqrt[3]{p_i}) \right\rfloor \\]

Where:

- \\(p_i\\): the \\(i\\)-th prime number.
- \\(\sqrt[3]{p_i}\\): cube root of the prime.
- \\(\operatorname{frac}(x)\\): fractional part of the number.
- \\(2^{32}\\): converts the fractional part into a 32-bit integer.
- \\(K_i\\): the resulting 32-bit constant.

## Step 1 — Choose the number 17

Is 17 prime?

Yes.

\\[ 17 = 17 \\]

Its cube root is:

\\[ \sqrt[3]{17} \approx 2.571281590658235 \\]

## Step 2 — Extract the fractional part

Remove the integer part, which is 2.

\\[ \operatorname{frac}(\sqrt[3]{17}) = 0.571281590658235 \\]

## Step 3 — Multiply by \\(2^{32}\\)

\\[ 2^{32}=4294967296 \\]

Therefore:

\\[ K = \left\lfloor 0.571281590658235 \times 4294967296 \right\rfloor \\]

\\[ K = \left\lfloor 2453627175. \ldots \right\rfloor \\]

\\[ \boxed{K=2453627175} \\]

## Step 4 — Convert to hexadecimal

Convert the decimal integer into hexadecimal:

\\[ 2453627175\_{10} = \boxed{0x923F82A7} \\]

## Result for 17

Prime

# 17

Cube root

## 2.57128...

Fractional part

## 0.57128...

32-bit hexadecimal

# 923F82A7

Important: In the SHA-256 standard, the constants are generated from the first 64 prime numbers, not from the number 17 itself as an index.

For example:

| Prime | SHA-256 constant |
| ----- | ---------------- |
| 2     | `428A2F98`       |
| 3     | `71374491`       |
| 5     | `B5C0FBCF`       |
| 7     | `E9B5DBA5`       |
| 11    | `3956C25B`       |
| 13    | `59F111F1`       |
| 17    | `923F82A7`       |

The constant for prime 17 is therefore `923F82A7`.
