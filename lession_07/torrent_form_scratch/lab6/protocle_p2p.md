For Lab 6 — Binary Protocol Message Encoding, we will upgrade your existing C++ P2P network from sending text messages such as `PING|5000|hello` to sending structured messages encoded as bytes.

We will build it step by step, reusing your existing peer architecture rather than starting from scratch.

# Lab 6 — Binary Protocol Message Encoding

## 1. What are we going to build?

Currently, your application sends messages like:

```
MSG123|5000|Hello P2P network\n
```

This is a text-based protocol. In this lab, we will encode the same information into a binary message format.

CURRENT PROTOCOL — TEXT

MSG123|5000|Hello P2P network\n

NEW PROTOCOL — BINARY

01

Type

00 00

Flags

00 05

Length

…

Payload

Illustrative layout only; we will define the exact byte format in Step 1.

Binary encoding lets us represent message types, lengths, IDs, and payloads in a well-defined format without relying on delimiters such as `|` and `\n`.

## 2. What are the steps?

## 1

Define the binary protocol

Start here

Define the message structure, field sizes, byte order, and maximum payload length.

## 2

Create the message structure

Define a C++ Message class or struct with a message type, message ID, and payload.

## 3

Implement serialization

Convert a Message object into a sequence of bytes.

## 4

Implement deserialization

Parse received bytes back into a Message object and validate them.

## 5

Handle TCP framing

Receive complete binary messages even when TCP splits or combines data across reads.

## 6

Integrate with your P2P peers

Replace the text-based send/receive path and preserve duplicate detection and message forwarding.

## 7

Test the protocol

Test valid messages, malformed messages, partial reads, multiple messages, and oversized payloads.

## 3. What will our binary message contain?

For the first version, I recommend a simple fixed header followed by a variable-length payload.

| Field          | Size     | Purpose                                      |
| -------------- | -------- | -------------------------------------------- |
| Magic number   | 4 bytes  | Identify our P2P protocol                    |
| Version        | 1 byte   | Identify the protocol version                |
| Message type   | 1 byte   | For example, `PING`, `PONG`, or `DATA`       |
| Message ID     | 8 bytes  | Identify the message for duplicate detection |
| Payload length | 4 bytes  | Specify the number of payload bytes          |
| Payload        | Variable | Carry the actual message data                |

The header will therefore be 18 bytes, followed by the payload.

For example, a `PING` message could have message type `1`, message ID `1001`, and a short payload. We will define the exact numeric constants and network byte order during Step 1.

## 4. What you should understand before coding

Three concepts are essential:

- Serialization: converting a structured object into bytes.
- Deserialization: converting bytes back into a structured object.
- Framing: determining where one message ends and the next begins in a TCP byte stream.

One important difference from your previous lab: we will not use `strlen()` to determine the payload length, because binary payloads can contain zero bytes (`0x00`). We will use explicit lengths.

## Let's start with Step 1

Our first task is to define the exact protocol specification before writing the serialization code. This avoids compatibility problems when Peer A encodes a message and Peer B decodes it.

Once the format is fixed, we can implement it in C++ using `std::vector<std::uint8_t>` for the encoded bytes and fixed-width integer types for the header fields.



---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Let's start Lab 6 — Binary Protocol Message Encoding, Step 1.

Our goal is to define the exact format that every peer will use to exchange binary messages. We'll define it first, then implement serialization and deserialization in C++.

# Step 1 — Define the binary protocol

## 1. Why do we need a binary protocol?

In your previous labs, you used text messages such as:

```
MSG123|5000|Hello P2P network\n
```

This works for learning, but it has limitations:

- We must parse delimiters such as `|`.
- We need a rule to determine where each message ends.
- Text representation can be less compact.
- TCP is a byte stream: one `send()` does not necessarily correspond to one `recv()`.

Instead, we'll define a fixed-size binary header followed by a variable-size payload.

## 2. Define the message format

## Our P2P message

Fixed header: 18 bytes · Payload: variable length

#### Magic

4 bytes

#### Ver.

1 B

#### Type

1 B

#### Message ID

8 bytes

#### Length

4 bytes

Payload

0 to 1,048,576 bytes (1 MiB)

The receiver reads the 18-byte header first. The `Length` field tells it exactly how many payload bytes to read next.

## 3. Define every field

