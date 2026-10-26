// Lab 9 - File splitting into pieces (complete lab)
//
//   lab9 split       [input_file=shared/example.bin] [piece_size=1048576] [pieces_dir=pieces]
//   lab9 reconstruct [pieces_dir=pieces] [output_dir=reconstructed]
//   lab9 verify      <file_a> <file_b>
//
// split       Step 1-3: read the file in fixed-size binary pieces, assign each an
//                       index/offset/size, save them as pieces/piece_000000.bin ...
//                       and write pieces/metadata.json (with a SHA-256 per piece).
// reconstruct Step 4:   rebuild the original file from the pieces in index order,
//                       checking every piece's size and SHA-256 on the way.
// verify      Step 5:   compare two files by size and SHA-256.

#include <algorithm>
#include <cctype>
#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <exception>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <system_error>
#include <utility>
#include <vector>

#include "sha256.hpp"

namespace fs = std::filesystem;

constexpr std::uint64_t kDefaultPieceSize = 1024 * 1024;  // 1 MiB
constexpr const char* kMetadataName = "metadata.json";

// ---------------------------------------------------------------------------
// Data model + piece layout
// ---------------------------------------------------------------------------

struct PieceInfo {
    std::uint64_t index = 0;
    std::uint64_t offset = 0;
    std::uint64_t size = 0;
    std::string file;    // piece file name inside the pieces directory
    std::string sha256;  // lowercase hex digest of the piece bytes
};

struct Metadata {
    std::string filename;  // name of the original file
    std::uint64_t file_size = 0;
    std::uint64_t piece_size = 0;
    std::string file_sha256;  // digest of the whole original file
    std::vector<PieceInfo> pieces;
};

// piece count = ceil(file_size / piece_size), written without overflow
std::uint64_t piece_count_for(std::uint64_t file_size, std::uint64_t piece_size) {
    return file_size / piece_size + (file_size % piece_size != 0 ? 1 : 0);
}

std::string piece_filename(std::uint64_t index) {
    std::ostringstream name;
    name << "piece_" << std::setw(6) << std::setfill('0') << index << ".bin";
    return name.str();
}

// offset = index * piece_size
// size   = min(piece_size, file_size - offset)   (the last piece may be smaller)
std::vector<PieceInfo> compute_pieces(std::uint64_t file_size, std::uint64_t piece_size) {
    const std::uint64_t count = piece_count_for(file_size, piece_size);
    std::vector<PieceInfo> pieces;
    pieces.reserve(static_cast<std::size_t>(count));
    for (std::uint64_t i = 0; i < count; ++i) {
        PieceInfo p;
        p.index = i;
        p.offset = i * piece_size;
        p.size = std::min(piece_size, file_size - p.offset);
        p.file = piece_filename(i);
        pieces.push_back(std::move(p));
    }
    return pieces;
}

// ---------------------------------------------------------------------------
// Small helpers
// ---------------------------------------------------------------------------

std::string sha256_of_file(const fs::path& path) {
    std::ifstream in(path, std::ios::binary);
    if (!in) throw std::runtime_error("cannot open " + path.string());

    Sha256 hash;
    std::vector<char> chunk(64 * 1024);
    while (in) {
        in.read(chunk.data(), static_cast<std::streamsize>(chunk.size()));
        const std::streamsize n = in.gcount();
        if (n > 0) hash.update(chunk.data(), static_cast<std::size_t>(n));
    }
    if (in.bad()) throw std::runtime_error("read error on " + path.string());
    return hash.finalize_hex();
}


std::uint64_t parse_piece_size(const std::string& text) {
    if (text.empty() || text.find_first_not_of("0123456789") != std::string::npos) {
        throw std::invalid_argument("invalid piece size: '" + text + "'");
    }
    std::uint64_t value = 0;
    try {
        value = std::stoull(text);
    } catch (const std::exception&) {
        throw std::invalid_argument("piece size out of range: '" + text + "'");
    }
    if (value == 0) throw std::invalid_argument("piece size must be > 0");
    return value;
}



