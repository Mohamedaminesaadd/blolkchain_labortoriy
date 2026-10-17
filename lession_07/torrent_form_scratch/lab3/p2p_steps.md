1. Step 0 — Understand the architecture. What is a peer, a port, and a TCP connection?
2. Step 1 — One TCP connection. Peer A sends PING to Peer B; Peer B returns PONG.
3. Step 2 — Make both peers communicate. Both can send and receive messages.
4. Step 3 — Add Peer C. Connect three peers.
5. Step 4 — Propagate messages. A PING received by one peer can be forwarded to another peer.
6. Step 5 — Prevent loops. Avoid forwarding the same message forever.


# Step 1 — First TCP PING/PONG in C++

We will create the simplest working communication between two peers. No threads, no arrays of peers, no message propagation yet.

Goal: Peer A sends `PING` to Peer B, and Peer B responds with `PONG`.

## 1. Understand the architecture

Peer A — Client

127.0.0.1 · Connects to port 5000

PING

Peer B — Listener

127.0.0.1 · Listens on port 5000

PONG

One TCP connection, two-way communication.

For this first experiment, Peer A acts as the client and Peer B acts as the server. Later, both programs will be able to accept and initiate connections.

## 2. Create `server.cpp`

Go to your project directory:

```
cd ~/Documents/blockchain/lession_07/torrent_form_scratch/simple_p2p
```

Create `server.cpp`:

```

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

    // 6. Receive PING
    char buffer[1024];
    ssize_t n = recv(peer_fd, buffer, sizeof(buffer), 0);

    if (n > 0) {
        string request(buffer, static_cast<size_t>(n));
        cout << "Received: " << request << '\n';

        // 7. Process the request
        string response;

        if (request == "PING") {
            response = "PONG";
        } else {
            response = "UNKNOWN";
        }

        // 8. Send the response
        if (send(peer_fd, response.data(),
                 response.size(), 0) == -1) {
            perror("send");
        } else {
            cout << "Sent: " << response << '\n';
        }
    } else if (n == 0) {
        cout << "Peer disconnected.\n";
    } else {
        perror("recv");
    }

    // 9. Close sockets
    close(peer_fd);
    close(server_fd);

    return 0;
}

```

## 3. Create `client.cpp`

```

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

    // 4. Send PING
    string request = "PING";

    if (send(sock_fd, request.data(),
             request.size(), 0) == -1) {
        perror("send");
        close(sock_fd);
        return 1;
    }

    cout << "Sent: " << request << '\n';

    // 5. Receive PONG
    char buffer[1024];

    ssize_t n = recv(sock_fd, buffer, sizeof(buffer), 0);

    if (n > 0) {
        string response(buffer, static_cast<size_t>(n));
        cout << "Received: " << response << '\n';
    } else if (n == 0) {
        cout << "Server disconnected.\n";
    } else {
        perror("recv");
    }

    // 6. Close the connection
    close(sock_fd);

    return 0;
}

```

## 4. Compile both programs

Run these commands in the project directory:

```
g++ -std=c++17 -Wall -Wextra server.cpp -o server
g++ -std=c++17 -Wall -Wextra client.cpp -o client
```

Remember the distinction from your earlier mistake: `server.cpp` produces `server`, and `client.cpp` produces `client`.

## 5. Run the experiment

Open two terminals.

Terminal 1 — Peer B

```
./server
```

Expected:

```
Peer B listening on port 5000...
```

Terminal 2 — Peer A

```
./client
```

Expected:

```
Connected to Peer B
Sent: PING
Received: PONG
```

Peer B should display:

```
Peer B listening on port 5000...
Peer A connected!
Received: PING
Sent: PONG
```

## 6. What you have learned

- `server_fd` listens for new connections.
- `peer_fd` represents the connection accepted by Peer B.
- `sock_fd` represents Peer A's connection.
- `send()` transmits bytes.
- `recv()` receives bytes.
- The same TCP connection carries `PING` toward Peer B and `PONG` back toward Peer A.

One limitation: this version exchanges one request and one response, then closes the connection. We will extend it gradually.

Your task now: run both programs and confirm that you see `Received: PONG`. Once this works, Step 2 will allow repeated PING/PONG exchanges over the same connection.

------------------------------------------------------------------------------------------------------------------------------------------------------------
# Step 2 — Repeated PING/PONG over one TCP connection

In Step 1, Peer A sent one `PING`, received one `PONG`, and the connection closed.

Now we will make the smallest possible change: keep the TCP connection open and exchange multiple messages.

## 1. What we are building

Peer A — Client

PING

PONG

PING

PONG

Peer B — Server

One TCP connection stays open until QUIT.

## 2. Update `server.cpp`

Keep the socket setup from Step 1. Replace the section that receives one message with this loop:

```

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

```

The important change is `while (true)`: the server processes more than one request without calling `accept()` again.

## 3. Update `client.cpp`

Keep the socket creation and connection setup from Step 1. Replace the single-send/single-receive section with this loop:

```

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

```

## 4. Compile again

```
g++ -std=c++17 -Wall -Wextra server.cpp -o server
g++ -std=c++17 -Wall -Wextra client.cpp -o client
```

## 5. Test it

Start the server in Terminal 1:

```
./server
```

Start the client in Terminal 2:

```
./client
```

Try this sequence:

```
Enter command (PING or QUIT): PING
Received: PONG
Enter command (PING or QUIT): PING
Received: PONG
Enter command (PING or QUIT): PING
Received: PONG
Enter command (PING or QUIT): QUIT
Received: BYE
```

