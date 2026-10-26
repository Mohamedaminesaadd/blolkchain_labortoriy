# 1. First, understand the purpose of `PeerIdentity`

In your C++ P2P file-sharing project, `PeerIdentity` represents one computer participating in your P2P network.

For example, suppose three computers want to share files:

| Peer | ID         | IP address     | Port |
| ---- | ---------- | -------------- | ---- |
| A    | `peer-001` | `192.168.1.10` | 5001 |
| B    | `peer-002` | `192.168.1.11` | 5002 |
| C    | `peer-003` | `192.168.1.12` | 5003 |

Your program needs a way to represent the identity and network address of each peer. That's what this structure does.

# 2. Understand the code line by line

## A. Header guards

```
#ifndef PEER_IDENTITY_HPP
#define PEER_IDENTITY_HPP

// Your code goes here

#endif
```

These lines prevent the same header from being included multiple times in one translation unit.

Let's understand the three directives.

- `#ifndef PEER_IDENTITY_HPP`: means if this macro has not been defined.
- `#define PEER_IDENTITY_HPP`: defines the macro so subsequent inclusions skip the header contents.
- `#endif`: closes the conditional directive.

Why is this useful?

Imagine that both `main.cpp` and `peer_registry.hpp` include `peer_identity.hpp`. Without protection, including the same definitions multiple times can cause redefinition errors.

Header guards prevent that problem.

You can also use `#pragma once` as a simpler alternative:

```
#pragma once
```

Both approaches are widely used.

## B. The libraries

```
#include <string>
#include <cstdint>
#include <iostream>
```

Each header provides a different capability.

| Header       | What it provides          | Example                |
| ------------ | ------------------------- | ---------------------- |
| `<string>`   | Text strings              | `std::string peer_id;` |
| `<cstdint>`  | Fixed-width integer types | `std::uint16_t port;`  |
| `<iostream>` | Input/output streams      | `std::cout`            |

Why use `std::uint16_t` for the port?

```
std::uint16_t port;
```

It is an unsigned integer type with exactly 16 bits, when that type is available on the platform. Its range is 0–65535, which covers TCP and UDP port numbers.

However, port `0` has a special meaning when binding a socket: the operating system can choose an available port. For a peer's advertised listening port, you would normally store the actual assigned port.

## C. Defining the structure

```
struct PeerIdentity {
    std::string peer_id;
    std::string ip_address;
    std::uint16_t port;
};
```

This defines a custom data type named `PeerIdentity`.

It contains three member variables:

```
std::string peer_id;
std::string ip_address;
std::uint16_t port;
```

Think of it as a record holding related information.

For example:

```
PeerIdentity peer;

peer.peer_id = "peer-001";
peer.ip_address = "192.168.1.10";
peer.port = 5001;
```

Now `peer` contains all three values.

Why `struct` instead of `class`?

In C++, the main difference is the default access level:

- `struct`: members are `public` by default.
- `class`: members are `private` by default.

For a simple object that groups data, `struct` is convenient. You can also use a `class` if you want to hide the data and control access to it.

## D. The constructor

Your code:

```
PeerIdentity(
    const std::string& id,
    const std::string& ip,
    std::uint16_t p
)
    : peer_id(id),
      ip_address(ip),
      port(p) {}
```

The constructor initializes the object's members when you create it.

For example:

```
PeerIdentity peer(
    "peer-001",
    "192.168.1.10",
    5001
);
```

The values are assigned as follows:

`id`

`peer_id = "peer-001"`

`ip`

`ip_address = "192.168.1.10"`

`p`

`port = 5001`

### What does `: peer_id(id), ip_address(ip), port(p)` mean?

This is called a member initializer list.

```
: peer_id(id),
  ip_address(ip),
  port(p)
```

It initializes the members directly rather than assigning to them later in the constructor body.

Compare the two approaches.

Using an initializer list:

