# What is Boost.Asio?

Boost.Asio is a C++ library for network programming and asynchronous input/output (I/O). It helps you build TCP servers, TCP clients, UDP applications, and other programs that communicate over networks without having to manage every low-level operating-system detail yourself.

In your C++ P2P file-sharing project, Boost.Asio can help you manage many connected peers without creating a separate thread for every connection.

## 1. First, understand the problem

Imagine your P2P node is a TCP server that receives messages from Peer A, Peer B, and Peer C.

With a simple blocking socket, your program might wait here:

```
int client = accept(server_socket, nullptr, nullptr);
```

The program waits until a client connects. Similar blocking operations can make it difficult to manage many clients efficiently.

Boost.Asio provides asynchronous operations that let you register an operation and continue doing other work while the network operation is pending.

For example:

```
acceptor.async_accept(
    [](boost::system::error_code error,
       boost::asio::ip::tcp::socket socket) {
        if (!error) {
            std::cout << "Client connected\n";
        }
    }
);
```

Instead of waiting at the call site for a connection, the program registers a callback. When the operation completes, Boost.Asio invokes that callback.

## 2. How Boost.Asio works

### Your C++ P2P application

Connect to peers • Send messages • Receive data

### Boost.Asio

TCP sockets • Async reads • Async writes • Async accepts

### Operating system

Linux networking APIs and I/O facilities

The central component is `io_context`. Think of it as an event loop that runs handlers when asynchronous operations complete.

For example:

1. Your peer requests a TCP connection.
2. Boost.Asio registers the asynchronous operation.
3. Your program can initiate other operations instead of blocking on that connection.
4. When the connection succeeds or fails, the corresponding handler runs.

Important: asynchronous networking does not automatically mean multithreading. One thread running `io_context.run()` can manage many network connections. You can also use multiple threads when needed.

## 3. Blocking sockets vs. Boost.Asio

| Concept              | Traditional sockets      | Boost.Asio                             |
| -------------------- | ------------------------ | -------------------------------------- |
| Accept connection    | `accept()`               | `async_accept()`                       |
| Receive data         | `recv()`                 | `async_read()` or `async_read_until()` |
| Send data            | `send()`                 | `async_write()`                        |
| Concurrency approach | Often threads per client | Event-driven operations                |
| Resource management  | Mostly manual            | Higher-level socket abstractions       |

Boost.Asio also supports synchronous operations, so you don't have to use asynchronous APIs for everything.

## 4. Where is Boost.Asio used?

- TCP servers handling many clients.
- Multiplayer game networking.
- P2P applications and file-sharing systems.
- Network proxies and messaging services.
- Applications that need asynchronous timers and network operations.

## 5. How it fits into your P2P project

Your current architecture is approximately:

Peer class

Message IDs • Neighbors • Forwarding

Boost.Asio networking layer

Async accept • Async read • Async write

TCP/IP network

You can keep your message-ID logic from Lab 4 and replace the low-level socket operations with Boost.Asio operations. Your P2P protocol and your networking implementation are separate concerns.

Your next exercise: build a basic asynchronous TCP server using `boost::asio::ip::tcp::acceptor` and `async_accept()`. This is the first step toward converting your existing `Peer` class to Boost.Asio.


--------------------------------------------------------------------------------------------------------------------------------------------------
Let's start Lab 5 — Boost.Asio coding, step by step. We'll begin with an asynchronous TCP server, test it, and then integrate it into your P2P `Peer` class with message IDs.

# Step 1 — Build your first asynchronous TCP server

## 1. Create the file

Open your Lab 5 directory and create `server.cpp`:

```
cd ~/Documents/blockchain/lession_07/torrent_form_scratch/lab05_asio
nano server.cpp
```

## 2. Write the code

```

#include <iostream>
#include <boost/asio.hpp>

using boost::asio::ip::tcp;

class Server {
private:
    boost::asio::io_context io;
    tcp::acceptor acceptor;

public:
    Server(short port)
        : acceptor(
            io,
            tcp::endpoint(tcp::v4(), port)
        ) {}

    void start() {
        std::cout << "Server listening on port "
                  << acceptor.local_endpoint().port()
                  << std::endl;

        accept_connection();

        // Process asynchronous events.
        io.run();
    }

private:
    void accept_connection() {
        acceptor.async_accept(
            [this](boost::system::error_code error,
                   tcp::socket socket) {
                if (!error) {
                    std::cout << "Client connected from "
                              << socket.remote_endpoint()
                              << std::endl;
                } else {
                    std::cerr << "Accept error: "
                              << error.message()
                              << std::endl;
                }

                // Continue accepting more clients.
                if (acceptor.is_open()) {
                    accept_connection();
                }
            }
        );
    }
};

int main() {
    try {
        Server server(5000);
        server.start();
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    }

    return 0;
}

```

