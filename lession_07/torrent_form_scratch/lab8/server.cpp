
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
