# Lab 8 — File Transfer Between Two Peers

In Lab 7, you learned how to read and write files in binary mode. In Lab 8, we'll use that knowledge to transfer a real file from one computer or peer to another over TCP.

The goal is to build a basic version of the file-transfer mechanism used in a P2P file-sharing application.

## 1. What are we going to build?

Imagine Peer A has a file named `document.pdf`, and Peer B wants to download it.

Peer A — Sender

document.pdf

TCP connection

File bytes + transfer metadata

Peer B — Receiver

received_document.pdf

Peer A reads the file in binary mode and sends its contents over a TCP connection. Peer B receives the bytes and writes them to a new file.

The destination file should be byte-for-byte identical to the source.

## 2. How does the transfer work?

We need a protocol so both peers know what data is being sent.

1. Connect: Peer B establishes a TCP connection to Peer A.
2. Request: Peer B requests a specific file.
3. Metadata: Peer A sends the file size so B knows how many bytes to expect.
4. Read and send: Peer A reads the file in binary chunks and sends them over TCP.
5. Receive and write: Peer B writes the received bytes to disk.
6. Verify: Compare the source and destination files using `cmp` or SHA-256 hashes.

## 3. Example protocol

For our first implementation, we'll use a simple protocol:

```
Peer B                         Peer A
  |                              |
  |------ GET document.pdf ----->|
  |                              |
  |<----- FILE_SIZE: 1024 -------|
  |                              |
  |<----- File bytes ------------|
  |<----- File bytes ------------|
  |<----- File bytes ------------|
  |                              |
  |       Transfer complete      |
```

The actual implementation should use a well-defined framing format rather than relying on the displayed text alone. TCP is a byte stream, so one `send()` call does not necessarily correspond to one `recv()` call.

## 4. What will you learn?

| Concept                  | Why it matters                                              |
| ------------------------ | ----------------------------------------------------------- |
| TCP client and server    | Establish a connection between peers                        |
| Binary file I/O          | Preserve arbitrary file contents                            |
| Chunk-based transfer     | Transfer large files without loading them entirely into RAM |
| File size and framing    | Know when the transfer is complete                          |
| Partial reads and writes | Handle TCP correctly                                        |
| SHA-256 verification     | Check whether the received file matches the source          |

## 5. How this connects to BitTorrent

Lab 8 will transfer an entire file between two peers. Later, you can extend it to divide files into pieces, assign piece indexes, verify each piece using hashes, and download different pieces from multiple peers.

That gives you the foundation for a simplified BitTorrent-like system.

Our first coding step will be: create a TCP file server that opens a file in binary mode and sends it to a client in fixed-size chunks. We'll test it locally before adding file requests and more advanced protocol features.


# Lab 8 — File Transfer Between Two Peers using Boost.Asio

We'll implement your requested `lab8/` project using C++17, Boost.Asio, TCP, and binary file I/O.

The server will expose only files inside `shared/`, while the client requests a filename and saves the received file inside `downloads/`. We'll transfer files in fixed-size chunks, so the entire file does not need to fit in memory.

## Architecture

Client

Requests a filename and receives file bytes

`client.cpp`

TCP + Boost.Asio

Request → status + file size → exact number of bytes

Server

Validates the requested filename and streams the file

`server.cpp`

## 1. Project structure

```
lab8/
├── server.cpp
├── client.cpp
├── CMakeLists.txt
├── shared/
│   └── example.bin
└── downloads/
```

The protocol will use a newline-terminated request and a fixed-size binary header:

- Client sends a filename request.
- Server sends a status byte and an 8-byte file size.
- If successful, server sends exactly that many bytes.
- Client writes the bytes to disk in chunks.

## 2. `server.cpp`

The server listens on port `5000`, accepts a filename request, validates it, and streams the file in 8 KiB chunks. This first version uses synchronous Boost.Asio operations to keep the transfer logic easy to understand.