## 3. Understand the important code

### `io_context`

```
boost::asio::io_context io;
```

This is the event-processing engine. Calling `io.run()` processes asynchronous operations and executes their handlers.

### `tcp::acceptor`

```
tcp::acceptor acceptor;
```

The acceptor listens for incoming TCP connections on port `5000`.

### `async_accept()`

```
acceptor.async_accept(
    [](boost::system::error_code error,
       tcp::socket socket) {
        // Runs when a connection attempt completes.
    }
);
```

Unlike blocking `accept()`, this schedules the operation and lets the event loop handle its completion later.

### Accepting the next client

```
accept_connection();
```

We call this again after each accept completes. That way, the server continues accepting clients while the event loop runs.

## 4. Compile and run

Compile:

```
g++ -std=c++17 -Wall -Wextra server.cpp -o server
```

Run:

```
./server
```

Expected output:

```
Server listening on port 5000
```

## 5. Test the server

Open another terminal:

```
nc 127.0.0.1 5000
```

The server should print a connection message, such as:

```
Client connected from 127.0.0.1:xxxxx
```

The connection is accepted, but this first version does not yet read messages from the client.

## Your task

Run the code and verify that the server accepts a connection.

Once it works, we'll implement Step 2 — asynchronous message reception with `async_read_until()`, then add responses and integrate message IDs.



------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Lab 5 — Step 2: Receive messages asynchronously

In Step 1, your Boost.Asio server accepted TCP connections, but it did not read data from them.

Now we'll use `async_read_until()` to receive a complete newline-terminated message without blocking the event loop.

## 1. How it works

TCP client

Sends `Hello from client\n`

`async_read_until()`

Waits asynchronously for newline

Completion handler

Prints the received message

## 2. Replace `server.cpp` with this complete code

```

#include <iostream>
#include <string>
#include <memory>

#include <boost/asio.hpp>

using boost::asio::ip::tcp;

class Server {
private:
    boost::asio::io_context io;
    tcp::acceptor acceptor;

public:
    Server(short port)
        : acceptor(io, tcp::endpoint(tcp::v4(), port)) {}

    void start() {
        std::cout << "Server listening on port "
                  << acceptor.local_endpoint().port()
                  << std::endl;

        accept_connection();
        io.run();
    }

private:
    void accept_connection() {
        acceptor.async_accept(
            [this](boost::system::error_code error,
                   tcp::socket socket) {
                if (!error) {
                    std::cout << "Client connected: "
                              << socket.remote_endpoint()
                              << std::endl;

                    // Keep the socket alive during async operations.
                    auto client = std::make_shared<tcp::socket>(
                        std::move(socket)
                    );

                    receive_message(client);
                } else {
                    std::cerr << "Accept error: "
                              << error.message() << std::endl;
                }

                if (acceptor.is_open()) {
                    accept_connection();
                }
            }
        );
    }

    void receive_message(
        std::shared_ptr<tcp::socket> client
    ) {
        auto buffer = std::make_shared<boost::asio::streambuf>();

        boost::asio::async_read_until(
            *client,
            *buffer,
            '\n',
            [this, client, buffer](
                boost::system::error_code error,
                std::size_t bytes_transferred
            ) {
                if (!error) {
                    std::istream input(buffer.get());
                    std::string message;
                    std::getline(input, message);

                    std::cout << "Received: "
                              << message << std::endl;

                    // Continue receiving from this client.
                    receive_message(client);
                } else if (error != boost::asio::error::eof) {
                    std::cerr << "Read error: "
                              << error.message() << std::endl;
                }
            }
        );
    }
};

int main() {
    try {
        Server server(5000);
        server.start();
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    }

    return 0;
}

```

## 3. Compile and run

```
g++ -std=c++17 -Wall -Wextra server.cpp -o server
./server
```

Open a second terminal:

```
nc 127.0.0.1 5000
```

Type several messages:

```
Hello
Message number two
Testing Boost.Asio
```

The server should print each message as you press Enter.

## 4. Understand the important parts

- `async_read_until()` schedules a read that completes when a newline is received.
- `std::shared_ptr` keeps the socket and buffer alive while the asynchronous operation is pending.
- `receive_message(client)` schedules another read, allowing the same client to send multiple messages.
- `accept_connection()` continues accepting new clients independently of those reads.

