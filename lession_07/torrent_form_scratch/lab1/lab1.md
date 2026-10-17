# Lab 1 — TCP Socket Communication in C++

We will build the first component of your C++ P2P File-Sharing System step by step. In this lab, you will learn how two programs communicate over a network using TCP sockets on Ubuntu Linux.

## 1. Lab objective

Program A — Sender

Creates a TCP connection and sends a message.

TCP socket over localhost

Program B — Receiver

Listens on a TCP port and receives the message.

By the end, you will understand:

- What a TCP socket is.
- How IP addresses and ports identify network endpoints.
- How a TCP connection is established.
- How to send and receive bytes in C++.
- How to compile and run networking programs on Linux.

## 2. Prepare your environment

Open your Ubuntu terminal and install the C++ compiler and basic tools:

```
sudo apt update
sudo apt install build-essential
```

Create the lab directory:

```
mkdir -p ~/cpp-p2p-lab/lab01
cd ~/cpp-p2p-lab/lab01
```

Check the compiler:

```
g++ --version
```

We will use the Linux Berkeley sockets API with C++. You do not need Boost.Asio yet; that comes in Lab 5.

## 3. Understand the architecture

TCP communication follows this sequence:

Receiver

socket() → bind() → listen()

TCP connection

Sender: connect() · Receiver: accept()

Exchange data

send() / recv()

Close the connection

close()

Important: TCP is a transport protocol, not a programming language or a socket API. The socket API is how your C++ program uses the operating system's networking facilities.

## 4. Create the receiver

Create `receiver.cpp`:

```

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

```

### What the receiver does

| Function   | Purpose                                         |
| ---------- | ----------------------------------------------- |
| `socket()` | Creates a TCP socket                            |
| `bind()`   | Assigns the local IP address and port           |
| `listen()` | Marks the socket as ready to accept connections |
| `accept()` | Accepts a client connection                     |
| `recv()`   | Receives bytes                                  |
| `close()`  | Releases a socket descriptor                    |

`AF_INET` means IPv4, `SOCK_STREAM` selects a TCP-style stream socket, and `htons(5000)` converts the port to network byte order.

## 5. Create the sender

Create `sender.cpp`:

```

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

```

For this introductory lab, the sender sends one short message. Later, we will improve the code to handle partial sends, repeated messages, and multiple clients.

## 6. Compile both programs

From `~/cpp-p2p-lab/lab01`:

```
g++ -std=c++17 -Wall -Wextra receiver.cpp -o receiver
g++ -std=c++17 -Wall -Wextra sender.cpp -o sender
```

If compilation succeeds, you should have two executables:

```
lab01/
├── receiver.cpp
├── receiver
├── sender.cpp
└── sender
```

## 7. Run the experiment

Open two terminal windows.

Terminal 1 — Receiver

```
cd ~/cpp-p2p-lab/lab01
./receiver
```

Expected output:

```
Receiver listening on 127.0.0.1:5000
```

Terminal 2 — Sender

```
cd ~/cpp-p2p-lab/lab01
./sender
```

Expected output:

```
Connected to receiver!
Sent 27 bytes
```

The receiver should print:

```
Receiver listening on 127.0.0.1:5000
Sender connected!
Received: Hello from the C++ sender!
```

The message is 27 bytes long.

## 8. Observe the network connection

While the receiver is waiting for a connection, open a third terminal:

```
ss -ltnp | grep ':5000'
```

This should show a listening TCP socket on port 5000.

You can also inspect TCP traffic with `tcpdump` if it is installed:

```
sudo tcpdump -i lo -nn 'tcp port 5000'
```

The `lo` interface is the loopback interface, used for traffic between programs on the same machine.

## 9. Understand what you built

You have not built a P2P system yet. You have built the TCP communication foundation that will support it.

- Your receiver waits for an incoming connection.
- Your sender initiates the connection.
- The operating system establishes TCP and handles reliable, ordered byte delivery.
- Your application decides what those bytes mean.

One important limitation: TCP is a byte stream, not a message protocol. A single `send()` does not guarantee that the other side receives the entire message in one `recv()`. We will address framing and binary message encoding in Lab 6.

## 10. Lab 1 exercises

Try these yourself before moving on.

### Practical checklist

0 of 5

Change the port

Use port 6000 in both programs and test again.

Change the message

Send your own text and verify the receiver prints it.

Test a failed connection

Start the sender without starting the receiver. Observe the error.

Send a longer message

Try a message longer than 1024 bytes and investigate why the current receiver is insufficient.

Inspect the listening socket

Run ss -ltnp while the receiver is waiting.

Your milestone: both C++ programs compile, connect through TCP, and exchange a message successfully.

When you finish, tell me what output you got or share any error. Then we will move to Lab 2 — Client-Server Architecture, where we will turn this simple connection into a more structured network application.