// Names read from metadata.json must be plain file names, never paths
// (prevents "../../something" from escaping the pieces/output directories).
void require_plain_filename(const std::string& name) {
    const fs::path p(name);
    if (name.empty() || name == "." || name == ".." || p.filename() != p) {
        throw std::runtime_error("unsafe file name in metadata: '" + name + "'");
    }
}

// Remove leftovers of a previous run (e.g. a different piece size); stale
// pieces would otherwise end up mixed with the new ones.
void clear_old_pieces(const fs::path& dir) {
    std::vector<fs::path> stale;
    for (const auto& entry : fs::directory_iterator(dir)) {
        const std::string name = entry.path().filename().string();
        const bool is_piece = name.rfind("piece_", 0) == 0 && entry.path().extension() == ".bin";
        if (entry.is_regular_file() && (is_piece || name == kMetadataName)) {
            stale.push_back(entry.path());
        }
    }
    for (const auto& p : stale) fs::remove(p);
}

// ---------------------------------------------------------------------------
// Minimal JSON reader (objects, arrays, strings, unsigned integers) - just
// enough to load the metadata.json this program writes.
// ---------------------------------------------------------------------------

struct Json {
    enum class Type { Number, String, Array, Object } type = Type::Number;
    std::uint64_t number = 0;
    std::string str;
    std::vector<Json> array;
    std::vector<std::pair<std::string, Json>> object;

    const Json& at(const std::string& key) const {
        for (const auto& kv : object) {
            if (kv.first == key) return kv.second;
        }
        throw std::runtime_error("metadata.json: missing key '" + key + "'");
    }
    std::uint64_t as_number() const {
        if (type != Type::Number) throw std::runtime_error("metadata.json: expected a number");
        return number;
    }
    const std::string& as_string() const {
        if (type != Type::String) throw std::runtime_error("metadata.json: expected a string");
        return str;
    }
    const std::vector<Json>& as_array() const {
        if (type != Type::Array) throw std::runtime_error("metadata.json: expected an array");
        return array;
    }
};

class JsonParser {
public:
    explicit JsonParser(const std::string& text) : s_(text) {}

    Json parse() {
        Json v = value();
        skip_ws();
        if (pos_ != s_.size()) fail("unexpected trailing data");
        return v;
    }

private:
    [[noreturn]] void fail(const std::string& msg) const {
        throw std::runtime_error("metadata.json: " + msg + " (at offset " + std::to_string(pos_) +
                                 ")");
    }
    void skip_ws() {
        while (pos_ < s_.size() && std::isspace(static_cast<unsigned char>(s_[pos_]))) ++pos_;
    }
    char peek() {
        skip_ws();
        if (pos_ >= s_.size()) fail("unexpected end of file");
        return s_[pos_];
    }
    void expect(char c) {
        if (peek() != c) fail(std::string("expected '") + c + "'");
        ++pos_;
    }

    Json value() {
        const char c = peek();
        if (c == '{') return object();
        if (c == '[') return array();
        if (c == '"') {
            Json j;
            j.type = Json::Type::String;
            j.str = string_literal();
            return j;
        }
        if (std::isdigit(static_cast<unsigned char>(c))) return number();
        fail("unsupported value");
    }

    Json object() {
        Json j;
        j.type = Json::Type::Object;
        expect('{');
        if (peek() == '}') {
            ++pos_;
            return j;
        }
        while (true) {
            std::string key = string_literal();
            expect(':');
            Json v = value();
            j.object.emplace_back(std::move(key), std::move(v));
            const char c = peek();
            ++pos_;
            if (c == '}') return j;
            if (c != ',') fail("expected ',' or '}'");
        }
    }

    Json array() {
        Json j;
        j.type = Json::Type::Array;
        expect('[');
        if (peek() == ']') {
            ++pos_;
            return j;
        }
        while (true) {
            j.array.push_back(value());
            const char c = peek();
            ++pos_;
            if (c == ']') return j;
            if (c != ',') fail("expected ',' or ']'");
        }
    }

