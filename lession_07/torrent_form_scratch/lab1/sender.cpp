
#include <iostream>
#include <string>
#include <cerrno>
#include <cstring>

#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>

int main() {
    // 1. Create a TCP socket
    int sock_fd = socket(AF_INET, SOCK_STREAM, 0);

    if (sock_fd == -1) {
        perror("socket");
        return 1;
    }

    // 2. Configure the receiver's address
    sockaddr_in server_addr{};
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(5000);

    if (inet_pton(AF_INET, "127.0.0.1",
                  &server_addr.sin_addr) != 1) {
        std::cerr << "Invalid IPv4 address\n";
        close(sock_fd);
        return 1;
    }

    // 3. Connect to the receiver
    if (connect(sock_fd,
                reinterpret_cast<sockaddr*>(&server_addr),
                sizeof(server_addr)) == -1) {
        perror("connect");
        close(sock_fd);
        return 1;
    }

    std::cout << "Connected to receiver!\n";

    // 4. Send a message
    std::string message = "Hello from the C++ sender!";

    ssize_t bytes_sent = send(
        sock_fd, message.data(), message.size(), 0
    );

    if (bytes_sent == -1) {
        perror("send");
        close(sock_fd);
        return 1;
    }

    std::cout << "Sent " << bytes_sent << " bytes\n";

    // 5. Close the socket
    close(sock_fd);

    return 0;
}