```
PeerIdentity(const std::string& id,
             const std::string& ip,
             std::uint16_t p)
    : peer_id(id), ip_address(ip), port(p) {}
```

Using assignments inside the body:

```
PeerIdentity(const std::string& id,
             const std::string& ip,
             std::uint16_t p) {
    peer_id = id;
    ip_address = ip;
    port = p;
}
```

Both work here, but the initializer list is generally preferred. It directly initializes the members and is required for certain member types, such as references and `const` members.

What about `const std::string& id`?

- `const` means the constructor cannot modify the string through this reference.
- `&` means it receives a reference instead of making a copy just to pass the argument into the function.
- `id` is the parameter name.

The constructor copies the string into the object's own `peer_id` member. The object does not depend on the parameter remaining alive.

## E. The `endpoint()` method

```
std::string endpoint() const {
    return ip_address + ":" + std::to_string(port);
}
```

This method combines the IP address and port into a single string.

For example:

```
PeerIdentity peer("peer-001", "192.168.1.10", 5001);

std::cout << peer.endpoint();
```

Output:

```
192.168.1.10:5001
```

Let's examine the parts:

- `std::string`: the return type.
- `endpoint()`: the method name.
- `const`: promises not to modify the object's members through this method.
- `std::to_string(port)`: converts the integer `5001` into the text `"5001"`.
- `+ ":" +`: concatenates the address, separator, and port.

The `const` after the parentheses is important. It allows you to call the method on a `const PeerIdentity` object.

## F. The `display()` method

```
void display() const {
    std::cout << "Peer ID: " << peer_id << '\n';
    std::cout << "Address: " << endpoint() << '\n';
}
```

This method prints the peer's information.

```
peer.display();
```

Output:

```
Peer ID: peer-001
Address: 192.168.1.10:5001
```

Here:

- `void` means the function does not return a value.
- `std::cout` writes text to the console.
- `'\n'` inserts a newline.
- `const` indicates that the method does not modify the peer's state.

# 3. Your main question: Why split code between `.hpp` and `.cpp`?

First, your current `PeerIdentity` code does not split the class across two files. The entire structure, constructor, and both methods are defined inside the header.

C++ allows this, and for a small data structure, it is perfectly reasonable.

However, in larger projects, we often separate the declaration from the implementation.

Think of it like this:

- `.hpp` tells other parts of the program what exists and how to use it.
- `.cpp` contains how the functions work.

The `.hpp` file is not the implementation's replacement. It is the interface that other source files can include.

## Example: splitting `PeerIdentity` into two files

`peer_identity.hpp`

Declaration — what the type offers

`peer_identity.cpp`

Implementation — how the methods work

### File 1 — `peer_identity.hpp`

```

#ifndef PEER_IDENTITY_HPP
#define PEER_IDENTITY_HPP

#include <cstdint>
#include <string>

struct PeerIdentity {
    std::string peer_id;
    std::string ip_address;
    std::uint16_t port;

    PeerIdentity(
        const std::string& id,
        const std::string& ip,
        std::uint16_t p
    );

    std::string endpoint() const;

    void display() const;
};

#endif

```

Notice what changed.

The constructor is now only declared:

```
PeerIdentity(
    const std::string& id,
    const std::string& ip,
    std::uint16_t p
);
```

There is no function body.

Likewise:

```
std::string endpoint() const;
void display() const;
```

These declarations tell the compiler the method names, return types, parameters, and whether the methods are `const`.

### File 2 — `peer_identity.cpp`

```

#include "peer_identity.hpp"

#include <iostream>
#include <string>

PeerIdentity::PeerIdentity(
    const std::string& id,
    const std::string& ip,
    std::uint16_t p
)
    : peer_id(id),
      ip_address(ip),
      port(p) {}

std::string PeerIdentity::endpoint() const {
    return ip_address + ":" + std::to_string(port);
}

void PeerIdentity::display() const {
    std::cout << "Peer ID: " << peer_id << '\n';
    std::cout << "Address: " << endpoint() << '\n';
}

```

