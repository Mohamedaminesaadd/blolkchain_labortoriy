
#include <iostream>
#include <thread>
#include <string>

#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>

void handle_client(int client_socket) {
    char buffer[1024];

    int bytes_received = recv(
        client_socket,
        buffer,
        sizeof(buffer) - 1,
        0
    );

    if (bytes_received > 0) {
        buffer[bytes_received] = '\0';

        std::cout << "Received: "
                  << buffer << std::endl;

        std::string response = "Message received";

        send(
            client_socket,
            response.c_str(),
            response.size(),
            0
        );
    }

    close(client_socket);
}

int main() {
    int server_socket = socket(
        AF_INET,
        SOCK_STREAM,
        0
    );

    if (server_socket < 0) {
        std::cerr << "Socket creation failed\n";
        return 1;
    }

    sockaddr_in server_address{};
    server_address.sin_family = AF_INET;
    server_address.sin_addr.s_addr = INADDR_ANY;
    server_address.sin_port = htons(5000);

    if (bind(
            server_socket,
            (sockaddr*)&server_address,
            sizeof(server_address)
        ) < 0) {
        std::cerr << "Bind failed\n";
        close(server_socket);
        return 1;
    }

    if (listen(server_socket, 10) < 0) {
        std::cerr << "Listen failed\n";
        close(server_socket);
        return 1;
    }

    std::cout << "Server listening on port 5000\n";

    while (true) {
        int client_socket = accept(
            server_socket,
            nullptr,
            nullptr
        );

        if (client_socket < 0) {
            continue;
        }

        std::cout << "New client connected\n";

        std::thread client_thread(
            handle_client,
            client_socket
        );

        client_thread.detach();
    }

    close(server_socket);
    return 0;
}
