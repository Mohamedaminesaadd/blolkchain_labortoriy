
#include <iostream>
#include <string>

#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>

using namespace std;

int main() {
    // 1. Create the listening socket
    int server_fd = socket(AF_INET, SOCK_STREAM, 0);

    if (server_fd == -1) {
        perror("socket");
        return 1;
    }

    // 2. Configure the server address
    sockaddr_in address{};
    address.sin_family = AF_INET;
    address.sin_port = htons(5000);
    address.sin_addr.s_addr = htonl(INADDR_LOOPBACK);

    // 3. Bind the socket to port 5000
    if (bind(server_fd,
             reinterpret_cast<sockaddr*>(&address),
             sizeof(address)) == -1) {
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

    cout << "Peer B listening on port 5000...\n";

    // 5. Accept one connection
    int peer_fd = accept(server_fd, nullptr, nullptr);

    if (peer_fd == -1) {
        perror("accept");
        close(server_fd);
        return 1;
    }

    cout << "Peer A connected!\n";

    // Keep receiving requests until the client disconnects
    // or sends QUIT.
    while (true) {
        char buffer[1024];

        ssize_t n = recv(peer_fd, buffer, sizeof(buffer), 0);

        if (n == 0) {
            cout << "Client disconnected\n";
            break;
        }

        if (n < 0) {
            perror("recv");
            break;
        }

        string request(buffer, static_cast<size_t>(n));

        cout << "Received: " << request << '\n';

        string response;

        if (request == "PING") {
            response = "PONG";
        } else if (request == "QUIT") {
            response = "BYE";
        } else {
            response = "UNKNOWN";
        }

        if (send(peer_fd, response.data(),
                 response.size(), 0) == -1) {
            perror("send");
            break;
        }

        cout << "Sent: " << response << '\n';

        if (request == "QUIT") {
            break;
        }
    }

    close(peer_fd);
    close(server_fd);

    return 0;

}