There is one new syntax you need to understand:

```
std::string PeerIdentity::endpoint() const
```

The `PeerIdentity::` part is the scope resolution operator. It tells C++ that `endpoint()` is a member function belonging to `PeerIdentity`.

Similarly:

```
PeerIdentity::PeerIdentity(...)
```

defines the constructor belonging to `PeerIdentity`.

Because these definitions are outside the structure's braces, we need to qualify the member names with `PeerIdentity::`.

## 4. How do you compile the split version?

Your directory:

```
peer_identity_lab/
├── peer_identity.hpp
├── peer_identity.cpp
└── main.cpp
```

Your `main.cpp` can be:

```
#include "peer_identity.hpp"

int main() {
    PeerIdentity peer(
        "peer-001",
        "192.168.1.10",
        5001
    );

    peer.display();

    return 0;
}
```

Compile both `.cpp` files together:

```
g++ -std=c++17 -Wall -Wextra \
    main.cpp peer_identity.cpp \
    -o peer_identity
```

Run:

```
./peer_identity
```

Output:

```
Peer ID: peer-001
Address: 192.168.1.10:5001
```

Important: You generally do not compile a `.hpp` file separately. You compile the `.cpp` source files that include it and contain the necessary function definitions.

# 5. Why is this separation useful in your P2P project?

Suppose your project grows to include:

```
p2p/
├── peer_identity.hpp
├── peer_identity.cpp
├── peer_registry.hpp
├── peer_registry.cpp
├── peer_connection.hpp
├── peer_connection.cpp
├── protocol.hpp
├── protocol.cpp
└── main.cpp
```

Each module has a distinct responsibility:

| File                  | Responsibility                           |
| --------------------- | ---------------------------------------- |
| `peer_identity.hpp`   | Describes the peer identity interface    |
| `peer_identity.cpp`   | Implements identity-related methods      |
| `peer_registry.hpp`   | Declares the peer registry interface     |
| `peer_registry.cpp`   | Implements registration and lookup       |
| `peer_connection.hpp` | Declares connection operations           |
| `peer_connection.cpp` | Implements TCP communication             |
| `protocol.hpp`        | Declares protocol messages               |
| `protocol.cpp`        | Implements message encoding and decoding |

This organization makes your code easier to maintain, test, and extend.

For example, if you change how an endpoint string is formatted, you can edit `peer_identity.cpp` without changing the interface in `peer_identity.hpp`.

There is also a build advantage: source files can be compiled separately and linked together. With a well-organized build system, changing one implementation does not require recompiling every unrelated source file.

One caveat: changing a header can still require recompiling source files that include it.

## 6. When should you use each approach?

| Situation                                    | Recommended approach                      |
| -------------------------------------------- | ----------------------------------------- |
| Small structure with simple methods          | Define methods inside `.hpp`              |
| Larger class with substantial implementation | Declare in `.hpp`, define in `.cpp`       |
| Template class or function                   | Usually keep the definition in the header |
| Class used by many source files              | A clear public header is useful           |
| Implementation you want to hide from callers | Put method definitions in `.cpp`          |

One technical detail: methods defined inside a class definition are implicitly `inline`. This allows the same definition to appear in multiple translation units when the One Definition Rule's requirements are satisfied.

For your current `PeerIdentity` structure, either approach is correct. I recommend learning the split version because your P2P project will eventually contain several classes and network-related modules.

## 7. Test your understanding

Question 1: What does `PeerIdentity::endpoint()` mean?

It creates a new peer.

It identifies `endpoint()` as a method belonging to `PeerIdentity`.

It creates a TCP connection.

Question 2: What is the primary role of the `.hpp` file in the split version?

To declare the class members and method signatures.

To run the entire application.

To store all runtime peer information.