```

#include <boost/asio.hpp>

#include <array>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <string>

using boost::asio::ip::tcp;
namespace fs = std::filesystem;

constexpr unsigned short PORT = 5000;
constexpr std::size_t CHUNK_SIZE = 8192;

void send_header(tcp::socket& socket, char status,
                 std::uint64_t file_size) {
    // Header: 1 status byte + 8 size bytes, big-endian.
    std::array<unsigned char, 9> header{};
    header[0] = static_cast<unsigned char>(status);

    for (int i = 0; i < 8; ++i) {
        header[1 + i] = static_cast<unsigned char>(
            (file_size >> (56 - 8 * i)) & 0xFF
        );
    }

    boost::asio::write(socket, boost::asio::buffer(header));
}

bool safe_filename(const std::string& name) {
    if (name.empty() || name == "." || name == "..") {
        return false;
    }

    // Accept filenames only, not paths.
    return name.find('/') == std::string::npos &&
           name.find('\\') == std::string::npos &&
           name.find('\0') == std::string::npos;
}

void handle_client(tcp::socket socket, const fs::path& shared_root) {
    try {
        // Request format: filename followed by newline.
        boost::asio::streambuf request_buffer;

        boost::asio::read_until(
            socket, request_buffer, '\n'
        );

        std::istream request_stream(&request_buffer);
        std::string filename;
        std::getline(request_stream, filename);

        if (!safe_filename(filename)) {
            send_header(socket, 'E', 0);
            return;
        }

        // Resolve paths to prevent traversal and symlink escapes.
        std::error_code ec;
        fs::path file_path =
            fs::canonical(shared_root / filename, ec);

        if (ec ||
            file_path.parent_path() != shared_root ||
            !fs::is_regular_file(file_path, ec) ||
            ec) {
            send_header(socket, 'E', 0);
            return;
        }

        const std::uintmax_t size = fs::file_size(file_path, ec);

        if (ec || size > UINT64_MAX) {
            send_header(socket, 'E', 0);
            return;
        }

        std::ifstream file(file_path, std::ios::binary);

        if (!file) {
            send_header(socket, 'E', 0);
            return;
        }

        send_header(socket, 'O', static_cast<std::uint64_t>(size));

        std::array<char, CHUNK_SIZE> chunk{};
        std::uint64_t remaining = static_cast<std::uint64_t>(size);

        while (remaining > 0) {
            const std::size_t wanted =
                static_cast<std::size_t>(
                    std::min<std::uint64_t>(remaining, chunk.size())
                );

            file.read(chunk.data(),
                      static_cast<std::streamsize>(wanted));

            const std::streamsize count = file.gcount();

            if (count <= 0) {
                std::cerr << "File read failed during transfer\n";
                return;
            }

            boost::asio::write(
                socket,
                boost::asio::buffer(
                    chunk.data(),
                    static_cast<std::size_t>(count)
                )
            );

            remaining -= static_cast<std::uint64_t>(count);
        }

        std::cout << "Sent " << filename
                  << " (" << size << " bytes)\n";

    } catch (const std::exception& e) {
        std::cerr << "Client transfer error: "
                  << e.what() << '\n';
    }
}

int main() {
    try {
        const fs::path shared_root =
            fs::canonical(fs::path("shared"));

        boost::asio::io_context io;
        tcp::acceptor acceptor(
            io, tcp::endpoint(tcp::v4(), PORT)
        );

        std::cout << "File server listening on port "
                  << PORT << '\n';
        std::cout << "Shared directory: "
                  << shared_root << '\n';

        while (true) {
            tcp::socket socket(io);
            acceptor.accept(socket);

            handle_client(std::move(socket), shared_root);
        }

    } catch (const std::exception& e) {
        std::cerr << "Server error: " << e.what() << '\n';
        return 1;
    }

    return 0;
}

```

## 3. `client.cpp`

The client sends the requested filename, reads the 9-byte header, and then receives exactly the advertised number of bytes. It writes the data to a temporary file first and renames it after a successful transfer.