| Field          | Size     | Purpose                                      |
| -------------- | -------- | -------------------------------------------- |
| Magic number   | 4 bytes  | Identifies our protocol                      |
| Version        | 1 byte   | Identifies the protocol version              |
| Message type   | 1 byte   | Identifies the kind of message               |
| Message ID     | 8 bytes  | Identifies a message for duplicate detection |
| Payload length | 4 bytes  | Number of payload bytes                      |
| Payload        | Variable | Actual message data                          |

We'll use these values:

- Magic number: ASCII `P2P1`, represented by bytes `50 32 50 31` in hexadecimal.
- Version: `1`.
- Message types: `PING = 1`, `PONG = 2`, `DATA = 3`.
- Message ID: an unsigned 64-bit integer.
- Maximum payload: 1 MiB.

All multi-byte integers will use big-endian byte order: the most significant byte comes first. This ensures that peers on machines with different native byte orders interpret the same message correctly.

## 4. Example of a message

Imagine Peer A sends this message:

```
Type:          DATA
Message ID:    42
Payload:       Hello
Payload length: 5 bytes
```

Its conceptual structure is:

```
+-------------------------+
| Magic: P2P1             | 4 bytes
+-------------------------+
| Version: 1              | 1 byte
+-------------------------+
| Type: DATA (3)          | 1 byte
+-------------------------+
| Message ID: 42          | 8 bytes
+-------------------------+
| Payload length: 5       | 4 bytes
+-------------------------+
| Payload: Hello          | 5 bytes
+-------------------------+
```

The total message size is \\(18 + 5 = 23\\) bytes.

Notice that the payload does not need a newline delimiter. It can contain any bytes, including `0x00`.

## 5. Important design rule

Do not send a C++ structure directly over the network using `send(&message, sizeof(message), ...)`.

A structure can contain compiler-added padding, and its integer fields use the host machine's byte order. Instead, we'll explicitly serialize each field into a byte buffer.

This is also how we'll handle TCP correctly: the receiver must collect all 18 header bytes and then all payload bytes, even when TCP delivers them across several `recv()` calls.

## Next step

Step 2 — Create the C++ message structure and protocol constants.

We'll define the `Message` class or structure, the message type constants, the 18-byte header size, and the maximum payload in a header file named `protocol.hpp`. Then we'll use that definition in the serialization code.

---------------------------------------------------------------
# Lab 6 — Step 2: Create the message structure

Now we'll translate our protocol specification into C++.

We'll create a file called `protocol.hpp`. This file defines the format shared by every peer in our P2P network.

## 1. Create the project files

Your project can have this structure:

```
p2p/
├── protocol.hpp
├── protocol.cpp
└── main.cpp
```

- `protocol.hpp`: protocol constants and message structure.
- `protocol.cpp`: later, serialization and deserialization.
- `main.cpp`: test the protocol before integrating it into your peers.

## 2. Implement `protocol.hpp`

```

#ifndef PROTOCOL_HPP
#define PROTOCOL_HPP

#include <cstdint>
#include <string>
#include <vector>

namespace p2p {

// Protocol identification
constexpr std::uint32_t MAGIC = 0x50325031; // "P2P1"

// Protocol version
constexpr std::uint8_t VERSION = 1;

// Message header sizes
constexpr std::size_t MAGIC_SIZE = 4;
constexpr std::size_t VERSION_SIZE = 1;
constexpr std::size_t TYPE_SIZE = 1;
constexpr std::size_t MESSAGE_ID_SIZE = 8;
constexpr std::size_t LENGTH_SIZE = 4;

constexpr std::size_t HEADER_SIZE =
    MAGIC_SIZE +
    VERSION_SIZE +
    TYPE_SIZE +
    MESSAGE_ID_SIZE +
    LENGTH_SIZE;

// Maximum payload: 1 MiB
constexpr std::uint32_t MAX_PAYLOAD_SIZE = 1024 * 1024;

// Message types
enum class MessageType : std::uint8_t {
    PING = 1,
    PONG = 2,
    DATA = 3
};

// Logical representation of a message
struct Message {
    MessageType type;
    std::uint64_t id;
    std::vector<std::uint8_t> payload;
};

} // namespace p2p

#endif

```

## 3. Understand the important parts

### A. Why use `std::uint64_t` for the message ID?

```
std::uint64_t id;
```

It is an unsigned integer with a fixed width of 64 bits.