    Json number() {
        Json j;
        j.type = Json::Type::Number;
        std::uint64_t v = 0;
        while (pos_ < s_.size() && std::isdigit(static_cast<unsigned char>(s_[pos_]))) {
            const unsigned digit = static_cast<unsigned>(s_[pos_] - '0');
            if (v > (UINT64_MAX - digit) / 10) fail("number out of range");
            v = v * 10 + digit;
            ++pos_;
        }
        j.number = v;
        return j;
    }

    std::string string_literal() {
        if (peek() != '"') fail("expected a string");
        ++pos_;
        std::string out;
        while (true) {
            if (pos_ >= s_.size()) fail("unterminated string");
            const char c = s_[pos_++];
            if (c == '"') return out;
            if (c != '\\') {
                out += c;
                continue;
            }
            if (pos_ >= s_.size()) fail("unterminated escape");
            const char e = s_[pos_++];
            switch (e) {
                case '"': out += '"'; break;
                case '\\': out += '\\'; break;
                case '/': out += '/'; break;
                case 'n': out += '\n'; break;
                case 't': out += '\t'; break;
                case 'r': out += '\r'; break;
                case 'b': out += '\b'; break;
                case 'f': out += '\f'; break;
                case 'u': {
                    if (pos_ + 4 > s_.size()) fail("bad \\u escape");
                    unsigned code = 0;
                    for (int i = 0; i < 4; ++i) {
                        const char h = s_[pos_++];
                        if (!std::isxdigit(static_cast<unsigned char>(h))) fail("bad \\u escape");
                        code = code * 16 + static_cast<unsigned>(
                                               std::isdigit(static_cast<unsigned char>(h))
                                                   ? h - '0'
                                                   : std::tolower(static_cast<unsigned char>(h)) -
                                                         'a' + 10);
                    }
                    if (code > 0x7f) fail("non-ASCII \\u escapes are not supported");
                    out += static_cast<char>(code);
                    break;
                }
                default: fail("unknown escape sequence");
            }
        }
    }

    const std::string& s_;
    std::size_t pos_ = 0;
};

// ---------------------------------------------------------------------------
// metadata.json read / write
// ---------------------------------------------------------------------------

std::string json_escape(const std::string& s) {
    std::string out;
    for (const unsigned char c : s) {
        if (c == '"') {
            out += "\\\"";
        } else if (c == '\\') {
            out += "\\\\";
        } else if (c < 0x20) {
            char buf[8];
            std::snprintf(buf, sizeof buf, "\\u%04x", static_cast<unsigned>(c));
            out += buf;
        } else {
            out += static_cast<char>(c);
        }
    }
    return out;
}

void write_metadata(const fs::path& path, const Metadata& md) {
    std::ofstream out(path, std::ios::binary | std::ios::trunc);
    if (!out) throw std::runtime_error("cannot create " + path.string());

    out << "{\n"
        << "  \"filename\": \"" << json_escape(md.filename) << "\",\n"
        << "  \"file_size\": " << md.file_size << ",\n"
        << "  \"piece_size\": " << md.piece_size << ",\n"
        << "  \"piece_count\": " << md.pieces.size() << ",\n"
        << "  \"file_sha256\": \"" << md.file_sha256 << "\",\n"
        << "  \"pieces\": [";
    for (std::size_t i = 0; i < md.pieces.size(); ++i) {
        const PieceInfo& p = md.pieces[i];
        out << (i == 0 ? "" : ",") << "\n    {\"index\": " << p.index << ", \"offset\": " << p.offset
            << ", \"size\": " << p.size << ", \"filename\": \"" << json_escape(p.file)
            << "\", \"sha256\": \"" << p.sha256 << "\"}";
    }
    out << (md.pieces.empty() ? "" : "\n  ") << "]\n}\n";

    out.close();
    if (!out) throw std::runtime_error("failed writing " + path.string());
}

