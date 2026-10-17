
#include <iostream>
#include <string>
#include <ctime>
#include <cstring>

#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>

std::string process_request(const std::string& request) {
    if (request == "PING") {
        return "PONG";
    }

    if (request == "TIME") {
        std::time_t now = std::time(nullptr);
        std::string result = std::ctime(&now);

        // ctime() normally adds a newline.
        if (!result.empty() && result.back() == '\n') {
            result.pop_back();
        }

        return result;
    }

    if (request == "QUIT") {
        return "BYE";
    }

    return "ERROR: Unknown command";
}

int main() {
    // 1. Create TCP socket
    int server_fd = socket(AF_INET, SOCK_STREAM, 0);

    if (server_fd == -1) {
        perror("socket");
        return 1;
    }

    // Allow quick reuse of the local port after restarting.
    int opt = 1;
    if (setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR,
                   &opt, sizeof(opt)) == -1) {
        perror("setsockopt");
        close(server_fd);
        return 1;
    }

    // 2. Configure the address
    sockaddr_in address{};
    address.sin_family = AF_INET;
    address.sin_port = htons(5000);
    address.sin_addr.s_addr = htonl(INADDR_LOOPBACK);

    // 3. Bind
    if (bind(server_fd,
             reinterpret_cast<sockaddr*>(&address),
             sizeof(address)) == -1) {
        perror("bind");
        close(server_fd);
        return 1;
    }

    // 4. Listen
    if (listen(server_fd, 5) == -1) {
        perror("listen");
        close(server_fd);
        return 1;
    }

    std::cout << "Server listening on 127.0.0.1:5000\n";

    // 5. Accept one client
    int client_fd = accept(server_fd, nullptr, nullptr);

    if (client_fd == -1) {
        perror("accept");
        close(server_fd);
        return 1;
    }

    std::cout << "Client connected\n";

    // 6. Process requests until QUIT or disconnection
    while (true) {
        char buffer[1024];

        ssize_t n = recv(client_fd, buffer, sizeof(buffer), 0);

        if (n == 0) {
            std::cout << "Client disconnected\n";
            break;
        }

        if (n < 0) {
            perror("recv");
            break;
        }

        std::string request(buffer, n);

        std::cout << "Request: " << request << '\n';

        std::string response = process_request(request);

        // This introductory protocol sends one response per request.
        // Lab 6 will introduce explicit message framing.
        ssize_t sent = send(
            client_fd, response.data(), response.size(), MSG_NOSIGNAL
        );

        if (sent == -1) {
            perror("send");
            break;
        }

        if (request == "QUIT") {
            break;
        }
    }

    // 7. Close resources
    close(client_fd);
    close(server_fd);

    std::cout << "Server stopped\n";
    return 0;
}