## 6. What you learned

- A TCP connection can carry multiple requests.
- The server can process requests in a loop.
- The client sends a request and waits for its response.
- `QUIT` provides a simple way to end the session.

One limitation remains: TCP is a byte stream, so one `recv()` is not guaranteed to correspond to exactly one `send()`. Our short-message experiment assumes that each command and response arrives in one read. We will improve message framing when needed.

Next step — Step 3: make the connection genuinely bidirectional, so either peer can initiate a message rather than always having Peer A send the first request.


# Step 3 — Both Peers Can Send and Receive Messages

In Step 2, Peer A sends commands and Peer B responds. Now we will make communication bidirectional: either peer can send a message whenever it wants.

We will keep the code simple and build on your existing `server.cpp` and `client.cpp`.

## 1. Understand the architecture

Peer A — Port 5000

One TCP connection, two-way communication

Peer B — Port 5001

For this step, Peer B still listens for the connection and Peer A connects to it. However, both programs can now send messages and receive messages independently.

To achieve that, each program will use two threads:

- Main thread: reads your keyboard input and sends messages.
- Receiver thread: waits for incoming messages and displays them.

## 2. Create `peer.cpp`

Instead of maintaining separate client and server files, let's simplify the next step into one program that can run in either mode.

Create `peer.cpp`:

```

#include <iostream>
#include <string>
#include <thread>
#include <atomic>

#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>

using namespace std;

void receive_messages(int fd, atomic<bool>& running) {
    char buffer[1024];

    while (running.load()) {
        ssize_t n = recv(fd, buffer, sizeof(buffer), 0);

        if (n == 0) {
            cout << "\nPeer disconnected.\n";
            break;
        }

        if (n < 0) {
            if (running.load()) {
                perror("recv");
            }
            break;
        }

        cout << "\nPeer says: "
             << string(buffer, static_cast<size_t>(n))
             << "\n> " << flush;
    }

    running.store(false);
}

int main(int argc, char* argv[]) {
    if (argc != 3) {
        cout << "Usage:\n"
             << "  ./peer listen <port>\n"
             << "  ./peer connect <ip> <port>\n";
        return 1;
    }

    string mode = argv[1];
    int fd = -1;

    if (mode == "listen") {
        int port = stoi(argv[2]);

        int server_fd = socket(AF_INET, SOCK_STREAM, 0);
        if (server_fd == -1) {
            perror("socket");
            return 1;
        }

        int opt = 1;
        setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR,
                   &opt, sizeof(opt));

        sockaddr_in address{};
        address.sin_family = AF_INET;
        address.sin_port = htons(port);
        address.sin_addr.s_addr = htonl(INADDR_LOOPBACK);

        if (bind(server_fd,
                 reinterpret_cast<sockaddr*>(&address),
                 sizeof(address)) == -1) {
            perror("bind");
            close(server_fd);
            return 1;
        }

        if (listen(server_fd, 5) == -1) {
            perror("listen");
            close(server_fd);
            return 1;
        }

        cout << "Listening on port " << port << "...\n";

        fd = accept(server_fd, nullptr, nullptr);
        close(server_fd);

        if (fd == -1) {
            perror("accept");
            return 1;
        }
    } else if (mode == "connect" && argc == 4) {
        // This branch is corrected in the usage note below.
        int port = stoi(argv[3]);

        fd = socket(AF_INET, SOCK_STREAM, 0);
        if (fd == -1) {
            perror("socket");
            return 1;
        }

        sockaddr_in address{};
        address.sin_family = AF_INET;
        address.sin_port = htons(port);

        if (inet_pton(AF_INET, argv[2],
                      &address.sin_addr) != 1) {
            cerr << "Invalid IP address\n";
            close(fd);
            return 1;
        }

        if (connect(fd,
                    reinterpret_cast<sockaddr*>(&address),
                    sizeof(address)) == -1) {
            perror("connect");
            close(fd);
            return 1;
        }
    } else {
        cerr << "Invalid mode or arguments\n";
        return 1;
    }

    cout << "Connected! Type messages; /quit to exit.\n";

    atomic<bool> running{true};

    thread receiver(receive_messages, fd, ref(running));

    string message;

    while (running.load() && getline(cin, message)) {
        if (message == "/quit") {
            break;
        }

        if (send(fd, message.data(), message.size(), 0) == -1) {
            perror("send");
            break;
        }
    }

    running.store(false);
    shutdown(fd, SHUT_RDWR);
    close(fd);

    receiver.join();

    return 0;
}

```

## 3. Small correction to the argument check

The `connect` mode uses three arguments after the executable name? Actually, it uses the executable plus `connect`, IP, and port, so `argc` must be `4`. The initial argument validation must therefore allow both modes.

Replace the first argument check with:

```
if (argc < 3) {
    cerr << "Usage:\n"
         << "  ./peer listen <port>\n"
         << "  ./peer connect <ip> <port>\n";
    return 1;
}
```

The connection branch already checks `argc == 4`.

## 4. Compile

```
g++ -std=c++17 -Wall -Wextra peer.cpp -o peer -pthread
```

## 5. Run two peers

Terminal 1:

```
./peer listen 5000
```

Terminal 2:

```
./peer connect 127.0.0.1 5000
```

Now type a message in either terminal. The other peer should display it.

Example:

```
Peer says: Hello from Peer A!
```

