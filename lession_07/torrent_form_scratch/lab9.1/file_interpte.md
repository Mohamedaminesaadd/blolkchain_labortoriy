# Lab 6 — Step 4: Deserialization

In Step 3, we implemented `serialize()`, which converts a C++ message into binary bytes.

Now we'll implement the reverse operation: deserialization, which converts those bytes back into a C++ `Message`.

## 1. Understand the process

Received byte buffer

Header + payload

deserialize(bytes)

Validate header, type, version and length

C++ Message

Type = DATA · ID = 42 · Payload = Hello

A peer must not blindly trust incoming bytes. Another peer could send an invalid message, an unsupported version, or a payload length that exceeds our limit.

## 2. Declare the function in `protocol.hpp`

Add this declaration after the `serialize()` declaration:

```
Message deserialize(const std::vector<std::uint8_t>& bytes);
```

For this step, we'll require a complete message in the input buffer. Handling partial TCP reads comes in Step 5.

## 3. Implement deserialization in `protocol.cpp`

Add the following code to `protocol.cpp`, inside the `p2p` namespace. Keep the existing serialization code and its helper functions.

```

namespace {

std::uint32_t read_u32(
    const std::vector<std::uint8_t>& bytes,
    std::size_t offset
) {
    return
        (static_cast<std::uint32_t>(bytes[offset]) << 24) |
        (static_cast<std::uint32_t>(bytes[offset + 1]) << 16) |
        (static_cast<std::uint32_t>(bytes[offset + 2]) << 8) |
        static_cast<std::uint32_t>(bytes[offset + 3]);
}

std::uint64_t read_u64(
    const std::vector<std::uint8_t>& bytes,
    std::size_t offset
) {
    std::uint64_t value = 0;

    for (std::size_t i = 0; i < 8; ++i) {
        value = (value << 8) | bytes[offset + i];
    }

    return value;
}

} // namespace

Message deserialize(const std::vector<std::uint8_t>& bytes) {
    // 1. Ensure the complete fixed header is present.
    if (bytes.size() < HEADER_SIZE) {
        throw std::runtime_error("Incomplete message header");
    }

    // 2. Validate the magic number.
    if (read_u32(bytes, 0) != MAGIC) {
        throw std::runtime_error("Invalid magic number");
    }

    // 3. Validate protocol version.
    if (bytes[4] != VERSION) {
        throw std::runtime_error("Unsupported protocol version");
    }

    // 4. Validate message type.
    MessageType type;

    switch (bytes[5]) {
        case 1:
            type = MessageType::PING;
            break;
        case 2:
            type = MessageType::PONG;
            break;
        case 3:
            type = MessageType::DATA;
            break;
        default:
            throw std::runtime_error("Unknown message type");
    }

    // 5. Read the message ID and payload length.
    const std::uint64_t id = read_u64(bytes, 6);
    const std::uint32_t payload_length = read_u32(bytes, 14);

    // 6. Validate the payload size before using it.
    if (payload_length > MAX_PAYLOAD_SIZE) {
        throw std::runtime_error("Payload exceeds maximum size");
    }

    // This function expects exactly one complete message.
    if (bytes.size() != HEADER_SIZE + payload_length) {
        throw std::runtime_error("Message size does not match payload length");
    }

    // 7. Extract the payload.
    std::vector<std::uint8_t> payload(
        bytes.begin() + HEADER_SIZE,
        bytes.end()
    );

    return Message{type, id, std::move(payload)};
}

```

Make sure `protocol.cpp` includes these headers if they aren't already present:

```
#include <stdexcept>
#include <utility>
```

The helper functions `read_u32()` and `read_u64()` reverse the encoding process by reconstructing big-endian integers from individual bytes.

## 4. Test serialization and deserialization together

Replace your `main.cpp` with this round-trip test:

```

#include "protocol.hpp"

#include <iostream>
#include <stdexcept>

int main() {
    try {
        p2p::Message original{
            p2p::MessageType::DATA,
            42,
            {'H', 'e', 'l', 'l', 'o'}
        };

        // Encode the message.
        auto bytes = p2p::serialize(original);

        // Decode the same bytes.
        p2p::Message decoded = p2p::deserialize(bytes);

        std::cout << "Original ID: "
                  << original.id << '\n';

        std::cout << "Decoded ID: "
                  << decoded.id << '\n';

        std::cout << "Decoded payload: ";

        for (std::uint8_t byte : decoded.payload) {
            std::cout << static_cast<char>(byte);
        }

        std::cout << '\n';

        std::cout << "Round-trip successful!\n";
    }
    catch (const std::exception& e) {
        std::cerr << "Protocol error: "
                  << e.what() << '\n';
        return 1;
    }

    return 0;
}

```