Question 3: Why do we use `const` in `endpoint() const`?

It makes the method return a constant string.

It prevents the method from modifying the object's state through the method.

It makes the method execute faster in every case.

Check my answers

Once you understand these concepts, the next step is to implement `PeerRegistry` using the same `.hpp` and `.cpp` separation, then connect it to your TCP networking code.

----------------------------------------------------------------
# Understanding `PeerRegistry` in C++

Your `PeerRegistry` class is responsible for storing, searching, and managing peers in your P2P file-sharing application.

While `PeerIdentity` represents a single peer, `PeerRegistry` manages a collection of them.

## 1. What is a Peer Registry?

Imagine your P2P network contains four computers:

Peer A maintains a registry of the peers it knows.

For example, Peer A's registry might contain:

| Peer ID | IP address   | Port |
| ------- | ------------ | ---- |
| peer-B  | 192.168.1.11 | 5002 |
| peer-C  | 192.168.1.12 | 5003 |
| peer-D  | 192.168.1.13 | 5004 |

The registry exists in memory and provides methods to manipulate this information. It does not automatically establish TCP connections.

## 2. Understanding the libraries

```
#include "peer_identity.hpp"

#include <unordered_map>
#include <vector>
#include <string>
#include <utility>
```

| Library               | Purpose                                |
| --------------------- | -------------------------------------- |
| `"peer_identity.hpp"` | Provides your `PeerIdentity` structure |
| `<unordered_map>`     | Stores peers using their IDs as keys   |
| `<vector>`            | Holds a list of peers                  |
| `<string>`            | Provides `std::string`                 |
| `<utility>`           | Provides utilities such as `std::pair` |

The most important container here is `std::unordered_map`.

## 3. Understanding `std::unordered_map`

Your code:

```
private:
    std::unordered_map<std::string, PeerIdentity> peers;
```

An `unordered_map` stores key-value pairs.

In your application:

- Key: `std::string` containing the peer ID.
- Value: `PeerIdentity` containing information about the peer.

Conceptually, the map looks like this:

`std::unordered_map<std::string, PeerIdentity>`

Key

Value

peer-001

192.168.1.10:5001

peer-002

192.168.1.11:5002

peer-003

192.168.1.12:5003

Why use `unordered_map` instead of `vector`?

Because you frequently need to search for a peer by ID.

| Operation                | `unordered_map` | `vector`              |
| ------------------------ | --------------- | --------------------- |
| Search by peer ID        | O(1) average    | O(n)                  |
| Insert a peer            | O(1) average    | O(1) amortized at end |
| Remove by peer ID        | O(1) average    | O(n)                  |
| Preserve insertion order | No              | Yes                   |

`unordered_map` uses a hash table internally. Its average lookup time is constant, although the worst case can be O(n).

# 4. Understanding `addPeer()`

Your code:

```
bool addPeer(const PeerIdentity& peer) {
    auto result = peers.emplace(peer.peer_id, peer);
    return result.second;
}
```

This function adds a new peer to the registry.

### A. The parameter

```
const PeerIdentity& peer
```

This means:

- `PeerIdentity`: the parameter type.
- `&`: pass the object by reference, avoiding an unnecessary parameter copy.
- `const`: the function cannot modify the object through that reference.

For example:

```
PeerIdentity p("peer-001", "192.168.1.10", 5001);

registry.addPeer(p);
```

### B. What does `emplace()` do?

```
auto result = peers.emplace(peer.peer_id, peer);
```

`emplace()` attempts to insert an entry into the map.

It associates the key `peer.peer_id` with the corresponding `PeerIdentity` object.

The result of `emplace()` is a `std::pair` containing two values:

```
std::pair<iterator, bool>
```

- `result.first`: an iterator pointing to the inserted or already-existing element.
- `result.second`: a Boolean indicating whether a new element was inserted.

Example:

```
bool first = registry.addPeer(p);   // true
bool second = registry.addPeer(p);  // false
```

The second insertion fails because the ID already exists.

### Interactive example

Simulate `addPeer()`

CURRENT MAP

peer-001

Add peer-002Add peer-001Reset

Result

The registry initially contains peer-001.

# 5. Understanding `findPeer()`

Your code:

```
const PeerIdentity* findPeer(
    const std::string& peer_id
) const {
    auto it = peers.find(peer_id);

    if (it == peers.end()) {
        return nullptr;
    }

    return &it->second;
}
```

This is one of the most important functions in the registry.

### A. What is an iterator?

```
auto it = peers.find(peer_id);
```

An iterator is an object that refers to a position in a container.

For `unordered_map`, the iterator gives access to a key-value pair.

```
it->first   // Peer ID (key)
it->second  // PeerIdentity object (value)
```

For example:

```
auto it = peers.find("peer-002");
```

If `peer-002` exists, `it` refers to its map entry.

### B. What does `peers.end()` mean?

```
if (it == peers.end()) {
    return nullptr;
}
```

`end()` returns an iterator representing the position past the last element.

It does not refer to an actual element.

If `find()` fails, it returns `end()`.

Therefore:

```
it == peers.end()
```

means that the peer was not found.

### C. Why return `nullptr`?

The return type is:

```
const PeerIdentity*
```

This means the function returns a pointer to a constant `PeerIdentity`.

When the peer does not exist, `nullptr` represents the absence of a valid object.

When the peer exists:

```
return &it->second;
```

Here:

- `it->second` accesses the stored `PeerIdentity`.
- `&` obtains its memory address.
- `return` sends that pointer back to the caller.

Example:

```
const PeerIdentity* peer = registry.findPeer("peer-002");

if (peer != nullptr) {
    peer->display();
}
```

The `->` operator accesses a member through a pointer.

It is equivalent to:

```
(*peer).display();
```

Because the returned pointer is `const`, callers cannot modify the stored peer through it.

Important: This pointer is non-owning. It becomes invalid if the referenced entry is erased or the registry is destroyed. In concurrent code, additional synchronization is necessary.

# 6. Understanding `removePeer()`

```
bool removePeer(const std::string& peer_id) {
    return peers.erase(peer_id) > 0;
}
```

The `erase()` method removes an element using its key.

For example:

```
peers.erase("peer-002");
```

Because keys are unique in an `unordered_map`, `erase(key)` returns either:

- `1`: an entry was removed.
- `0`: no entry had that key.

Therefore:

```
return peers.erase(peer_id) > 0;
```

converts that result into a Boolean.

```
bool removed = registry.removePeer("peer-002");
```

`removed` will be `true` if the peer existed and was removed.

This only removes information from the registry. It does not close the peer's network connection.

# 7. Understanding `getAllPeers()`

Your code:

```
std::vector<PeerIdentity> getAllPeers() const {
    std::vector<PeerIdentity> result;
    result.reserve(peers.size());

    for (const auto& entry : peers) {
        result.push_back(entry.second);
    }

    return result;
}
```

This function creates a vector containing copies of all registered peers.

### A. Create an empty vector

```
std::vector<PeerIdentity> result;
```

A `vector` is a dynamic array.

Unlike a fixed-size C-style array, it can grow as elements are added.

### B. Reserve memory

```
result.reserve(peers.size());
```

Suppose your registry contains 100 peers.

This requests enough capacity for at least 100 `PeerIdentity` objects.

It helps avoid repeated memory reallocations as the vector grows.

Notice the distinction:

```
result.reserve(100); // capacity for 100 elements
result.resize(100);  // makes the vector contain 100 elements
```

`reserve()` does not add elements.

### C. Loop through the map

```
for (const auto& entry : peers) {
    result.push_back(entry.second);
}
```

This is a range-based `for` loop.

For each map entry:

- `entry.first` is the key.
- `entry.second` is the stored `PeerIdentity`.
- `push_back()` copies that identity into the vector.

The `const auto&` avoids copying the map entry during iteration.

### D. Return the vector

```
return result;
```

The caller receives a vector of peer identities.

Example:

```
std::vector<PeerIdentity> allPeers = registry.getAllPeers();

for (const auto& peer : allPeers) {
    peer.display();
}
```

The order of peers is unspecified because the original container is an `unordered_map`.

# 8. Understanding `size()` and `empty()`

These two methods provide information about the registry.

```
std::size_t size() const {
    return peers.size();
}
```

`size()` returns the number of registered peers.

```
std::cout << registry.size();
```

And:

```
bool empty() const {
    return peers.empty();
}
```

`empty()` returns `true` when the map contains no elements.

```
if (registry.empty()) {
    std::cout << "No peers registered\n";
}
```

The `const` at the end of both methods means they cannot modify the registry through `this`.

# 9. Splitting `PeerRegistry` into `.hpp` and `.cpp`

Since your project is growing, this class can also be separated into declarations and implementations.

## `peer_registry.hpp`

```

#ifndef PEER_REGISTRY_HPP
#define PEER_REGISTRY_HPP

#include "peer_identity.hpp"

#include <unordered_map>
#include <vector>
#include <string>
#include <cstddef>

class PeerRegistry {
private:
    std::unordered_map<std::string, PeerIdentity> peers;

public:
    bool addPeer(const PeerIdentity& peer);

    const PeerIdentity* findPeer(
        const std::string& peer_id
    ) const;

    bool removePeer(const std::string& peer_id);

    std::vector<PeerIdentity> getAllPeers() const;

    std::size_t size() const;

    bool empty() const;
};

#endif

```

## `peer_registry.cpp`

```

#include "peer_registry.hpp"

bool PeerRegistry::addPeer(const PeerIdentity& peer) {
    auto result = peers.emplace(peer.peer_id, peer);
    return result.second;
}

const PeerIdentity* PeerRegistry::findPeer(
    const std::string& peer_id
) const {
    auto it = peers.find(peer_id);

    if (it == peers.end()) {
        return nullptr;
    }

    return &it->second;
}

bool PeerRegistry::removePeer(const std::string& peer_id) {
    return peers.erase(peer_id) > 0;
}

std::vector<PeerIdentity> PeerRegistry::getAllPeers() const {
    std::vector<PeerIdentity> result;
    result.reserve(peers.size());

    for (const auto& entry : peers) {
        result.push_back(entry.second);
    }

    return result;
}

std::size_t PeerRegistry::size() const {
    return peers.size();
}

bool PeerRegistry::empty() const {
    return peers.empty();
}

```

Notice the `PeerRegistry::` prefix. It identifies the class that owns each method.

If your `PeerIdentity` constructor is also implemented in `peer_identity.cpp`, your build command must include all three source files:

```
g++ -std=c++17 -Wall -Wextra \
    main.cpp peer_registry.cpp peer_identity.cpp \
    -o p2p_app
```

## 10. Summary of the entire class

| Method          | Purpose                             | Return type                 |
| --------------- | ----------------------------------- | --------------------------- |
| `addPeer()`     | Add a new peer                      | `bool`                      |
| `findPeer()`    | Search for a peer by ID             | `const PeerIdentity*`       |
| `removePeer()`  | Delete a peer                       | `bool`                      |
| `getAllPeers()` | Get a snapshot of all peers         | `std::vector<PeerIdentity>` |
| `size()`        | Count registered peers              | `std::size_t`               |
| `empty()`       | Check whether the registry is empty | `bool`                      |

The central idea is that `PeerIdentity` describes one peer, and `PeerRegistry` manages many peers using a hash table.

In your P2P file-sharing system, the registry is the foundation for discovering peers, locating their network endpoints, and deciding which peer to contact for a file transfer.