Then send a reply from the listening peer:

```
Peer says: Hello from Peer B!
```

## 6. What you have learned

- TCP connections are bidirectional.
- `recv()` can block while waiting for incoming data.
- A receiver thread allows the main thread to read keyboard input simultaneously.
- A listening socket and a connected socket have different roles.

One limitation remains: the simple `send()` and `recv()` calls assume that each typed message arrives as one read. TCP does not guarantee that. We will introduce a simple message delimiter before relying on this for P2P propagation.

Next: Step 4 — Add Peer C and forward messages from Peer A through Peer B.


# Step 4 — Connect Three Peers and Propagate Messages

Now we move from two peers to three. We will keep the design simple and reuse the TCP socket concepts you have already learned.

Goal: Peer A sends `PING` to Peer B. Peer B forwards it to Peer C. Both B and C respond with `PONG`.

## 1. Architecture

Peer A

Port 5000

PING → · ← PONG

Peer B

Port 5001 · forwards PING

PING → · ← PONG

Peer C

Port 5002

For this first propagation experiment, we will use a chain: A connects to B, and B connects to C. Each connection is a separate TCP connection.

## 2. Use a simple protocol

We will send these commands:

- `PING` — request a response.
- `PONG` — response to a ping.
- `FORWARD_PING` — tell Peer B to propagate the ping to Peer C.

We will keep the protocol small so that you can focus on propagation rather than complex networking code.

## 3. Create `peer.cpp`

Replace your existing `peer.cpp` with this simplified three-peer version.

```

#include <iostream>
#include <string>

#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>

using namespace std;

int create_listener(int port) {
    int fd = socket(AF_INET, SOCK_STREAM, 0);
    if (fd == -1) {
        perror("socket");
        return -1;
    }

    int opt = 1;
    setsockopt(fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    sockaddr_in addr{};
    addr.sin_family = AF_INET;
    addr.sin_port = htons(port);
    addr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);

    if (bind(fd, reinterpret_cast<sockaddr*>(&addr),
             sizeof(addr)) == -1) {
        perror("bind");
        close(fd);
        return -1;
    }

    if (listen(fd, 5) == -1) {
        perror("listen");
        close(fd);
        return -1;
    }

    return fd;
}

int connect_peer(int port) {
    int fd = socket(AF_INET, SOCK_STREAM, 0);
    if (fd == -1) {
        perror("socket");
        return -1;
    }

    sockaddr_in addr{};
    addr.sin_family = AF_INET;
    addr.sin_port = htons(port);
    addr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);

    if (connect(fd, reinterpret_cast<sockaddr*>(&addr),
                sizeof(addr)) == -1) {
        perror("connect");
        close(fd);
        return -1;
    }

    return fd;
}

bool send_message(int fd, const string& message) {
    string data = message + "\n";
    size_t total = 0;

    while (total < data.size()) {
        ssize_t n = send(fd, data.data() + total,
                         data.size() - total, MSG_NOSIGNAL);

        if (n <= 0) {
            perror("send");
            return false;
        }

        total += static_cast<size_t>(n);
    }

    return true;
}

bool receive_message(int fd, string& message) {
    message.clear();

    while (true) {
        char ch;
        ssize_t n = recv(fd, &ch, 1, 0);

        if (n <= 0) {
            return false;
        }

        if (ch == '\n') {
            return true;
        }

        message += ch;
    }
}

int main(int argc, char* argv[]) {
    if (argc != 2) {
        cout << "Usage: ./peer <A|B|C>\n";
        return 1;
    }

    string role = argv[1];

    if (role == "A") {
        // Peer A connects to B.
        int fd = connect_peer(5001);
        if (fd == -1) return 1;

        cout << "A: Sending PING to B\n";
        send_message(fd, "PING");

        string response;
        if (receive_message(fd, response)) {
            cout << "A: Received " << response << " from B\n";
        }

        close(fd);
    }
    else if (role == "B") {
        // Peer B listens for A.
        int listen_fd = create_listener(5001);
        if (listen_fd == -1) return 1;

        cout << "B: Waiting for A\n";
        int a_fd = accept(listen_fd, nullptr, nullptr);
        if (a_fd == -1) {
            perror("accept A");
            close(listen_fd);
            return 1;
        }

        // Peer B connects to C.
        int c_fd = connect_peer(5002);
        if (c_fd == -1) {
            close(a_fd);
            close(listen_fd);
            return 1;
        }

        string request;
        if (receive_message(a_fd, request)) {
            cout << "B: Received " << request << " from A\n";

            if (request == "PING") {
                // Forward PING to C.
                cout << "B: Forwarding PING to C\n";
                send_message(c_fd, "PING");

                string c_response;
                if (receive_message(c_fd, c_response)) {
                    cout << "B: Received " << c_response
                         << " from C\n";
                }

                // Respond to A.
                send_message(a_fd, "PONG");
                cout << "B: Sent PONG to A\n";
            }
        }

        close(c_fd);
        close(a_fd);
        close(listen_fd);
    }
    else if (role == "C") {
        // Peer C listens for B.
        int listen_fd = create_listener(5002);
        if (listen_fd == -1) return 1;

        cout << "C: Waiting for B\n";
        int b_fd = accept(listen_fd, nullptr, nullptr);

        if (b_fd == -1) {
            perror("accept B");
            close(listen_fd);
            return 1;
        }

        string request;
        if (receive_message(b_fd, request)) {
            cout << "C: Received " << request << " from B\n";

            if (request == "PING") {
                send_message(b_fd, "PONG");
                cout << "C: Sent PONG to B\n";
            }
        }

        close(b_fd);
        close(listen_fd);
    }
    else {
        cout << "Role must be A, B, or C\n";
        return 1;
    }

    return 0;
}

```