Metadata load_metadata(const fs::path& path) {
    std::ifstream in(path, std::ios::binary);
    if (!in) throw std::runtime_error("cannot open " + path.string() + " (did you run 'split'?)");
    std::ostringstream buffer;
    buffer << in.rdbuf();
    const std::string text = buffer.str();
    const Json root = JsonParser(text).parse();

    Metadata md;
    md.filename = root.at("filename").as_string();
    md.file_size = root.at("file_size").as_number();
    md.piece_size = root.at("piece_size").as_number();
    md.file_sha256 = root.at("file_sha256").as_string();
    require_plain_filename(md.filename);
    if (md.piece_size == 0) throw std::runtime_error("metadata.json: piece_size must be > 0");

    // The layout must follow the lab formulas exactly, otherwise the metadata
    // is inconsistent (or has been tampered with).
    const std::vector<Json>& list = root.at("pieces").as_array();
    const std::uint64_t expected = piece_count_for(md.file_size, md.piece_size);
    if (root.at("piece_count").as_number() != expected || list.size() != expected) {
        throw std::runtime_error("metadata.json: piece count does not match file_size/piece_size");
    }
    for (std::uint64_t i = 0; i < expected; ++i) {
        const Json& j = list[static_cast<std::size_t>(i)];
        PieceInfo p;
        p.index = j.at("index").as_number();
        p.offset = j.at("offset").as_number();
        p.size = j.at("size").as_number();
        p.file = j.at("filename").as_string();
        p.sha256 = j.at("sha256").as_string();

        const std::uint64_t offset = i * md.piece_size;
        const std::uint64_t size = std::min(md.piece_size, md.file_size - offset);
        if (p.index != i || p.offset != offset || p.size != size) {
            throw std::runtime_error("metadata.json: piece " + std::to_string(i) +
                                     " has an inconsistent index/offset/size");
        }
        require_plain_filename(p.file);
        md.pieces.push_back(std::move(p));
    }
    return md;
}

// ---------------------------------------------------------------------------
// Command: split  (Steps 1-3)
// ---------------------------------------------------------------------------

int cmd_split(const std::vector<std::string>& args) {
    if (args.size() > 3) throw std::invalid_argument("split: too many arguments");
    const fs::path input = args.size() > 0 ? args[0] : "shared/example.bin";
    const std::uint64_t piece_size = args.size() > 1 ? parse_piece_size(args[1]) : kDefaultPieceSize;
    const fs::path pieces_dir = args.size() > 2 ? args[2] : "pieces";

    if (!fs::is_regular_file(input)) {
        throw std::runtime_error("input is not a regular file: " + input.string());
    }
    const std::uint64_t file_size = fs::file_size(input);

    std::ifstream in(input, std::ios::binary);
    if (!in) throw std::runtime_error("cannot open input file: " + input.string());

    fs::create_directories(pieces_dir);
    clear_old_pieces(pieces_dir);

    Metadata md;
    md.filename = input.filename().string();
    md.file_size = file_size;
    md.piece_size = piece_size;
    md.pieces = compute_pieces(file_size, piece_size);  // index, offset, size, file name

    // Only ONE piece is held in memory at a time.
    std::vector<char> buffer(static_cast<std::size_t>(std::min(piece_size, file_size)));
    Sha256 file_hash;

    for (PieceInfo& p : md.pieces) {
        in.seekg(static_cast<std::streamoff>(p.offset));
        in.read(buffer.data(), static_cast<std::streamsize>(p.size));
        if (in.gcount() != static_cast<std::streamsize>(p.size)) {
            throw std::runtime_error("short read on piece " + std::to_string(p.index));
        }

        Sha256 piece_hash;
        piece_hash.update(buffer.data(), static_cast<std::size_t>(p.size));
        p.sha256 = piece_hash.finalize_hex();
        file_hash.update(buffer.data(), static_cast<std::size_t>(p.size));

        const fs::path piece_path = pieces_dir / p.file;
        std::ofstream out(piece_path, std::ios::binary | std::ios::trunc);
        if (!out) throw std::runtime_error("cannot create " + piece_path.string());
        out.write(buffer.data(), static_cast<std::streamsize>(p.size));
        out.close();  // flush + detect write errors
        if (!out) throw std::runtime_error("write failed for " + piece_path.string());
    }
    md.file_sha256 = file_hash.finalize_hex();

    const fs::path metadata_path = pieces_dir / kMetadataName;
    write_metadata(metadata_path, md);

    std::cout << "File       : " << input.string() << " (" << file_size << " bytes)\n"
              << "Piece size : " << piece_size << " bytes\n"
              << "Pieces     : " << md.pieces.size() << '\n'
              << "SHA-256    : " << md.file_sha256 << '\n'
              << "Metadata   : " << metadata_path.string() << "\n\n";

    std::cout << std::left << std::setw(7) << "Index" << std::setw(13) << "Offset" << std::setw(11)
              << "Size" << std::setw(20) << "SHA-256 (first 16)" << "File\n";
    for (const PieceInfo& p : md.pieces) {
        std::cout << std::left << std::setw(7) << p.index << std::setw(13) << p.offset
                  << std::setw(11) << p.size << std::setw(20) << p.sha256.substr(0, 16) << p.file
                  << '\n';
    }
    if (md.pieces.empty()) std::cout << "(empty file: no pieces)\n";
    return 0;
}

