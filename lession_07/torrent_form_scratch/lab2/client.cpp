
#include <iostream>
#include <string>

#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>

int main() {
    // 1. Create TCP socket
    int sock_fd = socket(AF_INET, SOCK_STREAM, 0);

    if (sock_fd == -1) {
        perror("socket");
        return 1;
    }

    // 2. Configure server address
    sockaddr_in server{};
    server.sin_family = AF_INET;
    server.sin_port = htons(5000);

    if (inet_pton(AF_INET, "127.0.0.1",
                  &server.sin_addr) != 1) {
        std::cerr << "Invalid server address\n";
        close(sock_fd);
        return 1;
    }

    // 3. Connect
    if (connect(sock_fd,
                reinterpret_cast<sockaddr*>(&server),
                sizeof(server)) == -1) {
        perror("connect");
        close(sock_fd);
        return 1;
    }

    std::cout << "Connected to server\n";
    std::cout << "Commands: PING, TIME, QUIT\n";

    std::string request;

    while (true) {
        std::cout << "\nEnter command: ";

        if (!std::getline(std::cin, request)) {
            break;
        }

        // 4. Send request
        ssize_t sent = send(
            sock_fd, request.data(), request.size(), MSG_NOSIGNAL
        );

        if (sent == -1) {
            perror("send");
            break;
        }

        // 5. Receive response
        char buffer[1024];

        ssize_t n = recv(sock_fd, buffer, sizeof(buffer), 0);

        if (n <= 0) {
            if (n < 0) {
                perror("recv");
            } else {
                std::cout << "Server disconnected\n";
            }
            break;
        }

        std::string response(buffer, n);
        std::cout << "Server: " << response << '\n';

        if (request == "QUIT") {
            break;
        }
    }

    // 6. Close connection
    close(sock_fd);

    return 0;
}
