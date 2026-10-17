
#include <iostream>
#include <string>
#include <vector>
#include <unordered_set>
#include <thread>
#include <mutex>
#include <atomic>
#include <cstdlib>

#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <netinet/in.h>

class Peer {
private:
    int port;
    std::vector<int> neighbors;

    int server_socket = -1;
    std::thread listener_thread;
    std::atomic<bool> running{false};

    std::unordered_set<std::string> seen_messages;
    std::mutex seen_mutex;

    // Extract ID from ID|TYPE|PAYLOAD.
    std::string extract_message_id(const std::string& message) {
        size_t separator = message.find('|');

        if (separator == std::string::npos || separator == 0) {
            return "";
        }

        return message.substr(0, separator);
    }

    // Validate the basic message format.
    bool valid_message(const std::string& message) {
        size_t first = message.find('|');

        if (first == std::string::npos || first == 0) {
            return false;
        }

        size_t second = message.find('|', first + 1);

        if (second == std::string::npos || second == first + 1) {
            return false;
        }

        return true;
    }

    // Read one newline-terminated message.
    std::string receive_message(int client) {
        std::string message;
        char c;

        while (message.size() < 4096) {
            ssize_t n = recv(client, &c, 1, 0);

            if (n <= 0) {
                return "";
            }

            if (c == '\n') {
                return message;
            }

            message += c;
        }

        return "";
    }

    // Send all bytes, handling partial sends.
    bool send_all(int sock, const std::string& data) {
        size_t sent = 0;

        while (sent < data.size()) {
            ssize_t n = send(
                sock,
                data.data() + sent,
                data.size() - sent,
                0
            );

            if (n <= 0) {
                return false;
            }

            sent += static_cast<size_t>(n);
        }

        return true;
    }

    // Connect to one neighbor and send a message.
    void send_to_peer(int peer_port, const std::string& message) {
        int sock = socket(AF_INET, SOCK_STREAM, 0);

        if (sock < 0) {
            std::cerr << "Socket creation failed\n";
            return;
        }

        sockaddr_in addr{};
        addr.sin_family = AF_INET;
        addr.sin_port = htons(peer_port);
        inet_pton(AF_INET, "127.0.0.1", &addr.sin_addr);

        if (connect(sock, (sockaddr*)&addr, sizeof(addr)) == 0) {
            send_all(sock, message + "\n");
        } else {
            std::cerr << "Could not connect to port "
                      << peer_port << "\n";
        }

        close(sock);
    }

    // Forward to every configured neighbor.
    void broadcast_message(const std::string& message) {
        for (int peer_port : neighbors) {
            send_to_peer(peer_port, message);
        }
    }

    // Accept and process incoming connections.
    void listen_for_peers() {
        while (running) {
            int client = accept(server_socket, nullptr, nullptr);

            if (client < 0) {
                if (!running) {
                    break;
                }
                continue;
            }

            std::string message = receive_message(client);
            close(client);

            if (message.empty() || !valid_message(message)) {
                std::cout << "Invalid or empty message\n";
                continue;
            }

            std::string id = extract_message_id(message);
            bool is_new;

            {
                std::lock_guard<std::mutex> lock(seen_mutex);
                is_new = seen_messages.insert(id).second;
            }

            if (!is_new) {
                std::cout << "[Port " << port
                          << "] Duplicate ignored: " << id << "\n";
                continue;
            }

            std::cout << "[Port " << port
                      << "] Received: " << message << "\n";

            broadcast_message(message);
        }
    }

public:
    // Constructor: configure this peer.
    Peer(int peer_port, const std::vector<int>& peer_neighbors)
        : port(peer_port), neighbors(peer_neighbors) {}

    // Avoid accidentally copying a running network node.
    Peer(const Peer&) = delete;
    Peer& operator=(const Peer&) = delete;

    // Destructor: ensure resources are released.
    ~Peer() {
        stop();
    }

    // Start the TCP listener.
    bool start() {
        server_socket = socket(AF_INET, SOCK_STREAM, 0);

        if (server_socket < 0) {
            std::cerr << "Socket creation failed\n";
            return false;
        }

        int reuse = 1;
        setsockopt(
            server_socket, SOL_SOCKET, SO_REUSEADDR,
            &reuse, sizeof(reuse)
        );

        sockaddr_in addr{};
        addr.sin_family = AF_INET;
        addr.sin_addr.s_addr = INADDR_ANY;
        addr.sin_port = htons(port);

        if (bind(server_socket, (sockaddr*)&addr, sizeof(addr)) < 0) {
            std::cerr << "Bind failed on port " << port << "\n";
            close(server_socket);
            server_socket = -1;
            return false;
        }

        if (listen(server_socket, 10) < 0) {
            std::cerr << "Listen failed\n";
            close(server_socket);
            server_socket = -1;
            return false;
        }

        running = true;
        listener_thread = std::thread(&Peer::listen_for_peers, this);

        std::cout << "Peer listening on port " << port << "\n";
        return true;
    }

    // Stop the listener and release its resources.
    void stop() {
        if (!running.exchange(false)) {
            return;
        }

        shutdown(server_socket, SHUT_RDWR);
        close(server_socket);
        server_socket = -1;

        if (listener_thread.joinable()) {
            listener_thread.join();
        }
    }

    // Send a locally created message.
    void send_message(const std::string& message) {
        if (!valid_message(message)) {
            std::cout << "Use ID|TYPE|PAYLOAD\n";
            return;
        }

        std::string id = extract_message_id(message);
        bool is_new;

        {
            std::lock_guard<std::mutex> lock(seen_mutex);
            is_new = seen_messages.insert(id).second;
        }

        if (!is_new) {
            std::cout << "You already used message ID: "
                      << id << "\n";
            return;
        }

        std::cout << "[Port " << port
                  << "] Sending: " << message << "\n";

        broadcast_message(message);
    }
};

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cout
            << "Usage: ./step11 PORT [NEIGHBOR_PORT...]\n";
        return 1;
    }

    int port = std::atoi(argv[1]);
    std::vector<int> neighbors;

    for (int i = 2; i < argc; i++) {
        neighbors.push_back(std::atoi(argv[i]));
    }

    Peer peer(port, neighbors);

    if (!peer.start()) {
        return 1;
    }

    std::cout
        << "Enter ID|TYPE|PAYLOAD\n"
        << "Example: a81f29|PING|Hello network\n"
        << "Type QUIT to exit.\n";

    std::string message;

    while (std::getline(std::cin, message)) {
        if (message == "QUIT") {
            break;
        }

        peer.send_message(message);
    }

    peer.stop();
    return 0;
}