## 4. Compile the program

```
g++ -std=c++17 -Wall -Wextra peer.cpp -o peer
```

## 5. Start the peers in the correct order

Open three terminals in the same directory.

Terminal 1 — Peer C

```
./peer C
```

Peer C starts listening on port 5002.

Terminal 2 — Peer B

```
./peer B
```

Peer B listens on port 5001 and attempts to connect to Peer C.

Terminal 3 — Peer A

```
./peer A
```

Peer A connects to Peer B and initiates `PING`.

## 6. Expected behavior

Peer A:

```
A: Sending PING to B
A: Received PONG from B
```

Peer B:

```
B: Waiting for A
B: Received PING from A
B: Forwarding PING to C
B: Received PONG from C
B: Sent PONG to A
```

Peer C:

```
C: Waiting for B
C: Received PING from B
C: Sent PONG to B
```

## 7. What you have achieved

You now have a basic message-propagation chain:

1. A sends `PING` to B.
2. B forwards `PING` to C.
3. C returns `PONG` to B.
4. B returns `PONG` to A.

Notice that C's `PONG` does not reach A directly. B receives C's response and separately replies to A. That is the simplest chain to understand before implementing general message propagation.

Next step: we can make `PING` and `PONG` propagate through the network with message IDs, so every peer processes a message once and forwards it without creating infinite loops.


# Step 6 — Integrate Message IDs into Your C++ P2P Network

Now we will combine what you learned in Steps 4 and 5:

- TCP communication between peers.
- Forwarding `PING` messages.
- Assigning each message a unique ID.
- Ignoring duplicate messages.
- Returning `PONG` to the peer that originated the ping.

We will keep the architecture simple: Peer A → Peer B → Peer C.

## 1. Understand the message flow

Peer A

Creates PING|42

Peer B

Records ID 42, forwards PING|42

Peer C

Records ID 42, returns PONG|42

Peer B → Peer A

Forwards PONG|42 back to A

A message ID lets a peer recognize a duplicate. In this chain, each message travels along a defined path, so we do not yet have the complex routing of a fully connected P2P network.

## 2. Create `peer.cpp`

This version uses one TCP connection between each adjacent peer. It keeps the message format simple: `TYPE|ID`.

```

#include <iostream>
#include <string>
#include <unordered_set>

#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>

using namespace std;

unordered_set<string> seen_messages;

int create_listener(int port) {
    int fd = socket(AF_INET, SOCK_STREAM, 0);
    if (fd == -1) {
        perror("socket");
        return -1;
    }

    int opt = 1;
    setsockopt(fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    sockaddr_in address{};
    address.sin_family = AF_INET;
    address.sin_port = htons(port);
    address.sin_addr.s_addr = htonl(INADDR_LOOPBACK);

    if (bind(fd, reinterpret_cast<sockaddr*>(&address),
             sizeof(address)) == -1) {
        perror("bind");
        close(fd);
        return -1;
    }

    if (listen(fd, 5) == -1) {
        perror("listen");
        close(fd);
        return -1;
    }

    return fd;
}

int connect_peer(int port) {
    int fd = socket(AF_INET, SOCK_STREAM, 0);
    if (fd == -1) {
        perror("socket");
        return -1;
    }

    sockaddr_in address{};
    address.sin_family = AF_INET;
    address.sin_port = htons(port);
    address.sin_addr.s_addr = htonl(INADDR_LOOPBACK);

    if (connect(fd, reinterpret_cast<sockaddr*>(&address),
                sizeof(address)) == -1) {
        perror("connect");
        close(fd);
        return -1;
    }

    return fd;
}

bool send_message(int fd, const string& message) {
    string data = message + "\n";
    size_t total = 0;

    while (total < data.size()) {
        ssize_t n = send(fd, data.data() + total,
                         data.size() - total, MSG_NOSIGNAL);

        if (n <= 0) {
            perror("send");
            return false;
        }

        total += static_cast<size_t>(n);
    }

    return true;
}

bool receive_message(int fd, string& message) {
    message.clear();

    while (true) {
        char ch;
        ssize_t n = recv(fd, &ch, 1, 0);

        if (n <= 0) return false;
        if (ch == '\n') return true;

        message += ch;
    }
}

bool is_new_message(const string& message) {
    size_t separator = message.find('|');

    if (separator == string::npos ||
        separator + 1 == message.size()) {
        cout << "Invalid message: " << message << '\n';
        return false;
    }

    string id = message.substr(separator + 1);

    if (!seen_messages.insert(id).second) {
        cout << "Duplicate ignored: " << id << '\n';
        return false;
    }

    return true;
}

int main(int argc, char* argv[]) {
    if (argc != 2) {
        cout << "Usage: ./peer <A|B|C>\n";
        return 1;
    }

    string role = argv[1];

    if (role == "C") {
        int listen_fd = create_listener(5002);
        if (listen_fd == -1) return 1;

        cout << "C: Listening on 5002\n";

        int b_fd = accept(listen_fd, nullptr, nullptr);
        close(listen_fd);

        if (b_fd == -1) {
            perror("accept");
            return 1;
        }

        string message;

        if (receive_message(b_fd, message)) {
            cout << "C: Received " << message << '\n';

            if (is_new_message(message) &&
                message.rfind("PING|", 0) == 0) {
                string id = message.substr(message.find('|') + 1);
                string response = "PONG|" + id;

                send_message(b_fd, response);
                cout << "C: Sent " << response << '\n';
            }
        }

        close(b_fd);
    }
    else if (role == "B") {
        int listen_fd = create_listener(5001);
        if (listen_fd == -1) return 1;

        cout << "B: Listening on 5001\n";

        int a_fd = accept(listen_fd, nullptr, nullptr);

        if (a_fd == -1) {
            perror("accept");
            close(listen_fd);
            return 1;
        }

        int c_fd = connect_peer(5002);

        if (c_fd == -1) {
            close(a_fd);
            close(listen_fd);
            return 1;
        }

        string message;

        if (receive_message(a_fd, message)) {
            cout << "B: Received " << message << '\n';

            if (is_new_message(message) &&
                message.rfind("PING|", 0) == 0) {

                // Forward PING to C.
                send_message(c_fd, message);
                cout << "B: Forwarded " << message << " to C\n";

                string response;

                if (receive_message(c_fd, response)) {
                    cout << "B: Received " << response << '\n';

                    // Forward PONG to A.
                    send_message(a_fd, response);
                    cout << "B: Forwarded " << response << " to A\n";
                }
            }
        }

        close(c_fd);
        close(a_fd);
        close(listen_fd);
    }
    else if (role == "A") {
        int b_fd = connect_peer(5001);

        if (b_fd == -1) return 1;

        string message = "PING|42";

        seen_messages.insert("42");

        cout << "A: Sending " << message << '\n';
        send_message(b_fd, message);

        string response;

        if (receive_message(b_fd, response)) {
            cout << "A: Received " << response << '\n';
        }

        close(b_fd);
    }
    else {
        cout << "Role must be A, B, or C\n";
        return 1;
    }

    return 0;
}

```