// ---------------------------------------------------------------------------
// Command: reconstruct  (Step 4)
// ---------------------------------------------------------------------------

int cmd_reconstruct(const std::vector<std::string>& args) {
    if (args.size() > 2) throw std::invalid_argument("reconstruct: too many arguments");
    const fs::path pieces_dir = args.size() > 0 ? args[0] : "pieces";
    const fs::path out_dir = args.size() > 1 ? args[1] : "reconstructed";

    const Metadata md = load_metadata(pieces_dir / kMetadataName);

    // 1) Missing-piece detection: report every missing / wrong-sized piece up front.
    std::vector<std::string> problems;
    for (const PieceInfo& p : md.pieces) {
        const fs::path f = pieces_dir / p.file;
        std::error_code ec;
        if (!fs::is_regular_file(f, ec)) {
            problems.push_back("piece " + std::to_string(p.index) + " is missing (" + f.string() +
                               ")");
            continue;
        }
        const std::uintmax_t actual = fs::file_size(f, ec);
        if (ec || actual != p.size) {
            problems.push_back("piece " + std::to_string(p.index) + " has the wrong size (expected " +
                               std::to_string(p.size) + " bytes)");
        }
    }
    if (!problems.empty()) {
        for (const std::string& msg : problems) std::cerr << "  - " << msg << '\n';
        throw std::runtime_error(std::to_string(problems.size()) +
                                 " piece(s) missing or invalid; nothing was written");
    }

    // 2) Assemble in index order into <name>.part, verifying each piece's SHA-256.
    //    The .part file is only renamed to the final name if everything checks out.
    fs::create_directories(out_dir);
    const fs::path out_path = out_dir / md.filename;
    const fs::path part_path = out_path.string() + ".part";

    std::ofstream out(part_path, std::ios::binary | std::ios::trunc);
    if (!out) throw std::runtime_error("cannot create " + part_path.string());

    std::uint64_t total_bytes = 0;
    try {
        Sha256 file_hash;
        std::vector<char> chunk(64 * 1024);  // memory use does not depend on piece size

        for (const PieceInfo& p : md.pieces) {
            const fs::path piece_path = pieces_dir / p.file;
            std::ifstream in(piece_path, std::ios::binary);
            if (!in) throw std::runtime_error("cannot open " + piece_path.string());

            Sha256 piece_hash;
            std::uint64_t got = 0;
            while (in) {
                in.read(chunk.data(), static_cast<std::streamsize>(chunk.size()));
                const std::streamsize n = in.gcount();
                if (n <= 0) break;
                const auto len = static_cast<std::size_t>(n);
                piece_hash.update(chunk.data(), len);
                file_hash.update(chunk.data(), len);
                out.write(chunk.data(), n);
                got += len;
            }
            if (in.bad()) throw std::runtime_error("read error on " + piece_path.string());
            if (got != p.size) {
                throw std::runtime_error("piece " + std::to_string(p.index) + " changed size");
            }

            const std::string actual = piece_hash.finalize_hex();
            if (actual != p.sha256) {
                throw std::runtime_error("piece " + std::to_string(p.index) +
                                         " is corrupted (SHA-256 mismatch)\n  expected " + p.sha256 +
                                         "\n  actual   " + actual);
            }
            total_bytes += got;
            std::cout << "OK  " << p.file << "  (" << got << " bytes)\n";
        }

        out.close();
        if (!out) throw std::runtime_error("failed finalizing " + part_path.string());

        if (total_bytes != md.file_size) throw std::runtime_error("total size mismatch");
        if (file_hash.finalize_hex() != md.file_sha256) {
            throw std::runtime_error("whole-file SHA-256 mismatch");
        }
    } catch (...) {
        out.close();
        std::error_code ec;
        fs::remove(part_path, ec);  // never leave a half-built file behind
        throw;
    }

    std::error_code ec;
    fs::remove(out_path, ec);
    fs::rename(part_path, out_path);

    std::cout << "\nReconstruction complete!\n"
              << "Pieces processed : " << md.pieces.size() << '\n'
              << "Bytes written    : " << total_bytes << '\n'
              << "SHA-256          : " << md.file_sha256 << '\n'
              << "Output           : " << out_path.string() << '\n';
    return 0;
}

