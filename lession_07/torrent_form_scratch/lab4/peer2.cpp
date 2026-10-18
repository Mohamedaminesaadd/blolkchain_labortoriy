
#include <iostream>
#include <string>
#include <vector>
#include <unordered_set>
#include <thread>
#include <mutex>
#include <atomic>
#include <algorithm>
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
    std::atomic<bool> running{false};
    std::thread listener_thread;

    // Each peer maintains its own message history.
    std::unordered_set<std::string> seen_messages;
    std::mutex seen_mutex;

    // Worker threads handle incoming connections.
    std::vector<std::thread> workers;
    std::mutex workers_mutex;

    std::mutex output_mutex;

    std::string extract_id(const std::string& message) {
        size_t pos = message.find('|');

        if (pos == std::string::npos || pos == 0) {
            return "";
        }

        return message.substr(0, pos);
    }

    bool valid_message(const std::string& message) {
        size_t first = message.find('|');

        if (first == std::string::npos || first == 0) {
            return false;
        }

        size_t second = message.find('|', first + 1);

        return second != std::string::npos &&
               second != first + 1;
    }

    // Read until newline, the message delimiter.
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

    bool send_all(int sock, const std::string& data) {
        size_t sent = 0;

        while (sent < data.size()) {
            ssize_t n = send(
                sock,
                data.data() + sent,
                data.size() - sent,
                MSG_NOSIGNAL
            );

            if (n <= 0) {
                return false;
            }

            sent += static_cast<size_t>(n);
        }

        return true;
    }

    void send_to_peer(int neighbor_port,
                      const std::string& message) {
        int sock = socket(AF_INET, SOCK_STREAM, 0);

        if (sock < 0) {
            return;
        }

        sockaddr_in addr{};
        addr.sin_family = AF_INET;
        addr.sin_port = htons(neighbor_port);
        inet_pton(AF_INET, "127.0.0.1", &addr.sin_addr);

        if (connect(sock, (sockaddr*)&addr, sizeof(addr)) == 0) {
            send_all(sock, message + "\n");
        } else {
            std::lock_guard<std::mutex> lock(output_mutex);

            std::cout << "[Peer " << port
                      << "] Cannot connect to "
                      << neighbor_port << "\n";
        }

        close(sock);
    }

    void broadcast_message(const std::string& message) {
        for (int neighbor_port : neighbors) {
            if (neighbor_port != port) {
                send_to_peer(neighbor_port, message);
            }
        }
    }

    // This method runs in a worker thread.
    void handle_client(int client) {
        std::string message = receive_message(client);
        close(client);

        if (message.empty() || !valid_message(message)) {
            return;
        }

        std::string id = extract_id(message);
        bool is_new;

        {
            std::lock_guard<std::mutex> lock(seen_mutex);
            is_new = seen_messages.insert(id).second;
        }

        if (!is_new) {
            std::lock_guard<std::mutex> lock(output_mutex);

            std::cout << "[Peer " << port
                      << "] Duplicate ignored: "
                      << id << "\n";
            return;
        }

        {
            std::lock_guard<std::mutex> lock(output_mutex);

            std::cout << "[Peer " << port
                      << "] Received: "
                      << message << "\n";
        }

        // Forward only new messages.
        broadcast_message(message);
    }

    // Listener keeps accepting while workers process clients.
    void listen_for_peers() {
        while (running) {
            int client = accept(server_socket, nullptr, nullptr);

            if (client < 0) {
                if (!running) {
                    break;
                }

                continue;
            }

            std::lock_guard<std::mutex> lock(workers_mutex);

            workers.emplace_back(
                &Peer::handle_client, this, client
            );
        }
    }

public:
    Peer(int peer_port, const std::vector<int>& peer_neighbors)
        : port(peer_port), neighbors(peer_neighbors) {}

    Peer(const Peer&) = delete;
    Peer& operator=(const Peer&) = delete;

    ~Peer() {
        stop();
    }

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

        if (bind(server_socket, (sockaddr*)&addr,
                 sizeof(addr)) < 0) {
            std::cerr << "Bind failed on port "
                      << port << "\n";
            close(server_socket);
            server_socket = -1;
            return false;
        }

        if (listen(server_socket, 20) < 0) {
            std::cerr << "Listen failed\n";
            close(server_socket);
            server_socket = -1;
            return false;
        }

        running = true;
        listener_thread =
            std::thread(&Peer::listen_for_peers, this);

        std::cout << "[Peer " << port
                  << "] Listening\n";

        return true;
    }

    void send_message(const std::string& message) {
        if (!valid_message(message)) {
            std::cout << "Format: ID|TYPE|PAYLOAD\n";
            return;
        }

        std::string id = extract_id(message);
        bool is_new;

        {
            std::lock_guard<std::mutex> lock(seen_mutex);
            is_new = seen_messages.insert(id).second;
        }

        if (!is_new) {
            std::cout << "Message ID already used: "
                      << id << "\n";
            return;
        }

        {
            std::lock_guard<std::mutex> lock(output_mutex);

            std::cout << "[Peer " << port
                      << "] Sending: "
                      << message << "\n";
        }

        broadcast_message(message);
    }

    void stop() {
        if (!running.exchange(false)) {
            return;
        }

        // Interrupt accept() and close the listening socket.
        shutdown(server_socket, SHUT_RDWR);
        close(server_socket);
        server_socket = -1;

        if (listener_thread.joinable()) {
            listener_thread.join();
        }

        // All workers are joinable and senders close their sockets.
        std::lock_guard<std::mutex> lock(workers_mutex);

        for (auto& worker : workers) {
            if (worker.joinable()) {
                worker.join();
            }
        }

        workers.clear();

        std::cout << "[Peer " << port << "] Stopped\n";
    }
};

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cout
            << "Usage: ./step4_p2p PORT [NEIGHBOR_PORT...]\n";
        return 1;
    }

    int port = std::atoi(argv[1]);
    std::vector<int> neighbors;

    for (int i = 2; i < argc; ++i) {
        neighbors.push_back(std::atoi(argv[i]));
    }

    Peer peer(port, neighbors);

    if (!peer.start()) {
        return 1;
    }

    std::cout << "Message format: ID|TYPE|PAYLOAD\n";
    std::cout << "Example: a81f29|PING|Hello network\n";
    std::cout << "Type QUIT to stop this peer.\n";

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