Compile and run:

```
g++ -std=c++17 -Wall -Wextra -pedantic \
    main.cpp protocol.cpp -o protocol_test

./protocol_test
```

Expected output:

```
Original ID: 42
Decoded ID: 42
Decoded payload: Hello
Round-trip successful!
```

## 5. Test an invalid message

We should also verify that malformed messages are rejected.

For example, after serialization, modify the magic number:

```
bytes[0] = 0x00;

p2p::deserialize(bytes);
```

The function should throw an exception with:

```
Invalid magic number
```

You can catch this exception using the `try`/`catch` pattern from the test above.

## 6. Important limitation: TCP can split messages

Our deserializer assumes it receives exactly one complete message. TCP does not guarantee that.

For example, a 23-byte message might arrive as:

```
recv() #1:  [first 8 bytes]
recv() #2:  [next 10 bytes]
recv() #3:  [last 5 bytes]
```

Or several messages could arrive together in one read. This is why we must implement message framing and buffered reads before integrating the protocol with our peers.

Next: Step 5 — TCP framing and partial reads. We'll build a receiver that collects the fixed header, reads the declared payload length, and handles fragmented or concatenated messages without losing bytes.

Interrupted Transfer and Resume — P2P File-Sharing Lab
In your C++ torrent-like project, Interrupted Transfer and Resume means that if a peer disconnects while downloading a file, the client can continue downloading from where it stopped instead of starting again from zero.
This is one of the important features used by real file-sharing systems, including BitTorrent.
1. Understand the problem
Imagine Peer A has a file of 100 MB, and Peer B wants to download it.
Peer A — Seeder
Has the complete 100 MB file


Downloaded by Peer B
60 MB / 100 MB




Connection interrupted at 60%



Peer B — Downloader
Has already downloaded 60 MB



Without resume, Peer B might have to download the entire file again.
With resume, Peer B keeps the 60 MB already received and requests only the missing data.
2. How does resume work?
The basic procedure is:
1. Start downloading
   Peer B creates a local file and starts receiving data from Peer A.
2. Connection fails
   Peer B has downloaded 60 MB, but the connection drops.
3. Save progress
   Peer B saves the file and records which pieces have been downloaded successfully.
4. Reconnect
   Peer B reconnects to Peer A or another peer that has the file.
5. Request missing pieces
   Peer B asks for the remaining pieces rather than downloading everything again.
6. Verify and complete
   Peer B checks the downloaded pieces against their expected hashes, then reconstructs the complete file.

3. Why file splitting is important
This feature connects directly to your earlier lab on File Splitting into Pieces.
Instead of treating a 100 MB file as one huge transfer, divide it into pieces of 1 MB each.
For example:
Piece index	Byte range	Status
0	0–1 MB	Complete
1	1–2 MB	Complete
2	2–3 MB	Complete
...	...	...
59	59–60 MB	Complete
60	60–61 MB	Missing
61	61–62 MB	Missing
...	...	...
99	99–100 MB	Missing
Peer B has completed pieces 0–59 and needs pieces 60–99.
It can resume by requesting those missing pieces. In a real implementation, track pieces individually rather than relying only on the total number of downloaded bytes.
4. What metadata must we save?
To resume after the application closes or the computer restarts, the downloader needs a persistent record of its progress.
For example, a simple metadata file named download.state could contain:
File: movie.bin
Total size: 104857600
Piece size: 1048576
Total pieces: 100

Completed pieces:
0, 1, 2, 3, 4, ... 59


The file on disk contains the actual downloaded bytes. The metadata records which pieces have been completed and verified.
For a real implementation, you should also store a file identity, such as a torrent info hash or a trusted manifest identifier, so that saved progress cannot accidentally be reused for a different file.
Important: Don't mark a piece as complete just because some bytes arrived. Mark it complete only after all expected bytes have been written and its integrity has been verified.
5. How does the protocol request a missing piece?
Your P2P protocol could define additional message types:
Message	Purpose
FILE_INFO	Get file size, piece size and piece hashes
HAVE_PIECES	Advertise which pieces a peer has
REQUEST_PIECE	Request a particular piece
PIECE_DATA	Transfer the requested piece
CANCEL	Cancel an outstanding piece request
For example, Peer B might send:
REQUEST_PIECE
File ID: abc123
Piece index: 60