// ---------------------------------------------------------------------------
// Command: verify  (Step 5)
// ---------------------------------------------------------------------------

int cmd_verify(const std::vector<std::string>& args) {
    if (args.size() != 2) throw std::invalid_argument("verify: expected exactly two files");

    const std::uintmax_t size_a = fs::file_size(args[0]);
    const std::uintmax_t size_b = fs::file_size(args[1]);
    const std::string hash_a = sha256_of_file(args[0]);
    const std::string hash_b = sha256_of_file(args[1]);

    std::cout << args[0] << "\n  " << size_a << " bytes  sha256 " << hash_a << '\n'
              << args[1] << "\n  " << size_b << " bytes  sha256 " << hash_b << '\n';

    const bool same = size_a == size_b && hash_a == hash_b;
    std::cout << (same ? "\nRESULT: IDENTICAL\n" : "\nRESULT: DIFFERENT\n");
    return same ? 0 : 1;
}

// ---------------------------------------------------------------------------

void print_usage(const std::string& prog) {
    std::cerr << "Usage:\n"
              << "  " << prog << " split       [input_file=shared/example.bin] [piece_size=1048576] "
              << "[pieces_dir=pieces]\n"
              << "  " << prog << " reconstruct [pieces_dir=pieces] [output_dir=reconstructed]\n"
              << "  " << prog << " verify      <file_a> <file_b>\n";
}

int main(int argc, char* argv[]) {
    const std::string prog = argc > 0 ? argv[0] : "lab9";
    try {
        if (argc < 2) throw std::invalid_argument("missing command");
        const std::string command = argv[1];
        const std::vector<std::string> args(argv + 2, argv + argc);

        if (command == "split") return cmd_split(args);
        if (command == "reconstruct") return cmd_reconstruct(args);
        if (command == "verify") return cmd_verify(args);
        throw std::invalid_argument("unknown command: " + command);
    } catch (const std::invalid_argument& e) {
        std::cerr << "Error: " << e.what() << "\n\n";
        print_usage(prog);
        return 2;
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << '\n';
        return 1;
    }
}