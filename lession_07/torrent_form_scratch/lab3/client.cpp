
#include <iostream>
#include <string>

#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>

using namespace std;

int main() {
    // 1. Create a socket
    int sock_fd = socket(AF_INET, SOCK_STREAM, 0);

    if (sock_fd == -1) {
        perror("socket");
        return 1;
    }

    // 2. Configure Peer B's address
    sockaddr_in server{};
    server.sin_family = AF_INET;
    server.sin_port = htons(5000);
    server.sin_addr.s_addr = htonl(INADDR_LOOPBACK);

    // 3. Connect to Peer B
    if (connect(sock_fd,
                reinterpret_cast<sockaddr*>(&server),
                sizeof(server)) == -1) {
        perror("connect");
        close(sock_fd);
        return 1;
    }

    cout << "Connected to Peer B\n";

    
    string request;

    while (true) {
        cout << "Enter command (PING or QUIT): ";

        if (!getline(cin, request)) {
            break;
        }

        // Send request
        if (send(sock_fd, request.data(),
                 request.size(), 0) == -1) {
            perror("send");
            break;
        }

        // Receive response
        char buffer[1024];

        ssize_t n = recv(sock_fd, buffer, sizeof(buffer), 0);

        if (n <= 0) {
            cout << "Connection closed\n";
            break;
        }

        string response(buffer, static_cast<size_t>(n));

        cout << "Received: " << response << '\n';

        if (request == "QUIT") {
            break;
        }
    }

    close(sock_fd);
    return 0;

}