Peer A replies with the bytes for piece 60. Peer B validates the hash, writes the piece to the correct offset in its local file and updates its progress metadata.
This is a simplified protocol design for your lab, not the exact BitTorrent wire protocol.
6. What happens if the connection fails halfway through a piece?
Suppose Peer B is downloading piece 60, which should contain 1 MB, but the connection fails after 400 KB.
There are two approaches:
- Simple approach — restart that piece: Keep the already verified pieces and request all of piece 60 again. This is easier and suitable for your first implementation.
- Advanced approach — resume within a piece: Record verified byte ranges and request only the missing portion. This requires more complicated state tracking and validation.
For your C++ lab, I recommend the simple approach first. A partially downloaded piece is discarded or overwritten, while previously completed and verified pieces remain intact.
7. How this relates to BitTorrent
BitTorrent doesn't generally depend on a single central server continuously sending the entire file. A downloader can obtain different pieces from different peers, verify them using the torrent's integrity metadata, and keep completed pieces while continuing to find the rest.
That means a downloader can resume even if its original peer goes offline, provided other peers have the missing pieces and can be reached.
8. Your lab implementation plan
Since you've already been working on TCP file transfer, binary protocol encoding and file splitting, I'd implement this feature in the following order:
1. Create a persistent download-state file.
2. Track completed pieces with a std::vector<bool> or a bitfield.
3. Save a piece only after its integrity check passes.
4. Reload the state when the client restarts.
5. Request only missing pieces after reconnecting.
6. Simulate a network failure and verify that the download resumes correctly.
The main concept: Resume is not simply continuing a TCP connection. It is restarting the application-level download using saved progress, piece identifiers and integrity checks.



Let's implement Interrupted Transfer and Resume as a new lab in your C++ P2P file-sharing project, using the same step-by-step fiche format as your previous labs.

We'll build it incrementally, understand each step, test it, and only then move to the next one.

# Lab — Interrupted Transfer and Resume

## 1. Objective

Implement a file downloader that can:

- Download a file from another peer.
- Detect an interrupted transfer.
- Preserve already completed pieces.
- Save download progress to disk.
- Resume after reconnecting without downloading completed pieces again.
- Verify each piece before marking it complete.

We'll use C++17, Boost.Asio, and TCP, continuing your existing networking work.

## 2. Final architecture

Peer A — File provider

Original file + piece metadata

TCP + Boost.Asio

Piece requests and piece data

Peer B — Downloader

Download manager + state file + piece verification

Persistent storage

download.bin + download.state

Completed pieces survive a disconnect or restart.

## 3. Development roadmap

We'll implement one step at a time, testing each before continuing.

Step 1 — Prepare the project

Create the directory structure, define the file and piece metadata, and configure CMake.

Start here

Step 2 — Define file pieces

Calculate piece indexes, sizes, and offsets.

Step 3 — Save download state

Store the file identity and completed-piece information in `download.state`.

Step 4 — Verify pieces

Calculate and validate piece hashes before marking pieces complete.

Step 5 — Request missing pieces

Implement the request/response protocol between the two peers.

Step 6 — Simulate interruption

Disconnect the client during a download and preserve verified pieces.

Step 7 — Resume the download

Restart the client, load its state, and request only missing pieces.

Step 8 — Final integration test

Compare the completed download with the original file and test corruption and restart scenarios.

## 4. Step 1 — Prepare the project

Create this directory structure:

```
lab-resume/
├── CMakeLists.txt
├── src/
│   ├── main.cpp
│   ├── file_metadata.hpp
│   └── file_metadata.cpp
├── shared/
│   └── sample.bin
└── downloads/
```

What each file will do:

| File                | Responsibility                                   |
| ------------------- | ------------------------------------------------ |
| `main.cpp`          | Test the first step and later run the downloader |
| `file_metadata.hpp` | Declare file and piece metadata                  |
| `file_metadata.cpp` | Implement metadata calculations                  |
| `shared/sample.bin` | Original file served by Peer A                   |
| `downloads/`        | Downloaded data and saved state                  |

For this lab, we'll use a fixed piece size of 1 MiB. The last piece may be smaller.

### Create `file_metadata.hpp`

```
#ifndef FILE_METADATA_HPP
#define FILE_METADATA_HPP

#include <cstdint>
#include <string>

struct FileMetadata {
    std::string filename;
    std::uint64_t file_size;
    std::uint32_t piece_size;
    std::uint32_t total_pieces;
};

#endif
```

This structure stores the basic information needed to describe a downloadable file. We'll calculate `total_pieces` in the next step rather than manually entering it.

### Create `CMakeLists.txt`

```
cmake_minimum_required(VERSION 3.16)

project(lab_resume LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

add_executable(lab_resume
    src/main.cpp
    src/file_metadata.cpp
)

target_include_directories(lab_resume PRIVATE src)

target_compile_options(lab_resume PRIVATE
    -Wall
    -Wextra
    -Wpedantic
)
```