This is still a basic server: it doesn't yet send responses or limit the number of clients.

Next step — Step 3: implement `async_write()` so the server replies to each received message. After that, we'll integrate asynchronous message forwarding and duplicate detection into your P2P `Peer` class.

-----------------------------------------------------------------------------------------------------------------------------------------------------------------
# Lab 5 — Step 3: Send responses asynchronously with `async_write()`

In Step 2, your server received messages using `async_read_until()`. Now we'll make it respond to each message without blocking the event loop.

## 1. Understand the message flow

Client

Sends `PING`

Server: `async_read_until()`

Receives the message

Server: `async_write()`

Sends `PONG` asynchronously

Client

Receives `PONG`

## 2. Complete code — `server.cpp`

Replace your previous code with this version:

```

#include <iostream>
#include <string>
#include <memory>

#include <boost/asio.hpp>

using boost::asio::ip::tcp;

class Server {
private:
    boost::asio::io_context io;
    tcp::acceptor acceptor;

    struct Client {
        tcp::socket socket;
        boost::asio::streambuf buffer;

        explicit Client(tcp::socket s)
            : socket(std::move(s)) {}
    };

public:
    explicit Server(short port)
        : acceptor(io, tcp::endpoint(tcp::v4(), port)) {}

    void start() {
        std::cout << "Server listening on port "
                  << acceptor.local_endpoint().port()
                  << std::endl;

        accept_connection();
        io.run();
    }

private:
    void accept_connection() {
        acceptor.async_accept(
            [this](boost::system::error_code error,
                   tcp::socket socket) {
                if (!error) {
                    auto client = std::make_shared<Client>(
                        std::move(socket)
                    );

                    std::cout << "Client connected\n";
                    receive_message(client);
                } else {
                    std::cerr << "Accept error: "
                              << error.message() << '\n';
                }

                if (acceptor.is_open()) {
                    accept_connection();
                }
            }
        );
    }

    void receive_message(std::shared_ptr<Client> client) {
        boost::asio::async_read_until(
            client->socket,
            client->buffer,
            '\n',
            [this, client](
                boost::system::error_code error,
                std::size_t /*bytes_transferred*/
            ) {
                if (error) {
                    if (error != boost::asio::error::eof) {
                        std::cerr << "Read error: "
                                  << error.message() << '\n';
                    }
                    return;
                }

                std::istream input(&client->buffer);
                std::string message;
                std::getline(input, message);

                std::cout << "Received: " << message << '\n';

                std::string response =
                    (message == "PING" ? "PONG" : "ACK") + '\n';

                send_response(client, std::move(response));
            }
        );
    }

    void send_response(
        std::shared_ptr<Client> client,
        std::string response
    ) {
        // Keep response alive until async_write completes.
        auto data = std::make_shared<std::string>(
            std::move(response)
        );

        boost::asio::async_write(
            client->socket,
            boost::asio::buffer(*data),
            [this, client, data](
                boost::system::error_code error,
                std::size_t /*bytes_transferred*/
            ) {
                if (error) {
                    std::cerr << "Write error: "
                              << error.message() << '\n';
                    return;
                }

                std::cout << "Response sent\n";

                // Wait for the next message from this client.
                receive_message(client);
            }
        );
    }
};

int main() {
    try {
        Server server(5000);
        server.start();
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << '\n';
        return 1;
    }

    return 0;
}

```

## 3. Compile and test

Compile:

```
g++ -std=c++17 -Wall -Wextra server.cpp -o server
```

Run:

```
./server
```

In another terminal, connect:

```
nc 127.0.0.1 5000
```

Type:

```
PING
```

Expected response:

```
PONG
```

Then type:

```
Hello
```

Expected response:

```
ACK
```

You can send multiple messages through the same connection.

## 4. What did you learn?

- `async_read_until()` receives newline-delimited messages.
- `async_write()` sends the response asynchronously.
- The `Client` structure keeps each client's socket and read buffer together.
- `std::shared_ptr` keeps the client and outgoing response alive until their asynchronous operations finish.
- The server can accept other connections while existing clients are waiting for network I/O.

Next step — Step 4: make the asynchronous server support the message protocol `ID|TYPE|PAYLOAD`, then add duplicate detection and message propagation to build your Boost.Asio P2P node.

------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Lab 5 — Final Step: Build the asynchronous P2P node

Yes — we're at the integration stage of Lab 5. We'll combine what you learned with Boost.Asio into one `Peer` class.