## 3. Compile

```
g++ -std=c++17 -Wall -Wextra peer.cpp -o peer
```

## 4. Run the peers in order

Open three terminals in your `simple_p2p` directory.

Terminal 1 — Peer C

```
./peer C
```

C waits for B on port 5002.

Terminal 2 — Peer B

```
./peer B
```

B listens on port 5001 and connects to C.

Terminal 3 — Peer A

```
./peer A
```

A sends `PING|42` to B.

## 5. Expected result

The messages should travel in this order:

```
A -> B: PING|42
B -> C: PING|42
C -> B: PONG|42
B -> A: PONG|42
```

## 6. What you learned

- The message ID identifies a particular request.
- Peer B checks the ID before forwarding the request.
- Peer C checks the ID before responding.
- Peer B forwards the response back to the originator.

One limitation remains: because this is a chain with one request at a time, it does not yet demonstrate duplicate detection across multiple network paths. That becomes useful when peers form a mesh or a more general P2P topology.

Next: Step 7 — let peers connect to multiple neighbors and propagate messages safely through the network.



# Step 7 — Build a Small P2P Network with Multiple Neighbors

In Step 6, we built a chain:

`Peer A → Peer B → Peer C`

Now we will make a small change to the architecture: Peer B will connect to both A and C, allowing messages to travel across multiple connections.

Our goal is to learn how a peer forwards a message to its neighbors without forwarding the same message repeatedly.

## 1. Architecture

Peer A — Port 5000

TCP

Peer B — Port 5001

Forwards new messages

TCP

Peer C — Port 5002

This is still a chain. To create multiple paths, we will eventually add a direct connection between A and C, forming a triangle. For this step, we will first learn the basic forwarding rule.

## 2. The forwarding rule

Suppose Peer A sends:

```
PING|42
```

Peer B receives it and checks the ID.

- If ID `42` is new, Peer B processes and forwards the message.
- If ID `42` has already been seen, Peer B ignores it.
- Peer C receives the message and responds with `PONG|42`.

This is the same idea used in many message-propagation systems: identify each message, track what has been seen, and avoid unnecessary repetition.

## 3. Create a small forwarding simulation

Before modifying your TCP program, let's test the forwarding logic independently.

Create `step7.cpp`:

```

#include <iostream>
#include <string>
#include <unordered_set>

using namespace std;

unordered_set<string> seen;

void receive_message(const string& peer,
                     const string& message) {
    size_t separator = message.find('|');

    if (separator == string::npos) {
        cout << peer << ": Invalid message\n";
        return;
    }

    string type = message.substr(0, separator);
    string id = message.substr(separator + 1);

    // Check whether this peer has already seen the message.
    if (!seen.insert(id).second) {
        cout << peer << ": Duplicate " << id
             << " ignored\n";
        return;
    }

    cout << peer << ": Received " << message << '\n';

    if (type == "PING") {
        cout << peer << ": Process PING and forward it\n";
    } else if (type == "PONG") {
        cout << peer << ": Process PONG\n";
    } else {
        cout << peer << ": Unknown message type\n";
    }
}

int main() {
    receive_message("Peer B", "PING|42");
    receive_message("Peer C", "PING|42");
    receive_message("Peer B", "PING|42");

    return 0;
}

```

Compile and run:

```
g++ -std=c++17 -Wall -Wextra step7.cpp -o step7
./step7
```

Expected output:

```
Peer B: Received PING|42
Peer B: Process PING and forward it
Peer C: Duplicate 42 ignored
Peer B: Duplicate 42 ignored
```

## 4. Why is this output wrong?

There is an important design error in the simulation above: the `seen` set is global, so Peer B and Peer C share the same history. In a real P2P network, each peer runs its own process and maintains its own set of seen message IDs.

Let's correct that.

```

#include <iostream>
#include <string>
#include <unordered_set>

using namespace std;

class Peer {
private:
    string name;
    unordered_set<string> seen;

public:
    explicit Peer(string peer_name)
        : name(std::move(peer_name)) {}

    void receive_message(const string& message) {
        size_t separator = message.find('|');

        if (separator == string::npos) {
            cout << name << ": Invalid message\n";
            return;
        }

        string type = message.substr(0, separator);
        string id = message.substr(separator + 1);

        if (!seen.insert(id).second) {
            cout << name << ": Duplicate " << id
                 << " ignored\n";
            return;
        }

        cout << name << ": Received " << message << '\n';

        if (type == "PING") {
            cout << name << ": Process and forward PING\n";
        } else if (type == "PONG") {
            cout << name << ": Process PONG\n";
        }
    }
};

int main() {
    Peer peerB("Peer B");
    Peer peerC("Peer C");

    peerB.receive_message("PING|42");
    peerC.receive_message("PING|42");
    peerB.receive_message("PING|42");

    return 0;
}

```

Compile and run this version. Peer B and Peer C will each accept message `PING|42` once, while Peer B ignores its second copy.

## 5. What you learned

- Each peer must maintain its own set of seen IDs.
- The same message can be valid when received for the first time by different peers.
- Duplicate detection prevents one peer from repeatedly processing the same message.
- Forwarding requires actual neighbor connections; printing "forward" is only a simulation.

Next step: we can integrate this per-peer duplicate detection into the TCP code and add the direct A–C connection to form a triangle. That will let you observe a message arriving through two different paths and being ignored on its second arrival.


## Step 9 — Propagate messages without infinite loops

In Step 8, the three peers connected in a triangle. Now we want a message sent by Peer A to reach Peer B and Peer C.

The problem is that a triangle creates a loop:

Peer A

PING|42

Peer B

Peer C

B can forward to C, while C can forward back to A.

Without duplicate detection, the same message could circulate repeatedly.

Our solution: every peer remembers the IDs of messages it has already processed. When it receives `PING|42` for the first time, it accepts it. If it receives `PING|42` again, it ignores it.

## 1. Create `step9.cpp`

This version builds on Step 8. Each peer will:

1. Listen for incoming TCP messages.
2. Remember message IDs it has already seen.
3. Forward each new message to its neighbors.
4. Ignore duplicate messages to stop loops.

```
#include <iostream>
#include <string>
#include <vector>
#include <unordered_set>
#include <thread>
#include <mutex>
#include <cstdlib>

#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <netinet/in.h>

int my_port;
std::vector<int> neighbors;

std::unordered_set<std::string> seen_messages;
std::mutex seen_mutex;

void send_to_peer(int peer_port, const std::string& message) {
    int sock = socket(AF_INET, SOCK_STREAM, 0);

    if (sock < 0) {
        return;
    }

    sockaddr_in addr{};
    addr.sin_family = AF_INET;
    addr.sin_port = htons(peer_port);
    inet_pton(AF_INET, "127.0.0.1", &addr.sin_addr);

    if (connect(sock, (sockaddr*)&addr, sizeof(addr)) == 0) {
        send(sock, message.c_str(), message.size(), 0);
    }

    close(sock);
}

void broadcast_message(const std::string& message) {
    for (int port : neighbors) {
        send_to_peer(port, message);
    }
}

void listen_for_peers() {
    int server = socket(AF_INET, SOCK_STREAM, 0);

    int reuse = 1;
    setsockopt(server, SOL_SOCKET, SO_REUSEADDR, &reuse, sizeof(reuse));

    sockaddr_in addr{};
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = INADDR_ANY;
    addr.sin_port = htons(my_port);

    if (bind(server, (sockaddr*)&addr, sizeof(addr)) < 0) {
        std::cerr << "Bind failed on port " << my_port << "\n";
        close(server);
        return;
    }

    if (listen(server, 10) < 0) {
        std::cerr << "Listen failed\n";
        close(server);
        return;
    }

    std::cout << "Peer listening on port " << my_port << "\n";

    while (true) {
        int client = accept(server, nullptr, nullptr);

        if (client < 0) {
            continue;
        }

        char buffer[1024]{};
        int n = recv(client, buffer, sizeof(buffer) - 1, 0);
        close(client);

        if (n <= 0) {
            continue;
        }

        std::string message(buffer, n);

        // Accept each message ID only once.
        bool is_new;

        {
            std::lock_guard<std::mutex> lock(seen_mutex);
            is_new = seen_messages.insert(message).second;
        }

        if (!is_new) {
            std::cout << "Duplicate ignored: " << message << "\n";
            continue;
        }

        std::cout << "New message received: " << message << "\n";

        // Forward the new message to every neighbor.
        broadcast_message(message);
    }
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cout << "Usage: ./step9 PORT [NEIGHBOR_PORT...]\n";
        return 1;
    }

    my_port = std::atoi(argv[1]);

    for (int i = 2; i < argc; i++) {
        neighbors.push_back(std::atoi(argv[i]));
    }

    std::thread listener(listen_for_peers);

    // Let the listener start before accepting user input.
    std::this_thread::sleep_for(std::chrono::milliseconds(300));

    std::cout << "Type a message such as PING|42, or QUIT to exit.\n";

    std::string message;

    while (std::getline(std::cin, message)) {
        if (message == "QUIT") {
            break;
        }

        broadcast_message(message);
    }

    listener.detach();
    return 0;
}
```

