
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