The final program will support:

- Asynchronous TCP connections using `async_accept()`.
- Asynchronous message reception and sending.
- Message format `ID|TYPE|PAYLOAD`.
- Per-peer duplicate detection.
- Forwarding messages through a three-peer network.
- Multiple clients managed by one `io_context` event loop.

The key difference from Lab 4 is that we no longer need one thread per incoming connection. We'll use one event-loop thread for this lab.

## 1. Create `peer.cpp`

This implementation uses asynchronous operations for both incoming and outgoing TCP connections. Each incoming connection carries one newline-terminated message, and each peer forwards a newly received message to its neighbors.

```

#include <iostream>
#include <string>
#include <vector>
#include <unordered_set>
#include <memory>
#include <mutex>
#include <thread>
#include <atomic>

#include <boost/asio.hpp>

using boost::asio::ip::tcp;

class Peer {
private:
    int port_;
    std::vector<int> neighbors_;

    boost::asio::io_context io_;
    tcp::acceptor acceptor_;
    std::thread io_thread_;

    std::atomic<bool> running_{false};

    std::unordered_set<std::string> seen_messages_;
    std::mutex seen_mutex_;
    std::mutex output_mutex_;

    void log(const std::string& message) {
        std::lock_guard<std::mutex> lock(output_mutex_);
        std::cout << "[Peer " << port_ << "] "
                  << message << '\n';
    }

    std::string extract_id(const std::string& message) {
        const auto pos = message.find('|');

        if (pos == std::string::npos || pos == 0) {
            return "";
        }

        return message.substr(0, pos);
    }

    bool valid_message(const std::string& message) {
        const auto first = message.find('|');

        if (first == std::string::npos || first == 0) {
            return false;
        }

        const auto second = message.find('|', first + 1);

        return second != std::string::npos &&
               second != first + 1;
    }

    // Asynchronously accept incoming connections.
    void accept_connection() {
        if (!running_) {
            return;
        }

        acceptor_.async_accept(
            [this](boost::system::error_code error,
                   tcp::socket socket) {
                if (!error) {
                    auto client = std::make_shared<tcp::socket>(
                        std::move(socket)
                    );

                    receive_message(client);
                } else if (running_) {
                    log("Accept error: " + error.message());
                }

                if (running_) {
                    accept_connection();
                }
            }
        );
    }

    // Read one newline-terminated message asynchronously.
    void receive_message(
        std::shared_ptr<tcp::socket> socket
    ) {
        auto buffer =
            std::make_shared<boost::asio::streambuf>(4096);

        boost::asio::async_read_until(
            *socket,
            *buffer,
            '\n',
            [this, socket, buffer](
                boost::system::error_code error,
                std::size_t /*bytes_transferred*/
            ) {
                if (error) {
                    if (error != boost::asio::error::eof &&
                        running_) {
                        log("Read error: " + error.message());
                    }
                    return;
                }

                std::istream input(buffer.get());
                std::string message;
                std::getline(input, message);

                process_message(message);
            }
        );
    }

    // Process each message ID only once per peer.
    void process_message(const std::string& message) {
        if (!valid_message(message)) {
            log("Invalid message format");
            return;
        }

        const std::string id = extract_id(message);
        bool is_new;

        {
            std::lock_guard<std::mutex> lock(seen_mutex_);
            is_new = seen_messages_.insert(id).second;
        }

        if (!is_new) {
            log("Duplicate ignored: " + id);
            return;
        }

        log("Processed: " + message);

        // Forward the new message to every neighbor.
        broadcast_message(message);
    }

    void broadcast_message(const std::string& message) {
        for (int neighbor_port : neighbors_) {
            if (neighbor_port != port_) {
                send_to_peer(neighbor_port, message);
            }
        }
    }

    // Connect and send without blocking the event loop.
    void send_to_peer(
        int neighbor_port,
        const std::string& message
    ) {
        auto socket =
            std::make_shared<tcp::socket>(io_);

        auto data =
            std::make_shared<std::string>(message + "\n");

        auto endpoint = tcp::endpoint(
            boost::asio::ip::address_v4::loopback(),
            static_cast<unsigned short>(neighbor_port)
        );

        socket->async_connect(
            endpoint,
            [this, socket, data, neighbor_port](
                boost::system::error_code error
            ) {
                if (error) {
                    if (running_) {
                        log("Connection to port " +
                            std::to_string(neighbor_port) +
                            " failed: " + error.message());
                    }
                    return;
                }

                boost::asio::async_write(
                    *socket,
                    boost::asio::buffer(*data),
                    [this, socket, data, neighbor_port](
                        boost::system::error_code write_error,
                        std::size_t /*bytes_written*/
                    ) {
                        if (write_error && running_) {
                            log("Send to port " +
                                std::to_string(neighbor_port) +
                                " failed: " +
                                write_error.message());
                        }
                    }
                );
            }
        );
    }

public:
    Peer(int port, const std::vector<int>& neighbors)
        : port_(port),
          neighbors_(neighbors),
          acceptor_(io_) {}

    Peer(const Peer&) = delete;
    Peer& operator=(const Peer&) = delete;

    ~Peer() {
        stop();
    }

    void start() {
        tcp::endpoint endpoint(
            tcp::v4(),
            static_cast<unsigned short>(port_)
        );

        acceptor_.open(endpoint.protocol());
        acceptor_.set_option(
            tcp::acceptor::reuse_address(true)
        );
        acceptor_.bind(endpoint);
        acceptor_.listen();

        running_ = true;

        accept_connection();

        io_thread_ = std::thread([this]() {
            io_.run();
        });

        log("Listening on port " + std::to_string(port_));
    }

    // Schedule locally generated messages on the event loop.
    void send_message(const std::string& message) {
        if (!valid_message(message)) {
            log("Use ID|TYPE|PAYLOAD");
            return;
        }

        boost::asio::post(io_, [this, message]() {
            if (running_) {
                process_message(message);
            }
        });
    }

    void stop() {
        if (!running_.exchange(false)) {
            return;
        }

        // Stop event processing and wait for its thread.
        io_.stop();

        if (io_thread_.joinable()) {
            io_thread_.join();
        }

        boost::system::error_code error;
        acceptor_.close(error);

        log("Stopped");
    }
};

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cout
            << "Usage: ./peer PORT [NEIGHBOR_PORT...]\n";
        return 1;
    }

    try {
        const int port = std::stoi(argv[1]);
        std::vector<int> neighbors;

        for (int i = 2; i < argc; ++i) {
            neighbors.push_back(std::stoi(argv[i]));
        }

        Peer peer(port, neighbors);
        peer.start();

        std::cout << "Format: ID|TYPE|PAYLOAD\n";
        std::cout << "Example: a81f29|PING|Hello network\n";
        std::cout << "Type QUIT to exit.\n";

        std::string message;

        while (std::getline(std::cin, message)) {
            if (message == "QUIT") {
                break;
            }

            peer.send_message(message);
        }

        peer.stop();
    } catch (const std::exception& error) {
        std::cerr << "Error: " << error.what() << '\n';
        return 1;
    }

    return 0;
}

```

