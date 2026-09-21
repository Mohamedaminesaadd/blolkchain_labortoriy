## Lab 04 — Avalanche Effect

The **avalanche effect** is one of the most important properties of a good hash function.

The idea is simple:

> **Changing only one bit of the input should change approximately half of the output bits.**

For a **32-bit hash**, if you change one input bit, you ideally want about:

$$
\frac{32}{2}=16
$$

output bits to change.

---

### 1. Simple example

Suppose:

```text
Input 1:
10110100

Input 2:
10110101
        ↑
   only 1 bit changed
```

A bad hash might produce:

```text
Hash 1:
10010010

Hash 2:
10010011
          ↑
only 1 bit changed
```

That's poor avalanche behavior.

A better hash might produce:

```text
Hash 1:
1010110010110101

Hash 2:
0111001101001110
```

Many bits changed even though the input changed by only one bit.

---

# 2. Why is avalanche important?

Imagine your hash function:

```text
hash("hello")
```

produces:

```text
1011001010011010...
```

Now change:

```text
hello
```

to:

```text
jello
```

Only one character changed.

A good hash should produce something that looks completely unrelated:

```text
hello → 1011001010011010...
jello → 0110110101100011...
```

rather than:

```text
hello → 1011001010011010...
jello → 1011001010011011...
```

The second behavior reveals too much structure from the input.

---

# 3. Measuring avalanche mathematically

For two hash outputs:

$$
H_1
$$

and

$$
H_2
$$

we calculate:

$$
D=H_1\oplus H_2
$$

where \(\oplus\) is XOR.

Example:

```text
H1 = 10110100
H2 = 10011110
```

XOR:

```text
10110100
10011110
--------
00101010
```

Now count the `1`s:

```text
00101010
  ↑ ↑ ↑
```

There are 3 changed bits.

So the number of changed bits is:

$$
D_{\text{bits}} = \operatorname{popcount}(H_1\oplus H_2)
$$

For a 32-bit hash, the ideal value is approximately:

$$
16
$$

---

# 4. Avalanche percentage

We can calculate:

$$
A=\frac{\text{changed output bits}}{\text{total output bits}}\times100
$$

For a 32-bit hash, suppose 17 bits changed:

$$
A=\frac{17}{32}\times100
$$

$$
A=53.125\%
$$

That's close to the ideal:

$$
50\%
$$

So we want approximately:

```text
50%
```

on average.

---

# 5. Your Lab 04 experiment

You can build an experiment like:

```text
Input
  ↓
Hash
  ↓
Change ONE bit
  ↓
Hash again
  ↓
XOR the two hashes
  ↓
Count different bits
  ↓
Calculate percentage
```

For example:

```text
Original input
      ↓
01101001
      ↓
hash32()
      ↓
10110100101101010010101110100101


Change one bit
      ↓
01101000
      ↓
hash32()
      ↓
01001111010110110110011001100111


              XOR
                ↓
11111011011011100100110111010010
                ↓
          count 1 bits
                ↓
              20 bits
                ↓
          20 / 32 = 62.5%
```

---

# 6. Very important distinction

**Collision resistance** and **avalanche effect** are different.

### Collision

You test:

$$
x_1\neq x_2
$$

and look for:

$$
H(x_1)=H(x_2)
$$

---

### Avalanche

You deliberately make a tiny input change:

$$
x_1 \approx x_2
$$

and measure how much the output changes:

$$
H(x_1)\oplus H(x_2)
$$

So your labs are building toward understanding different properties of a hash function:

```text
Lab 01
Weak Hash
    ↓
Lab 02
Collision Detection
    ↓
Lab 03
Better 32-bit Hash
    ↓
Lab 04
Avalanche Effect
    ↓
Lab 05
Distribution / Uniformity
    ↓
Lab 06
Hash Table
    ↓
Lab 07
Collision Resolution
```

For your **32-bit hash project**, Lab 04 is particularly useful because you can compare your original weak hash against your improved hash and see quantitatively whether changing **one input bit** causes roughly **16 of the 32 output bits** to change.
