#include "file_metadata.hpp"

#include <iostream>

int main() {
    constexpr std::uint32_t PIECE_SIZE = 1024 * 1024;

    const std::uint64_t file_size =
        2ULL * 1024 * 1024 + 512 * 1024;

    const auto total_pieces =
        calculate_total_pieces(file_size, PIECE_SIZE);

    FileMetadata metadata{
        "large.bin",
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