## 2. Compile

```
g++ -std=c++17 -Wall -Wextra peer.cpp -o peer -pthread -lboost_system
```

If Boost.Asio is installed correctly, compilation should succeed.

## 3. Start the P2P triangle

Open three terminals.

Terminal A:

```
./peer 5000 5001 5002
```

Terminal B:

```
./peer 5001 5000 5002
```

Terminal C:

```
./peer 5002 5000 5001
```

In Terminal A, send:

```
a81f29|PING|Hello from A
```

Then try a new message from Terminal B:

```
b72c10|CHAT|Hello from B
```

Each peer processes a new message ID once and forwards it. Messages returning through the triangle should be identified as duplicates.

## 4. What you completed in Lab 5

| Concept                            | Implementation                        |
| ---------------------------------- | ------------------------------------- |
| Asynchronous connection acceptance | `async_accept()`                      |
| Asynchronous reception             | `async_read_until()`                  |
| Asynchronous transmission          | `async_connect()` and `async_write()` |
| Event processing                   | `io_context` and `io.run()`           |
| Message identity                   | `seen_messages_`                      |
| P2P propagation                    | `broadcast_message()`                 |
| Class-based design                 | `Peer`                                |

### Important limitations

This is a learning prototype, not yet a production-ready P2P implementation. It uses one event-loop thread, assumes one message per connection, and uses localhost addresses. Shutdown stops the event loop immediately, so pending network operations may be cancelled. Also, a peer does not distinguish which neighbor sent an incoming message, and there is no peer discovery, authentication, or retry mechanism.

Lab 5's main lesson: asynchronous I/O lets one event loop coordinate multiple network operations without dedicating a thread to each connection.

Your next lab is Lab 6 — Binary Protocol Message Encoding, where you can move beyond text messages like `ID|TYPE|PAYLOAD` and learn to encode structured binary messages, similar in principle to protocols used in real P2P systems.


