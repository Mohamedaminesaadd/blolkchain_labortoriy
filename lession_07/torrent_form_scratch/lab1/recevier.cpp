
#include <iostream>
#include <cstring>
#include <string>

#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>

int main() {
    // 1. Create a TCP socket
    int server_fd = socket(AF_INET, SOCK_STREAM, 0);

    if (server_fd == -1) {
        perror("socket");
        return 1;
    }

    // 2. Configure the server address
    sockaddr_in server_addr{};
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(5000);
    server_addr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);

    // 3. Bind the socket to 127.0.0.1:5000
    if (bind(server_fd,
             reinterpret_cast<sockaddr*>(&server_addr),
             sizeof(server_addr)) == -1) {
        perror("bind");
        close(server_fd);
        return 1;
    }

    // 4. Listen for incoming connections
    if (listen(server_fd, 5) == -1) {
        perror("listen");
        close(server_fd);
        return 1;
    }

    std::cout << "Receiver listening on 127.0.0.1:5000\n";

    // 5. Accept one incoming connection
    int client_fd = accept(server_fd, nullptr, nullptr);

    if (client_fd == -1) {
        perror("accept");
        close(server_fd);
        return 1;
    }

    std::cout << "Sender connected!\n";

    // 6. Receive data
    char buffer[1024];

    ssize_t bytes_received = recv(
        client_fd, buffer, sizeof(buffer), 0
    );

    if (bytes_received > 0) {
        std::string message(buffer, bytes_received);
        std::cout << "Received: " << message << '\n';
    } else if (bytes_received == 0) {
        std::cout << "Sender disconnected.\n";
    } else {
        perror("recv");
    }

    // 7. Close sockets
    close(client_fd);
    close(server_fd);

    return 0;
}