It can represent IDs from 0 to \\(2^{64}-1\\). This gives us a large identifier space for duplicate detection when peers forward messages.

For example:

```
Message message{
    MessageType::DATA,
    42,
    {'H', 'e', 'l', 'l', 'o'}
};
```

This represents a `DATA` message with ID `42` and the payload `Hello`.

### B. Why use `std::vector<std::uint8_t>` for the payload?

```
std::vector<std::uint8_t> payload;
```

Because the payload is binary data, not necessarily text.

It can contain:

```
48 65 6C 6C 6F 00 FF
```

Those bytes include a zero byte and a byte that is not ordinary printable text. A `std::string` can also hold arbitrary bytes when used with explicit lengths, but a byte vector makes the binary intent clearer here.

### C. Why use `enum class`?

```
enum class MessageType : std::uint8_t {
    PING = 1,
    PONG = 2,
    DATA = 3
};
```

It gives each message type a defined numeric value and stores it using one byte. `enum class` also avoids unintentionally mixing message types with unrelated integers.

### D. What does `HEADER_SIZE` calculate?

```
constexpr std::size_t HEADER_SIZE =
    MAGIC_SIZE + VERSION_SIZE + TYPE_SIZE +
    MESSAGE_ID_SIZE + LENGTH_SIZE;
```

The result is:

\\[ 4+1+1+8+4=\boxed{18\text{ bytes}} \\]

`constexpr` lets the compiler calculate this value at compile time.

## 4. Test that the structure works

Create `main.cpp`:

```

#include <iostream>
#include "protocol.hpp"

int main() {
    p2p::Message message{
        p2p::MessageType::DATA,
        42,
        {'H', 'e', 'l', 'l', 'o'}
    };

    std::cout << "Protocol version: "
              << static_cast<int>(p2p::VERSION) << '\n';

    std::cout << "Header size: "
              << p2p::HEADER_SIZE << " bytes\n";

    std::cout << "Message ID: "
              << message.id << '\n';

    std::cout << "Payload size: "
              << message.payload.size() << " bytes\n";

    std::cout << "Payload: ";

    for (std::uint8_t byte : message.payload) {
        std::cout << static_cast<char>(byte);
    }

    std::cout << '\n';
    return 0;
}

```

Compile and execute:

```
g++ -std=c++17 -Wall -Wextra -pedantic main.cpp -o protocol_test
./protocol_test
```

Expected output:

```
Protocol version: 1
Header size: 18 bytes
Message ID: 42
Payload size: 5 bytes
Payload: Hello
```

## 5. What have we completed?

- Defined the protocol constants.
- Defined the supported message types.
- Created a C++ representation of a message.
- Established the fixed header size and payload limit.

Important: We have not encoded the structure into network bytes yet. `Message` is only the logical representation.

Next is Step 3 — Serialization: implement a function that converts a `Message` into a `std::vector<std::uint8_t>` containing the exact binary format we defined.

-----------------------------------------------------
# Lab 6 — Step 3: Serialization

Now we'll implement the first important function of our binary protocol: converting a C++ `Message` into a sequence of bytes that can be sent over TCP.

Previously, we created a message like this:

```
p2p::Message message{
    p2p::MessageType::DATA,
    42,
    {'H', 'e', 'l', 'l', 'o'}
};
```

But this is only a C++ object. Peer B cannot assume it receives the same in-memory object layout as Peer A. We must encode every field into our defined wire format.

## 1. Understand the serialization process

C++ Message

Type = DATA · ID = 42 · Payload = Hello

serialize(message)

Encode fields · Big-endian integers

Binary byte buffer

Header (18 bytes) + payload (5 bytes)

Total: 23 bytes

## 2. Create `protocol.cpp`

We'll implement helper functions to append integers in big-endian order, then use them to encode the message.

