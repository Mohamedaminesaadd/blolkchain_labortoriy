# Lab 7 — File Reading and Writing in Binary Mode

Let's start the next stage of your C++ P2P file-sharing project. We'll learn to read files as raw bytes, write them without modifying their contents, and prepare for transferring files between peers.

## 1. What is binary mode?

There are two common ways to read a file in C++.

- Text mode: intended for text; some platforms may translate newline characters.
- Binary mode: reads and writes raw bytes without text-mode translations.

For a P2P file-sharing application, binary mode is essential because files can contain arbitrary data: images, PDFs, ZIP archives, audio, executables, and more.

Original file

PDF, image, archive, or any file

Read binary bytes

`std::ifstream` + `std::ios::binary`

Write binary bytes

`std::ofstream` + `std::ios::binary`

Copied file

Should contain exactly the same bytes

## 2. Step 1 — Create a binary file copier

Create a directory and a source file:

```
mkdir -p lab07_binary_files
cd lab07_binary_files
nano copy_file.cpp
```

Write this code:

```

#include <iostream>
#include <fstream>
#include <vector>

int main() {
    const char* source = "input.bin";
    const char* destination = "output.bin";

    // Open the source file in binary mode.
    std::ifstream input(source, std::ios::binary);

    if (!input) {
        std::cerr << "Cannot open input file\n";
        return 1;
    }

    // Read the file as raw bytes.
    std::vector<char> data(
        (std::istreambuf_iterator<char>(input)),
        std::istreambuf_iterator<char>()
    );

    input.close();

    // Open the destination in binary mode.
    std::ofstream output(
        destination,
        std::ios::binary
    );

    if (!output) {
        std::cerr << "Cannot open output file\n";
        return 1;
    }

    // Write the exact bytes.
    output.write(data.data(), data.size());

    if (!output) {
        std::cerr << "Failed to write output file\n";
        return 1;
    }

    output.close();

    std::cout << "Copied " << data.size()
              << " bytes successfully\n";

    return 0;
}

```

## 3. Step 2 — Compile and test

Compile:

```
g++ -std=c++17 -Wall -Wextra copy_file.cpp -o copy_file
```

Create a sample binary file:

```
printf '\x00\x01\x02\xFF\x41\x42\x43' > input.bin
```

Run the program:

```
./copy_file
```

Expected output:

```
Copied 7 bytes successfully
```

Compare the files:

```
cmp input.bin output.bin
```

If `cmp` prints nothing and returns exit code `0`, the files are identical.

Inspect the bytes:

```
xxd input.bin
xxd output.bin
```

You should see the same byte sequence in both files.

## 4. Understand the key C++ operations

| Code                | Purpose                                  |
| ------------------- | ---------------------------------------- |
| `std::ifstream`     | Opens a file for reading                 |
| `std::ofstream`     | Opens a file for writing                 |
| `std::ios::binary`  | Disables text-mode transformations       |
| `std::vector<char>` | Stores the bytes read into memory        |
| `output.write()`    | Writes bytes, including zero bytes       |
| `cmp`               | Verifies byte-for-byte equality on Linux |

This first implementation loads the entire file into memory. That's fine for a small exercise, but it isn't appropriate for very large files.

## 5. Your Lab 7 roadmap

1. Binary file copying — read and write arbitrary bytes.
2. Chunk-based reading — process files in fixed-size blocks instead of loading everything into memory.
3. File metadata — obtain file size and track chunk offsets.
4. Prepare for P2P transfer — define how chunks will be read, sent, received, and written by peers.

Your first task: run the binary copier and verify that `cmp input.bin output.bin` succeeds. Then we'll implement chunk-based file reading, which is much closer to how a BitTorrent-like file-sharing system operates.