### Create `src/main.cpp`

```
#include "file_metadata.hpp"

#include <iostream>

int main() {
    FileMetadata metadata{
        "sample.bin",
        0,
        1024 * 1024,
        0
    };

    std::cout << "File: " << metadata.filename << '\n';
    std::cout << "Piece size: "
              << metadata.piece_size << " bytes\n";

    return 0;
}
```

### Create `src/file_metadata.cpp`

For now, leave this file empty except for its include:

```
#include "file_metadata.hpp"
```

### Compile and run

From the `lab-resume/` directory:

```
mkdir -p build
cd build
cmake ..
cmake --build .
./lab_resume
```

Expected output:

```
File: sample.bin
Piece size: 1048576 bytes
```

## 5. What you should understand before moving on

At this point, we have only created the foundation. We haven't implemented networking, saved progress, or resumed any transfer yet.

The key distinction is:

- File metadata describes the file and its pieces.
- Download state records which pieces have been received and verified.
- Piece data is the actual content stored on disk.

Once this foundation works, we'll move to Step 2 — Calculate piece count, indexes, and byte offsets, which is the basis for requesting and resuming the correct parts of a file.


Great. Let's continue with Step 2 — Calculate File Pieces.

The goal is to divide a file into fixed-size pieces so that later we can download, verify, and resume each piece independently.

## 1. Understand the calculation

Suppose the file size is 2.5 MiB and each piece is 1 MiB.

- Piece 0: 1 MiB
- Piece 1: 1 MiB
- Piece 2: 0.5 MiB

The number of pieces is:

\\[ \text{total pieces} = \left\lceil\frac{\text{file size}}{\text{piece size}}\right\rceil \\]

For integer arithmetic, use:

\\[ \text{total pieces} = \frac{\text{file size}+\text{piece size}-1}{\text{piece size}} \\]

We need to handle empty files separately or carefully use this formula with a zero size.

## 2. Update `file_metadata.hpp`

Add a function declaration to calculate the number of pieces.

```
#ifndef FILE_METADATA_HPP
#define FILE_METADATA_HPP

#include <cstdint>
#include <string>

struct FileMetadata {
    std::string filename;
    std::uint64_t file_size;
    std::uint32_t piece_size;
    std::uint32_t total_pieces;
};

std::uint32_t calculate_total_pieces(
    std::uint64_t file_size,
    std::uint32_t piece_size
);

#endif
```

## 3. Implement `file_metadata.cpp`

```
#include "file_metadata.hpp"

#include <stdexcept>

std::uint32_t calculate_total_pieces(
    std::uint64_t file_size,
    std::uint32_t piece_size
) {
    if (piece_size == 0) {
        throw std::invalid_argument(
            "Piece size cannot be zero"
        );
    }

    if (file_size == 0) {
        return 0;
    }

    const std::uint64_t count =
        1 + (file_size - 1) / piece_size;

    if (count > UINT32_MAX) {
        throw std::overflow_error(
            "Too many pieces for uint32_t"
        );
    }

    return static_cast<std::uint32_t>(count);
}
```

### Why use `1 + (file_size - 1) / piece_size`?

It computes the ceiling division without adding `piece_size - 1` to `file_size`, which could overflow for extremely large files.

## 4. Test it in `main.cpp`

```
#include "file_metadata.hpp"

#include <iostream>

int main() {
    constexpr std::uint32_t PIECE_SIZE = 1024 * 1024;

    const std::uint64_t file_size =
        2ULL * 1024 * 1024 + 512 * 1024;

    const auto total_pieces =
        calculate_total_pieces(file_size, PIECE_SIZE);

    FileMetadata metadata{
        "sample.bin",
        file_size,
        PIECE_SIZE,
        total_pieces
    };

    std::cout << "File: " << metadata.filename << '\n';
    std::cout << "File size: " << metadata.file_size << " bytes\n";
    std::cout << "Piece size: " << metadata.piece_size << " bytes\n";
    std::cout << "Total pieces: " << metadata.total_pieces << '\n';

    return 0;
}
```

Compile from your build directory:

```
cmake --build .
./lab_resume
```

Expected output:

```
File: sample.bin
File size: 2621440 bytes
Piece size: 1048576 bytes
Total pieces: 3
```

## 5. Your next task

Now that we know how many pieces exist, the next step is to calculate the offset and size of a specific piece.

For example, piece 2 begins at byte `2097152` and has a size of `524288` bytes. These calculations will let us request the correct bytes from Peer A without retransferring completed pieces.