# Lab 9 — File Splitting into Pieces

Now we'll extend your Lab 8 file-transfer project. Instead of treating a file as one continuous stream, we'll divide it into smaller pieces, just like the basic idea used by BitTorrent.

## 1. What are we going to build?

Imagine Peer A has a 10 MB file. We'll split it into pieces of 1 MB each.

original_file.bin

10 MB

Split into 1 MB pieces

Piece 0

Piece 1

Piece 2

Piece 3

Piece 4

Piece 5

Piece 6

Piece 7

Piece 8

Piece 9

Each piece has an index and a byte offset. The final piece may be smaller than the others.

## 2. Why split a file into pieces?

- Memory efficiency: process a small part instead of loading the entire file into RAM.
- Parallel downloading: later, different pieces can be downloaded from different peers at the same time.
- Retrying: if one piece fails, you can download that piece again instead of restarting the whole file.
- Integrity checking: each piece can be hashed and verified independently.
- Resumable downloads: record which pieces are complete and continue later.

## 3. How do we calculate the pieces?

Suppose a file is 10,500 bytes and the piece size is 4,096 bytes.

| Piece index | Offset | Size        |
| ----------- | ------ | ----------- |
| 0           | 0      | 4,096 bytes |
| 1           | 4,096  | 4,096 bytes |
| 2           | 8,192  | 2,308 bytes |

The formulas are:

\\[ \text{offset} = \text{piece index} \times \text{piece size} \\]

\\[ \text{piece size} = \min(\text{piece size configured},\ \text{file size}-\text{offset}) \\]

The last piece is usually smaller because the file size might not be an exact multiple of the configured piece size.

## 4. Lab 9 implementation plan

We'll implement it in C++ using your existing project.

1. Step 1 — Read a file in fixed-size pieces using `std::ifstream` and binary mode.
2. Step 2 — Assign each piece an index, offset, and size.
3. Step 3 — Save each piece separately in a `pieces/` directory.
4. Step 4 — Reconstruct the original file from the pieces in index order.
5. Step 5 — Verify correctness using `cmp` or SHA-256 hashes.

## 5. Proposed directory structure

```
lab9/
├── main.cpp
├── CMakeLists.txt
├── shared/
│   └── example.bin
├── pieces/
└── reconstructed/
```

For this lab, we'll focus on splitting and reconstructing files locally. In the next stage, we'll combine the piece format with Boost.Asio so peers can request specific pieces over TCP.

Next: we'll implement Step 1, the C++ program that reads a file in fixed-size binary chunks and saves each chunk as a separate piece.


-----------------------------------------------------
Let's implement Lab 9 — File Splitting into Pieces in C++.

In this first step, we'll write a program that reads a file in binary mode, splits it into fixed-size pieces, and saves each piece separately. We will not use Boost.Asio yet; this lab focuses on file handling.

## Step 1 — Create the project

Open your terminal:

```
mkdir -p lab9/shared lab9/pieces lab9/reconstructed
cd lab9
```

Our project structure will be:

```
lab9/
├── main.cpp
├── shared/
│   └── example.bin
├── pieces/
└── reconstructed/
```

Create a sample binary file:

```
printf '\x00\x01\x02\xFF\x41\x42\x43\x44\x45' > shared/example.bin
```

This file contains 9 bytes, including binary values such as `0x00` and `0xFF`.

## Step 2 — Implement the file splitter

Create `main.cpp`:

```

#include <algorithm>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>
#include <filesystem>

namespace fs = std::filesystem;

int main(int argc, char* argv[]) {
    if (argc != 3) {
        std::cerr << "Usage: " << argv[0]
                  << " <input_file> <piece_size>\n";
        return 1;
    }

    const std::string input_path = argv[1];
    const std::string output_dir = "pieces";

    std::size_t piece_size = 0;

    try {
        piece_size = std::stoull(argv[2]);
    } catch (...) {
        std::cerr << "Error: piece size must be a positive integer.\n";
        return 1;
    }

    if (piece_size == 0) {
        std::cerr << "Error: piece size cannot be zero.\n";
        return 1;
    }

    // Open the input file in binary mode.
    std::ifstream input(input_path, std::ios::binary);

    if (!input) {
        std::cerr << "Error: cannot open input file: "
                  << input_path << '\n';
        return 1;
    }

    // Create the directory for the output pieces.
    fs::create_directories(output_dir);

    std::vector<char> buffer(piece_size);
    std::size_t piece_index = 0;
    std::uintmax_t total_bytes = 0;

    while (input) {
        // Read at most piece_size bytes.
        input.read(buffer.data(),
                   static_cast<std::streamsize>(buffer.size()));

        const std::streamsize bytes_read = input.gcount();

        // No more bytes to write.
        if (bytes_read == 0) {
            break;
        }

        // Generate a filename such as piece_000000.bin.
        std::ostringstream filename;
        filename << output_dir << "/piece_"
                 << std::setw(6) << std::setfill('0')
                 << piece_index << ".bin";

        // Write only the bytes actually read.
        std::ofstream output(filename.str(), std::ios::binary);

        if (!output) {
            std::cerr << "Error: cannot create "
                      << filename.str() << '\n';
            return 1;
        }

        output.write(buffer.data(), bytes_read);

        if (!output) {
            std::cerr << "Error: failed writing "
                      << filename.str() << '\n';
            return 1;
        }

        std::cout << "Created " << filename.str()
                  << " (" << bytes_read << " bytes)\n";

        total_bytes += static_cast<std::uintmax_t>(bytes_read);
        ++piece_index;
    }

    if (input.bad()) {
        std::cerr << "Error: failed while reading input file.\n";
        return 1;
    }

    std::cout << "\nSplitting complete!\n";
    std::cout << "Total bytes: " << total_bytes << '\n';
    std::cout << "Total pieces: " << piece_index << '\n';

    return 0;
}

```

This code uses `std::uintmax_t`, so add this header alongside the other includes:

```
#include <cstdint>
```

## Step 3 — Compile and run

Compile:

```
g++ -std=c++17 -Wall -Wextra main.cpp -o split
```

Run the program with a piece size of 4 bytes:

```
./split shared/example.bin 4
```

Expected output:

```
Created pieces/piece_000000.bin (4 bytes)
Created pieces/piece_000001.bin (4 bytes)
Created pieces/piece_000002.bin (1 bytes)

Splitting complete!
Total bytes: 9
Total pieces: 3
```

Check the generated files:

```
ls -l pieces/
```

You should have:

```
piece_000000.bin   4 bytes
piece_000001.bin   4 bytes
piece_000002.bin   1 byte
```

The last piece is smaller because only one byte remains.

## Step 4 — Understand the algorithm

Original file — 9 bytes

00

01

02

FF

41

42

43

44

45

Split into pieces of at most 4 bytes

Piece 0

00 01 02 FF

4 bytes

Piece 1

41 42 43 44

4 bytes

Piece 2

45

1 byte

The key operation is:

```
input.read(buffer.data(), buffer.size());
std::streamsize bytes_read = input.gcount();
```

- `read()` reads up to the buffer capacity.
- `gcount()` tells us how many bytes were actually read.
- `write()` saves exactly those bytes, including binary data.
- The loop continues until the file has been fully processed.

Why is this useful for P2P? Instead of downloading an entire large file from one peer, a client can later request individual pieces from different peers, verify them, and reconstruct the original file.

Important: Run this on a fresh `pieces/` directory. This simple version does not remove stale pieces left over from a previous run with a larger input file.

## Next step

We'll implement Step 2 — Reconstruct the original file from the pieces, in the correct order, and verify that the reconstructed file is identical to the original using `cmp`.
------------------------------------------------------------
# Lab 9 — Step 2: Reconstruct the Original File

Now we have split `example.bin` into several pieces. Our next goal is to combine those pieces in the correct order to recreate the original file.

## 1. Understand the reconstruction

Our files are:

```
pieces/
├── piece_000000.bin   # First 4 bytes
├── piece_000001.bin   # Next 4 bytes
└── piece_000002.bin   # Last byte
```

The reconstruction process is:

Piece 0 → Piece 1 → Piece 2

Read sequentially in numerical order

reconstructed/example.bin

The original 9-byte file

We must use binary mode and append the bytes in order. Otherwise, binary data could be corrupted or the file could be assembled incorrectly.

## 2. Create `reconstruct.cpp`

Create a new file in `lab9/`:

```

#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>

namespace fs = std::filesystem;

int main() {
    const std::string pieces_dir = "pieces";
    const std::string output_path = "reconstructed/example.bin";

    if (!fs::exists(pieces_dir) || !fs::is_directory(pieces_dir)) {
        std::cerr << "Error: pieces directory does not exist.\n";
        return 1;
    }

    fs::create_directories("reconstructed");

    // Open the reconstructed file in binary mode.
    std::ofstream output(
        output_path,
        std::ios::binary | std::ios::trunc
    );

    if (!output) {
        std::cerr << "Error: cannot create output file.\n";
        return 1;
    }

    std::size_t piece_index = 0;
    std::uintmax_t total_bytes = 0;

    while (true) {
        // Generate the expected piece filename.
        std::ostringstream filename;
        filename << pieces_dir << "/piece_"
                 << std::setw(6) << std::setfill('0')
                 << piece_index << ".bin";

        if (!fs::exists(filename.str())) {
            break;
        }

        // Open the current piece in binary mode.
        std::ifstream input(filename.str(), std::ios::binary);

        if (!input) {
            std::cerr << "Error: cannot open "
                      << filename.str() << '\n';
            return 1;
        }

        // Copy the current piece to the output file.
        char buffer[4096];

        while (input) {
            input.read(buffer, sizeof(buffer));
            const std::streamsize bytes_read = input.gcount();

            if (bytes_read > 0) {
                output.write(buffer, bytes_read);

                if (!output) {
                    std::cerr << "Error: failed writing output.\n";
                    return 1;
                }

                total_bytes +=
                    static_cast<std::uintmax_t>(bytes_read);
            }
        }

        if (input.bad()) {
            std::cerr << "Error reading "
                      << filename.str() << '\n';
            return 1;
        }

        std::cout << "Added " << filename.str() << '\n';
        ++piece_index;
    }

    if (piece_index == 0) {
        std::cerr << "Error: no pieces found.\n";
        return 1;
    }

    output.close();

    if (!output) {
        std::cerr << "Error: failed finalizing output file.\n";
        return 1;
    }

    std::cout << "\nReconstruction complete!\n";
    std::cout << "Pieces processed: " << piece_index << '\n';
    std::cout << "Bytes written: " << total_bytes << '\n';
    std::cout << "Output: " << output_path << '\n';

    return 0;
}

```

Add this include at the top, because we use `std::uintmax_t`:

```
#include <cstdint>
```

## 3. Compile and execute

From inside `lab9/`:

```
g++ -std=c++17 -Wall -Wextra reconstruct.cpp -o reconstruct
```

Run:

```
./reconstruct
```

Expected output:

```
Added pieces/piece_000000.bin
Added pieces/piece_000001.bin
Added pieces/piece_000002.bin

Reconstruction complete!
Pieces processed: 3
Bytes written: 9
Output: reconstructed/example.bin
```

## 4. Verify the result

Use `cmp` to compare the original and reconstructed files byte by byte:

```
cmp shared/example.bin reconstructed/example.bin
```

If the files are identical, `cmp` prints nothing and exits successfully.

You can check the exit status:

```
echo $?
```

Expected result:

```
0
```

You can also inspect the bytes:

```
xxd shared/example.bin
xxd reconstructed/example.bin
```

Both outputs should be identical.

## 5. One important limitation

This reconstruction program expects piece files to have consecutive names starting at `piece_000000.bin`. If a piece is missing, it stops at that point. It also doesn't verify whether pieces were modified or corrupted.

A real torrent-like system needs piece metadata, integrity verification, and missing-piece detection.

## Next step

Lab 9 — Step 3: Add metadata and calculate the number of pieces.

We'll calculate the original file size, piece size, piece count, each piece's index, and its offset—the information a P2P peer needs to request a specific piece.
--------------------------------------------------------------
# Lab 9 — Step 3: Piece Metadata

Before writing the code, let's understand why a P2P file-sharing system needs metadata.

## 1. Why do we need metadata?

In Step 1, we split a file into pieces. In Step 2, we reconstructed it by reading files sequentially.

That works for a local experiment, but imagine downloading a 10 GB file from multiple peers over a network.

Your client needs to know:

- How large is the original file?
- How many pieces exist?
- What is the size of each piece?
- Where does each piece belong in the original file?
- Which piece should the client request from a peer?

Metadata provides this information.

For example, suppose we have a file of 10,500 bytes and choose a piece size of 4,096 bytes.

### Piece metadata example

Original file size: 10,500 bytes · Configured piece size: 4,096 bytes

Piece 0

Offset 0 · 4,096 bytes

Piece 1

Offset 4,096 · 4,096 bytes

P2

Offset 8,192 · 2,308 bytes

The metadata could look like this:

| Piece index | Offset | Size        |
| ----------- | ------ | ----------- |
| 0           | 0      | 4,096 bytes |
| 1           | 4,096  | 4,096 bytes |
| 2           | 8,192  | 2,308 bytes |

The offset tells us where the piece begins in the original file. The size tells us how many bytes belong to that piece.

The formulas are:

\\[ \text{piece count}=\left\lceil\frac{\text{file size}}{\text{piece size}}\right\rceil \\]