```

#include <boost/asio.hpp>

#include <array>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <string>

using boost::asio::ip::tcp;
namespace fs = std::filesystem;

constexpr std::size_t CHUNK_SIZE = 8192;

std::uint64_t decode_size(const std::array<unsigned char, 9>& header) {
    std::uint64_t size = 0;

    for (int i = 0; i < 8; ++i) {
        size = (size << 8) | header[1 + i];
    }

    return size;
}

bool safe_filename(const std::string& name) {
    if (name.empty() || name == "." || name == "..") {
        return false;
    }

    return name.find('/') == std::string::npos &&
           name.find('\\') == std::string::npos &&
           name.find('\0') == std::string::npos;
}

int main(int argc, char* argv[]) {
    if (argc != 3) {
        std::cerr << "Usage: ./client HOST FILENAME\n"
                  << "Example: ./client 127.0.0.1 example.bin\n";
        return 1;
    }

    const std::string host = argv[1];
    const std::string filename = argv[2];

    if (!safe_filename(filename)) {
        std::cerr << "Please specify a filename, not a path.\n";
        return 1;
    }

    const fs::path destination =
        fs::path("downloads") / filename;
    const fs::path temporary =
        fs::path("downloads") / (filename + ".part");

    try {
        fs::create_directories("downloads");

        boost::asio::io_context io;
        tcp::resolver resolver(io);
        tcp::socket socket(io);

        auto endpoints = resolver.resolve(host, "5000");
        boost::asio::connect(socket, endpoints);

        // Send filename followed by newline.
        const std::string request = filename + "\n";
        boost::asio::write(socket, boost::asio::buffer(request));

        // Read the fixed-size response header.
        std::array<unsigned char, 9> header{};
        boost::asio::read(socket, boost::asio::buffer(header));

        if (header[0] != 'O') {
            std::cerr << "Server rejected the request or file "
                         "does not exist.\n";
            return 1;
        }

        const std::uint64_t file_size = decode_size(header);
        std::cout << "Downloading " << filename
                  << " (" << file_size << " bytes)\n";

        std::ofstream output(temporary, std::ios::binary);

        if (!output) {
            std::cerr << "Cannot create temporary output file.\n";
            return 1;
        }

        std::array<char, CHUNK_SIZE> chunk{};
        std::uint64_t remaining = file_size;

        while (remaining > 0) {
            const std::size_t wanted =
                static_cast<std::size_t>(
                    std::min<std::uint64_t>(remaining, chunk.size())
                );

            // read() waits for exactly the requested bytes
            // unless the connection closes prematurely.
            boost::asio::read(
                socket,
                boost::asio::buffer(chunk.data(), wanted)
            );

            output.write(
                chunk.data(),
                static_cast<std::streamsize>(wanted)
            );

            if (!output) {
                throw std::runtime_error("Failed to write downloaded data");
            }

            remaining -= wanted;
        }

        output.close();

        if (!output) {
            throw std::runtime_error("Failed to finish output file");
        }

        // Replace an existing destination only after transfer success.
        std::error_code ec;
        fs::rename(temporary, destination, ec);

        if (ec) {
            // Some platforms don't replace an existing destination.
            std::error_code remove_error;
            fs::remove(destination, remove_error);
            ec.clear();
            fs::rename(temporary, destination, ec);
        }

        if (ec) {
            throw std::runtime_error(
                "Cannot finalize download: " + ec.message()
            );
        }

        std::cout << "Download complete: "
                  << destination << '\n';

    } catch (const std::exception& e) {
        std::cerr << "Download failed: " << e.what() << '\n';
        return 1;
    }

    return 0;
}

```

## 4. `CMakeLists.txt`

Create `CMakeLists.txt` in the project root:

```

cmake_minimum_required(VERSION 3.16)

project(Lab8FileTransfer LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(Boost REQUIRED COMPONENTS system)

add_executable(server server.cpp)
add_executable(client client.cpp)

target_link_libraries(server PRIVATE Boost::system)
target_link_libraries(client PRIVATE Boost::system)

```

## 5. Build the project

Install the dependencies if you haven't already:

```
sudo apt update
sudo apt install build-essential cmake libboost-dev libboost-system-dev
```

Create the directories:

```
mkdir -p lab8/shared lab8/downloads
cd lab8
```

Your directory should now contain:

```
lab8/
├── server.cpp
├── client.cpp
├── CMakeLists.txt
├── shared/
└── downloads/
```

Build both programs:

```
cmake -S . -B build
cmake --build build
```

The compiled executables will be:

```
build/server
build/client
```

## 6. Test the transfer

First, create a test file inside the server's shared directory:

```
printf '\x00\x01\x02\xFF\x41\x42\x43' > shared/example.bin
```

Start the server from the `lab8/` directory:

```
./build/server
```

Open another terminal, navigate to the same `lab8/` directory, and run:

```
./build/client 127.0.0.1 example.bin
```

Expected client output:

```
Downloading example.bin (7 bytes)
Download complete: "downloads/example.bin"
```

The server should report that it sent the file.

Verify the result:

```
cmp shared/example.bin downloads/example.bin
sha256sum shared/example.bin downloads/example.bin
```

`cmp` should print nothing if the files are identical. The two SHA-256 hashes should also match.

You can test a larger file too:

```
dd if=/dev/urandom of=shared/large.bin bs=1M count=10
./build/client 127.0.0.1 large.bin
cmp shared/large.bin downloads/large.bin
```

## 7. What you have implemented

| Component              | Responsibility                                                 |
| ---------------------- | -------------------------------------------------------------- |
| `server.cpp`           | Accepts requests and sends approved files                      |
| `client.cpp`           | Requests a file and saves the received bytes                   |
| Boost.Asio TCP         | Handles network connections and byte transfer                  |
| Binary streams         | Preserve the exact file contents                               |
| Fixed-size chunks      | Avoid loading the entire file into memory                      |
| File-size header       | Tells the client exactly how many bytes to receive             |
| Temporary `.part` file | Prevents an incomplete transfer from being treated as complete |

Limitations of this first version: the server uses synchronous Boost.Asio operations and handles one client at a time. The client does not yet verify a cryptographic hash, and an interrupted download may leave a `.part` file. Later, we can improve this with asynchronous transfers, SHA-256 verification, and resumable downloads.

Your first milestone is to transfer `example.bin` successfully and verify it with `cmp`.