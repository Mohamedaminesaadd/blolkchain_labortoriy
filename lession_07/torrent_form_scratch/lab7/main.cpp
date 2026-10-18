
#include <array>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <string>

bool copy_binary_file(
    const std::string& source_path,
    const std::string& destination_path
) {
    // 1. Open the source file in binary mode.
    std::ifstream source(
        source_path,
        std::ios::binary
    );

    if (!source) {
        std::cerr << "Error: cannot open source file\n";
        return false;
    }

    // 2. Open the destination file in binary mode.
    std::ofstream destination(
        destination_path,
        std::ios::binary | std::ios::trunc
    );

    if (!destination) {
        std::cerr << "Error: cannot open destination file\n";
        return false;
    }

    // 3. Use a fixed-size buffer.
    std::array<char, 4096> buffer{};

    // 4. Read and write until the source is exhausted.
    while (source) {
        source.read(
            buffer.data(),
            static_cast<std::streamsize>(buffer.size())
        );

        const std::streamsize bytes_read = source.gcount();

        if (bytes_read > 0) {
            destination.write(buffer.data(), bytes_read);

            if (!destination) {
                std::cerr << "Error: writing destination failed\n";
                return false;
            }
        }
    }

    // 5. Check whether reading ended normally.
    if (!source.eof()) {
        std::cerr << "Error: reading source failed\n";
        return false;
    }

    destination.close();

    if (!destination) {
        std::cerr << "Error: closing destination failed\n";
        return false;
    }

    std::cout << "File copied successfully!\n";
    return true;
}

int main() {
    std::string source_path;
    std::string destination_path;

    std::cout << "Source file: ";
    std::getline(std::cin, source_path);

    std::cout << "Destination file: ";
    std::getline(std::cin, destination_path);

    if (source_path == destination_path) {
        std::cerr << "Error: source and destination must differ\n";
        return 1;
    }

    if (!copy_binary_file(source_path, destination_path)) {
        return 1;
    }

    return 0;
}