\\[ \text{offset}(i)=i\times\text{piece size} \\]

\\[ \text{size}(i)=\min(\text{piece size},\text{file size}-\text{offset}(i)) \\]

Metadata also makes it possible to track missing pieces and associate integrity hashes with each piece in a later step.

## 2. Implement Step 3

We'll create a separate program called `metadata.cpp`. It reads the original file, calculates the piece metadata, and prints a table. This step does not transfer files or calculate hashes yet.

```

#include <algorithm>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iostream>

namespace fs = std::filesystem;

struct PieceMetadata {
    std::uint64_t index;
    std::uint64_t offset;
    std::uint64_t size;
};

int main(int argc, char* argv[]) {
    if (argc != 3) {
        std::cerr << "Usage: " << argv[0]
                  << " <input_file> <piece_size>\n";
        return 1;
    }

    const fs::path input_path = argv[1];
    std::uint64_t piece_size = 0;

    try {
        piece_size = std::stoull(argv[2]);
    } catch (...) {
        std::cerr << "Error: invalid piece size.\n";
        return 1;
    }

    if (piece_size == 0) {
        std::cerr << "Error: piece size must be positive.\n";
        return 1;
    }

    std::ifstream input(input_path, std::ios::binary);

    if (!input) {
        std::cerr << "Error: cannot open input file.\n";
        return 1;
    }

    const std::uint64_t file_size = fs::file_size(input_path);

    // Calculate the number of pieces without floating-point arithmetic.
    const std::uint64_t piece_count =
        file_size / piece_size +
        (file_size % piece_size != 0);

    std::cout << "File: " << input_path << '\n';
    std::cout << "File size: " << file_size << " bytes\n";
    std::cout << "Piece size: " << piece_size << " bytes\n";
    std::cout << "Piece count: " << piece_count << "\n\n";

    std::cout << "Index\tOffset\tSize\n";

    for (std::uint64_t i = 0; i < piece_count; ++i) {
        const std::uint64_t offset = i * piece_size;
        const std::uint64_t size =
            std::min(piece_size, file_size - offset);

        PieceMetadata piece{i, offset, size};

        std::cout << piece.index << '\t'
                  << piece.offset << '\t'
                  << piece.size << '\n';
    }

    return 0;
}

```

Add these two headers if your compiler reports that `std::stoull` is not declared:

```
#include <string>
#include <utility>
```

`std::stoull` is declared in `<string>`.

## 3. Compile and run

```
g++ -std=c++17 -Wall -Wextra metadata.cpp -o metadata
```

Run it using your sample file:

```
./metadata shared/example.bin 4
```

Expected output:

```
File: "shared/example.bin"
File size: 9 bytes
Piece size: 4 bytes
Piece count: 3

Index   Offset  Size
0       0       4
1       4       4
2       8       1
```

The exact file path formatting may vary slightly by compiler.

## 4. How metadata is used in P2P

Consider a client that wants to download piece 2.

Client

Requests piece index 2

Peer

Looks up piece 2: offset 8,192; size 2,308 bytes

Client receives the piece

Stores it at the correct position or in a piece file

In a real system, the peer usually receives a request containing a piece index or a byte range. Both sides must agree on the protocol and piece size.

One important distinction: metadata describes the pieces; it does not prove that they are correct. For that, we'll add hashes in a later step.

## 5. Your task

Try these commands to see how the piece count changes:

```
./metadata shared/example.bin 1
./metadata shared/example.bin 4
./metadata shared/example.bin 5
./metadata shared/example.bin 20
```

Notice that a piece size larger than the file produces just one piece, while a piece size of 1 byte produces nine pieces.

Next step: We'll save the metadata to a file instead of printing it. This will let our future P2P client and peer load the same piece layout.

--------------------------------------------------------------In our P2P file-sharing lab, chunk metadata is a description of each piece of a file: its index, offset, size, and eventually its hash.

Let's see what it looks like in practice.

## 1. Metadata for our example file

Suppose `example.bin` contains 9 bytes and the configured piece size is 4 bytes.

We split it into three pieces:

```
example.bin (9 bytes)
        |
        +---- Piece 0: 4 bytes
        +---- Piece 1: 4 bytes
        +---- Piece 2: 1 byte
```

The metadata table is:

| Index | Offset | Size | Filename           |
| ----- | ------ | ---- | ------------------ |
| 0     | 0      | 4    | `piece_000000.bin` |
| 1     | 4      | 4    | `piece_000001.bin` |
| 2     | 8      | 1    | `piece_000002.bin` |

## 2. What metadata looks like in a file

