# Lab 2 — Client-Server Architecture in C++

In Lab 1, you created a TCP connection and exchanged a message. Now we will build a more structured client-server application in C++.

The objective is to understand how a server manages requests and sends responses — a foundation for your future P2P file-sharing system.

## 1. Lab objectives

By the end of this lab, you will understand:

- The responsibilities of a client and a server.
- The request-response communication pattern.
- How a server processes client requests.
- How to keep a TCP connection open for multiple requests.
- How to separate networking code from application logic.

## 2. Architecture

C++ Client

Sends commands and displays responses

TCP connection

127.0.0.1:5000

C++ Server

Receives commands, executes logic, returns responses

We will implement three commands:

| Client request | Server response                  |
| -------------- | -------------------------------- |
| `PING`         | `PONG`                           |
| `TIME`         | Current server time              |
| `QUIT`         | `BYE`, then close the connection |

This is a simple application protocol built on top of TCP.

## 3. Create the project

```
cd ~/cpp-p2p-lab
mkdir -p lab02
cd lab02
```

The directory will contain:

```
lab02/
├── server.cpp
└── client.cpp
```

## 4. Implement the server

Create `server.cpp`:

```

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

```

### Understand the important part

The server separates the application logic into a function:

```
std::string process_request(const std::string& request)
```

This function does not know anything about TCP sockets. It receives a command and returns a result.

That separation is important: later, your file-sharing application will have functions such as `list_files()`, `request_file()` and `receive_file()`.

A limitation to understand: TCP does not preserve application message boundaries. This example assumes each small request arrives in a single `recv()` call. That is fine for this introductory experiment, but it is not a reliable general-purpose protocol. We will fix that with message framing in Lab 6.

## 5. Implement the client

Create `client.cpp`:

```

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

```

## 6. Compile the programs

```
g++ -std=c++17 -Wall -Wextra server.cpp -o server
g++ -std=c++17 -Wall -Wextra client.cpp -o client
```

## 7. Run the experiment

Open two terminals.

Terminal 1 — Start the server

```
cd ~/cpp-p2p-lab/lab02
./server
```

Expected output:

```
Server listening on 127.0.0.1:5000
```

Terminal 2 — Start the client

```
cd ~/cpp-p2p-lab/lab02
./client
```

Enter these commands one by one:

```
PING
TIME
PING
QUIT
```

The interaction should look similar to this:

```
Connected to server
Commands: PING, TIME, QUIT

Enter command: PING
Server: PONG

Enter command: TIME
Server: Sat Oct 17 14:00:00 2026

Enter command: PING
Server: PONG

Enter command: QUIT
Server: BYE
```

The time shown is illustrative; your server returns its actual system time.

## 8. What changed from Lab 1?

| Lab 1                                | Lab 2                                       |
| ------------------------------------ | ------------------------------------------- |
| One message                          | Multiple requests over one connection       |
| Fixed message                        | Commands interpreted by the server          |
| Basic data exchange                  | Request-response pattern                    |
| Networking and logic mostly together | Application logic separated into a function |

One important detail: this server accepts only one client connection per execution. It processes multiple requests from that client, then stops. We will explore multiple simultaneous clients in Lab 4.

## 9. Practical exercises

Lab 2 checklist

0/5 complete

Add a command

Implement HELP and return a list of supported commands.

Add an error response

Try UNKNOWN and inspect the response.

Change the port

Use port 6000 in both programs.

Inspect TCP

Use ss -tnp to observe the established connection while the client is running.

Separate the application

Move process_request() into a separate protocol.cpp and protocol.hpp file.

Next: Lab 3 — Peer-to-Peer Communication. We will make two programs act as peers rather than treating one program as a permanently dedicated server. That is where we begin moving toward your actual P2P file-sharing system.s