```

#include "protocol.hpp"

#include <stdexcept>

namespace p2p {

namespace {

// Append a 32-bit integer in big-endian byte order.
void append_u32(std::vector<std::uint8_t>& out,
                std::uint32_t value) {
    out.push_back(static_cast<std::uint8_t>(value >> 24));
    out.push_back(static_cast<std::uint8_t>(value >> 16));
    out.push_back(static_cast<std::uint8_t>(value >> 8));
    out.push_back(static_cast<std::uint8_t>(value));
}

// Append a 64-bit integer in big-endian byte order.
void append_u64(std::vector<std::uint8_t>& out,
                std::uint64_t value) {
    for (int shift = 56; shift >= 0; shift -= 8) {
        out.push_back(
            static_cast<std::uint8_t>(value >> shift)
        );
    }
}

} // namespace

std::vector<std::uint8_t> serialize(const Message& message) {
    if (message.payload.size() > MAX_PAYLOAD_SIZE) {
        throw std::length_error("Payload exceeds maximum size");
    }

    std::vector<std::uint8_t> out;
    out.reserve(HEADER_SIZE + message.payload.size());

    // 1. Magic number: 4 bytes
    append_u32(out, MAGIC);

    // 2. Protocol version: 1 byte
    out.push_back(VERSION);

    // 3. Message type: 1 byte
    out.push_back(static_cast<std::uint8_t>(message.type));

    // 4. Message ID: 8 bytes
    append_u64(out, message.id);

    // 5. Payload length: 4 bytes
    append_u32(
        out,
        static_cast<std::uint32_t>(message.payload.size())
    );

    // 6. Payload: variable number of bytes
    out.insert(
        out.end(),
        message.payload.begin(),
        message.payload.end()
    );

    return out;
}

} // namespace p2p

```

We also need to declare the function in `protocol.hpp`, inside the `p2p` namespace, after the `Message` structure:

```
std::vector<std::uint8_t> serialize(const Message& message);
```

## 3. Understand the important implementation details

### A. Why shift bits?

Consider this call:

```
append_u32(out, 0x50325031);
```

The integer is split into four bytes:

| Shift   | Resulting byte |
| ------- | -------------- |
| 24 bits | `0x50`         |
| 16 bits | `0x32`         |
| 8 bits  | `0x50`         |
| 0 bits  | `0x31`         |

So the encoded bytes are:

```
50 32 50 31
```

Those are the ASCII bytes for `P2P1`.

This works independently of the computer's native byte order because we explicitly choose the order in which bytes are appended.

### B. Why `reserve()`?

```
out.reserve(HEADER_SIZE + message.payload.size());
```

This asks the vector to allocate enough capacity for the header and payload in advance. It can reduce memory reallocations as we append bytes.

### C. Why not `strlen()`?

A binary payload can contain zero bytes:

```
48 65 00 6C 6F
```

The zero byte is valid data. Functions such as `strlen()` would incorrectly treat it as the end of a C-style string. We instead use `message.payload.size()`.

### D. Why validate the payload length?

Our protocol limits payloads to 1 MiB. We reject oversized messages before encoding them, so the sender cannot silently produce a message that violates our protocol's rules.

## 4. Test serialization

Update `main.cpp`:

```

#include "protocol.hpp"

#include <iomanip>
#include <iostream>

int main() {
    p2p::Message message{
        p2p::MessageType::DATA,
        42,
        {'H', 'e', 'l', 'l', 'o'}
    };

    const auto bytes = p2p::serialize(message);

    std::cout << "Encoded size: "
              << bytes.size() << " bytes\n";

    std::cout << "Encoded bytes:\n";

    for (std::uint8_t byte : bytes) {
        std::cout << std::hex
                  << std::setw(2)
                  << std::setfill('0')
                  << static_cast<unsigned int>(byte)
                  << ' ';
    }

    std::cout << '\n';
    return 0;
}

```

Compile both source files:

```
g++ -std=c++17 -Wall -Wextra -pedantic \
    main.cpp protocol.cpp -o protocol_test

./protocol_test
```

Expected output:

```
Encoded size: 23 bytes
Encoded bytes:
50 32 50 31 01 03 00 00 00 00 00 00 00 2a 00 00 00 05 48 65 6c 6c 6f
```

The bytes represent:

- `50 32 50 31` — magic number `P2P1`.
- `01` — protocol version 1.
- `03` — message type `DATA`.
- `00 00 00 00 00 00 00 2a` — message ID 42.
- `00 00 00 05` — payload length 5.
- `48 65 6c 6c 6f` — payload `Hello`.

## 5. What have we achieved?

We can now turn a logical C++ message into the exact sequence of bytes our peers will exchange.

The next step is Step 4 — Deserialization: take a received byte buffer, validate the header and payload length, and reconstruct the original `Message`. We'll also reject invalid magic numbers, unsupported versions, unknown message types, and malformed input.