We could store it in JSON, which is convenient for learning and debugging.

For example, `metadata.json`:

```

{
  "filename": "example.bin",
  "file_size": 9,
  "piece_size": 4,
  "piece_count": 3,
  "pieces": [
    {
      "index": 0,
      "offset": 0,
      "size": 4,
      "filename": "piece_000000.bin"
    },
    {
      "index": 1,
      "offset": 4,
      "size": 4,
      "filename": "piece_000001.bin"
    },
    {
      "index": 2,
      "offset": 8,
      "size": 1,
      "filename": "piece_000002.bin"
    }
  ]
}

```

This JSON file describes the layout of the original file. It does not contain the actual piece bytes.

## 3. Metadata with integrity hashes

A P2P system also needs to detect corrupted or modified pieces. We can extend the metadata with a SHA-256 hash for each piece:

```
{
  "filename": "example.bin",
  "file_size": 9,
  "piece_size": 4,
  "pieces": [
    {
      "index": 0,
      "offset": 0,
      "size": 4,
      "sha256": "hash_of_piece_0"
    },
    {
      "index": 1,
      "offset": 4,
      "size": 4,
      "sha256": "hash_of_piece_1"
    },
    {
      "index": 2,
      "offset": 8,
      "size": 1,
      "sha256": "hash_of_piece_2"
    }
  ]
}
```

The hash strings here are placeholders, not actual calculated hashes.

When a client downloads a piece, it calculates the hash of the received bytes and compares it with the expected hash.

- Match: the piece passes the integrity check.
- Mismatch: the piece may be corrupted or maliciously modified and should be rejected.

## 4. How metadata is used between peers

Peer A — File owner

File + metadata + pieces

Peer B — Downloader

Reads metadata, requests pieces, verifies hashes, reconstructs the file

The metadata lets Peer B know which pieces it needs and how to validate them. In a real torrent protocol, metadata and hashes have specific formats; our JSON is a simplified learning format.

For our next lab step, we can make `metadata.cpp` generate `metadata.json` automatically, including the piece indices, offsets, sizes, and actual SHA-256 hashes.

--------------------------------------------------------------
Here is the complete `metadata.cpp` for Lab 9, Step 3. It calculates the file size, piece count, index, offset, and size of every chunk, then prints the metadata.

## `metadata.cpp`

```

#include <algorithm>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <string>

namespace fs = std::filesystem;

struct PieceMetadata {
    std::uint64_t index;
    std::uint64_t offset;
    std::uint64_t size;
};

int main(int argc, char* argv[]) {
    if (argc != 3) {
        std::cerr << "Usage: " << argv[0]
                  << " <input_file> <piece_size>\n";
        return 1;
    }

    const fs::path input_path = argv[1];
    std::uint64_t piece_size;

    try {
        piece_size = std::stoull(argv[2]);
    } catch (...) {
        std::cerr << "Error: invalid piece size.\n";
        return 1;
    }

    if (piece_size == 0 ||
        argv[2][0] == '-') {
        std::cerr << "Error: piece size must be positive.\n";
        return 1;
    }

    std::ifstream input(input_path, std::ios::binary);

    if (!input) {
        std::cerr << "Error: cannot open input file.\n";
        return 1;
    }

    const std::uint64_t file_size = fs::file_size(input_path);

    const std::uint64_t piece_count =
        file_size / piece_size +
        (file_size % piece_size != 0);

    std::cout << "File: " << input_path << '\n';
    std::cout << "File size: " << file_size << " bytes\n";
    std::cout << "Piece size: " << piece_size << " bytes\n";
    std::cout << "Piece count: " << piece_count << "\n\n";

    std::cout << "Index\tOffset\tSize\n";

    for (std::uint64_t i = 0; i < piece_count; ++i) {
        const std::uint64_t offset = i * piece_size;
        const std::uint64_t size =
            std::min(piece_size, file_size - offset);

        PieceMetadata piece{i, offset, size};

        std::cout << piece.index << '\t'
                  << piece.offset << '\t'
                  << piece.size << '\n';
    }

    return 0;
}

```

## Compile and run

```
g++ -std=c++17 -Wall -Wextra metadata.cpp -o metadata
./metadata shared/example.bin 4
```

Expected output for the 9-byte example:

```
File: "shared/example.bin"
File size: 9 bytes
Piece size: 4 bytes
Piece count: 3

Index   Offset  Size
0       0       4
1       4       4
2       8       1
```

Note: This version displays metadata in the terminal. It does not yet save `metadata.json` or calculate SHA-256 hashes. Those can be added as the next improvement.