Add this missing include near the top:

```
#include <chrono>
```

## 2. Compile

```
g++ -std=c++17 step9.cpp -o step9 -pthread
```

Stop any old Step 8 processes using `Ctrl+C` before reusing the same ports.

## 3. Start the triangle network

Open three terminals.

Terminal A

```
./step9 5000 5001 5002
```

Terminal B

```
./step9 5001 5000 5002
```

Terminal C

```
./step9 5002 5000 5001
```

Wait until all three peers report that they are listening.

## 4. Send a message

In Terminal A, type:

```
PING|42
```

Peer A sends the message to B and C. Each receiving peer accepts the message once and forwards it. When the message returns to a peer that has already seen it, that peer ignores the duplicate.

Example output:

```
New message received: PING|42
Duplicate ignored: PING|42
```

The exact order depends on the timing of the connections.

## 5. What did we build?

Flooding

Every peer forwards a new message to all configured neighbors.

Duplicate detection

Each peer stores received message strings in `seen_messages`.

Loop prevention

The network can contain cycles without forwarding the same message forever.

Important limitation: this is a learning prototype. It uses the complete message string as the duplicate key, so sending the same message again will be ignored. A real protocol should use a distinct message ID, separate from its payload. This example also uses one `recv()` call per connection, which is not a robust TCP message-framing strategy.

### Step 10 — Next

We can introduce a proper message format:

```
MESSAGE_ID|MESSAGE_TYPE|PAYLOAD
```

For example:

```
a81f29|PING|Hello Bitcoin network
```

That will let us distinguish messages by ID, even when their payloads are identical.


# Step 11 — Refactor the P2P node into a C++ class

Now we’ll transform the complete Step 10 program into an object-oriented design. Instead of global variables and standalone functions, each peer will be an instance of a `Peer` class.

This is a useful step toward a maintainable P2P application, because each node owns its configuration, network listener, neighbors, and message history.

## 1. New class design

## Peer

One instance per network node

Attributes

`port`

`neighbors`

`seen_messages`

`server_socket`

Methods

`start()`

`listen_for_peers()`

`send_to_peer()`

`broadcast_message()`

`receive_message()`

For example, `Peer peerA(5000, {5001, 5002});` creates a node listening on port `5000` with two configured neighbors.

## 2. Complete code — `step11.cpp`

This version puts the networking logic into a single `Peer` class. It also adds a `stop()` method so the listener can shut down cleanly when you type `QUIT`.

```

#include <iostream>
#include <string>
#include <vector>
#include <unordered_set>
#include <thread>
#include <mutex>
#include <atomic>
#include <cstdlib>

#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <netinet/in.h>

class Peer {
private:
    int port;
    std::vector<int> neighbors;

    int server_socket = -1;
    std::thread listener_thread;
    std::atomic<bool> running{false};

    std::unordered_set<std::string> seen_messages;
    std::mutex seen_mutex;

    // Extract ID from ID|TYPE|PAYLOAD.
    std::string extract_message_id(const std::string& message) {
        size_t separator = message.find('|');

        if (separator == std::string::npos || separator == 0) {
            return "";
        }

        return message.substr(0, separator);
    }

    // Validate the basic message format.
    bool valid_message(const std::string& message) {
        size_t first = message.find('|');

        if (first == std::string::npos || first == 0) {
            return false;
        }

        size_t second = message.find('|', first + 1);

        if (second == std::string::npos || second == first + 1) {
            return false;
        }

        return true;
    }

    // Read one newline-terminated message.
    std::string receive_message(int client) {
        std::string message;
        char c;

        while (message.size() < 4096) {
            ssize_t n = recv(client, &c, 1, 0);

            if (n <= 0) {
                return "";
            }

            if (c == '\n') {
                return message;
            }

            message += c;
        }

        return "";
    }

    // Send all bytes, handling partial sends.
    bool send_all(int sock, const std::string& data) {
        size_t sent = 0;

        while (sent < data.size()) {
            ssize_t n = send(
                sock,
                data.data() + sent,
                data.size() - sent,
                0
            );

            if (n <= 0) {
                return false;
            }

            sent += static_cast<size_t>(n);
        }

        return true;
    }

    // Connect to one neighbor and send a message.
    void send_to_peer(int peer_port, const std::string& message) {
        int sock = socket(AF_INET, SOCK_STREAM, 0);

        if (sock < 0) {
            std::cerr << "Socket creation failed\n";
            return;
        }

        sockaddr_in addr{};
        addr.sin_family = AF_INET;
        addr.sin_port = htons(peer_port);
        inet_pton(AF_INET, "127.0.0.1", &addr.sin_addr);

        if (connect(sock, (sockaddr*)&addr, sizeof(addr)) == 0) {
            send_all(sock, message + "\n");
        } else {
            std::cerr << "Could not connect to port "
                      << peer_port << "\n";
        }

        close(sock);
    }

    // Forward to every configured neighbor.
    void broadcast_message(const std::string& message) {
        for (int peer_port : neighbors) {
            send_to_peer(peer_port, message);
        }
    }

    // Accept and process incoming connections.
    void listen_for_peers() {
        while (running) {
            int client = accept(server_socket, nullptr, nullptr);

            if (client < 0) {
                if (!running) {
                    break;
                }
                continue;
            }

            std::string message = receive_message(client);
            close(client);

            if (message.empty() || !valid_message(message)) {
                std::cout << "Invalid or empty message\n";
                continue;
            }

            std::string id = extract_message_id(message);
            bool is_new;

            {
                std::lock_guard<std::mutex> lock(seen_mutex);
                is_new = seen_messages.insert(id).second;
            }

            if (!is_new) {
                std::cout << "[Port " << port
                          << "] Duplicate ignored: " << id << "\n";
                continue;
            }

            std::cout << "[Port " << port
                      << "] Received: " << message << "\n";

            broadcast_message(message);
        }
    }

public:
    // Constructor: configure this peer.
    Peer(int peer_port, const std::vector<int>& peer_neighbors)
        : port(peer_port), neighbors(peer_neighbors) {}

    // Avoid accidentally copying a running network node.
    Peer(const Peer&) = delete;
    Peer& operator=(const Peer&) = delete;

    // Destructor: ensure resources are released.
    ~Peer() {
        stop();
    }

    // Start the TCP listener.
    bool start() {
        server_socket = socket(AF_INET, SOCK_STREAM, 0);

        if (server_socket < 0) {
            std::cerr << "Socket creation failed\n";
            return false;
        }

        int reuse = 1;
        setsockopt(
            server_socket, SOL_SOCKET, SO_REUSEADDR,
            &reuse, sizeof(reuse)
        );

        sockaddr_in addr{};
        addr.sin_family = AF_INET;
        addr.sin_addr.s_addr = INADDR_ANY;
        addr.sin_port = htons(port);

        if (bind(server_socket, (sockaddr*)&addr, sizeof(addr)) < 0) {
            std::cerr << "Bind failed on port " << port << "\n";
            close(server_socket);
            server_socket = -1;
            return false;
        }

        if (listen(server_socket, 10) < 0) {
            std::cerr << "Listen failed\n";
            close(server_socket);
            server_socket = -1;
            return false;
        }

        running = true;
        listener_thread = std::thread(&Peer::listen_for_peers, this);

        std::cout << "Peer listening on port " << port << "\n";
        return true;
    }

    // Stop the listener and release its resources.
    void stop() {
        if (!running.exchange(false)) {
            return;
        }

        shutdown(server_socket, SHUT_RDWR);
        close(server_socket);
        server_socket = -1;

        if (listener_thread.joinable()) {
            listener_thread.join();
        }
    }

    // Send a locally created message.
    void send_message(const std::string& message) {
        if (!valid_message(message)) {
            std::cout << "Use ID|TYPE|PAYLOAD\n";
            return;
        }

        std::string id = extract_message_id(message);
        bool is_new;

        {
            std::lock_guard<std::mutex> lock(seen_mutex);
            is_new = seen_messages.insert(id).second;
        }

        if (!is_new) {
            std::cout << "You already used message ID: "
                      << id << "\n";
            return;
        }

        std::cout << "[Port " << port
                  << "] Sending: " << message << "\n";

        broadcast_message(message);
    }
};

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cout
            << "Usage: ./step11 PORT [NEIGHBOR_PORT...]\n";
        return 1;
    }

    int port = std::atoi(argv[1]);
    std::vector<int> neighbors;

    for (int i = 2; i < argc; i++) {
        neighbors.push_back(std::atoi(argv[i]));
    }

    Peer peer(port, neighbors);

    if (!peer.start()) {
        return 1;
    }

    std::cout
        << "Enter ID|TYPE|PAYLOAD\n"
        << "Example: a81f29|PING|Hello network\n"
        << "Type QUIT to exit.\n";

    std::string message;

    while (std::getline(std::cin, message)) {
        if (message == "QUIT") {
            break;
        }

        peer.send_message(message);
    }

    peer.stop();
    return 0;
}

```

## 3. Compile and run

Compile:

```
g++ -std=c++17 -Wall -Wextra step11.cpp -o step11 -pthread
```

Open three terminals.

Terminal A:

```
./step11 5000 5001 5002
```

Terminal B:

```
./step11 5001 5000 5002
```

Terminal C:

```
./step11 5002 5000 5001
```

In Terminal A, send:

```
a81f29|PING|Hello network
```

You should see the message propagate to B and C. Duplicate IDs should be ignored.

To stop a peer, type:

```
QUIT
```

## 4. What changed with OOP?

| Before: procedural     | Now: object-oriented          |
| ---------------------- | ----------------------------- |
| Global `my_port`       | `Peer::port`                  |
| Global `neighbors`     | `Peer::neighbors`             |
| Global message history | `Peer::seen_messages`         |
| `listen_for_peers()`   | `Peer::listen_for_peers()`    |
| `broadcast_message()`  | `Peer::broadcast_message()`   |
| Manual cleanup         | `Peer::stop()` and destructor |

One important design point: every `Peer` instance has its own message history. This is essential because different nodes must independently track which messages they have already processed.

This remains a learning prototype: it uses localhost connections, sequentially handles incoming clients, and opens a new TCP connection for every message. It does not yet implement PING/PONG responses or a robust peer-discovery mechanism.

Next step: separate the protocol into a `Message` class or structure, then make `PING` produce a `PONG` response instead of blindly forwarding every message.