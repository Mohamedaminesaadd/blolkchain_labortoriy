# What is RPC in Bitcoin?

RPC stands for Remote Procedure Call. It allows one program to request an operation from another program, as if it were calling a function.

In your Bitcoin Core lab, RPC lets you control your Bitcoin node using commands from a terminal, Python program, or another application.

## 1. How Bitcoin RPC works

Your terminal

`bitcoin-cli`

RPC interface

Request and response over HTTP

Bitcoin Core (`bitcoind`)

Executes the requested operation

For example, when you execute:

```
bitcoin-cli -regtest getblockchaininfo
```

The process is:

1. `bitcoin-cli` constructs an RPC request.
2. It sends the request to the Bitcoin Core RPC server.
3. `bitcoind` executes `getblockchaininfo`.
4. The node returns the result, typically encoded as JSON.
5. `bitcoin-cli` displays the result in your terminal.

## 2. Common Bitcoin RPC commands

| Command             | What it does                         |
| ------------------- | ------------------------------------ |
| `getblockchaininfo` | Returns blockchain information       |
| `getpeerinfo`       | Shows connected P2P peers            |
| `getrawmempool`     | Lists unconfirmed transactions       |
| `getnewaddress`     | Generates a wallet receiving address |
| `getbalance`        | Returns the wallet balance           |
| `sendtoaddress`     | Sends bitcoin to an address          |
| `generatetoaddress` | Mines blocks in regtest              |

For example:

```
bitcoin-cli -regtest getpeerinfo
```

This uses RPC to ask your local node for information about its P2P connections.

Notice the distinction: RPC is how you communicate with your own node's API; P2P is how your node communicates with other Bitcoin nodes.

## 3. RPC versus P2P

| Feature              | RPC                                | P2P                         |
| -------------------- | ---------------------------------- | --------------------------- |
| Main purpose         | Control or query a node            | Communicate between nodes   |
| Typical participants | Application ↔ Bitcoin Core         | Bitcoin node ↔ Bitcoin node |
| Example              | `getblockchaininfo`                | Transaction propagation     |
| Protocol             | HTTP with JSON-RPC in Bitcoin Core | Bitcoin P2P protocol        |
| Used by              | `bitcoin-cli`, Python apps         | Connected Bitcoin peers     |

## 4. Can Python use Bitcoin RPC?

Yes. Your Streamlit Bitcoin wallet dashboard can use RPC to interact with Bitcoin Core.

For example, using Python's `requests` library:

```
import requestsfrom requests.auth import HTTPBasicAuthurl = "http://127.0.0.1:18443/"auth = HTTPBasicAuth("your_rpc_user", "your_rpc_password")response = requests.post(    url,    auth=auth,    json={        "jsonrpc": "2.0",        "id": "python",        "method": "getblockchaininfo",        "params": []    },    timeout=10)response.raise_for_status()print(response.json())
```

This example assumes your regtest node uses the default RPC port, `18443`, and that you configure the credentials appropriately. Bitcoin Core can also use cookie authentication.

Security note: Never expose the RPC interface to the public internet or hardcode real credentials in your source code.

### Remember this

- RPC: You ask your node to do something or return information.
- P2P: Your node exchanges information with other nodes.
- Blockchain: The shared history of confirmed blocks and transactions.
---------------------------------------------------------------
# Bitcoin RPC: the complete procedure

Yes, RPC uses a communication protocol, just as SSH does, but RPC and SSH have different purposes.

In your Bitcoin Core lab with Amine, Omar, and Sara, understanding RPC means understanding how a terminal command travels to a Bitcoin node, how the node executes it, and how the answer comes back.

Let's start from the network fundamentals.

## 1. Is RPC a protocol like SSH?

First, distinguish three concepts:

- RPC (Remote Procedure Call): a mechanism for requesting that another program execute an operation.
- JSON-RPC: an application-level protocol that defines how requests and responses are structured using JSON.
- SSH (Secure Shell): a protocol for securely accessing and controlling a remote computer, typically through an encrypted terminal session.

Bitcoin Core's RPC interface uses HTTP for transport and JSON-RPC-style messages for requests and responses. It is not the same protocol as SSH.

| Property             | Bitcoin RPC                                                 | SSH                                      |
| -------------------- | ----------------------------------------------------------- | ---------------------------------------- |
| Purpose              | Query or control Bitcoin Core                               | Securely access a remote machine         |
| Application protocol | JSON-RPC over HTTP                                          | SSH protocol                             |
| Default TCP port     | `8332` mainnet; `18443` regtest                             | `22`                                     |
| Typical client       | `bitcoin-cli`, Python                                       | `ssh`                                    |
| Typical response     | JSON data                                                   | Terminal session or command output       |
| Security             | RPC authentication; HTTP itself is not encrypted by default | Encrypted connection with authentication |

Ports are configurable. These are the usual defaults.

## 2. What exactly happens when you execute an RPC command?

Suppose you run this on Amine's Ubuntu machine:

```
bitcoin-cli -regtest getblockchaininfo
```

The complete flow is:

1\. Terminal

You type the command

2\. bitcoin-cli

Parses the command and prepares an RPC request

3\. HTTP + TCP + IP

Transports the request to the node's RPC endpoint

4\. Bitcoin Core RPC server

Authenticates and dispatches the method

5\. Bitcoin Core

Reads blockchain state and builds the result

6\. Response

JSON response returns to bitcoin-cli and is displayed

The request and response use the same connection in the ordinary HTTP request-response exchange.

One important detail: in the command above, `bitcoin-cli` normally communicates with the Bitcoin Core process running on the same computer. If the node is remote, the client must be configured to reach that node's RPC endpoint.

## 3. The protocol stack: what happens at each layer?

When an RPC request travels through a network, it uses several layers. RPC is not itself the transport mechanism.

Application

JSON-RPC + HTTP

Defines the method, parameters, HTTP request, and response.

Example: `getblockchaininfo`

Transport

TCP

Provides a reliable, ordered byte stream between the client and server.

Example: destination port `18443` in regtest

Internet

IP

Routes packets between the client machine and the server machine.

Network access

Ethernet, Wi-Fi, virtual network, etc.

Carries packets across the local network link.

For a typical Bitcoin Core RPC call, the data travels down these layers at the client and back up these layers at the server. The response follows the reverse path.

## 4. What does an RPC request actually look like?

Consider this command:

```
bitcoin-cli -regtest getblockchaininfo
```

### Step 1 — The client prepares the request

Conceptually, the request body contains information like this:

```
{
  "jsonrpc": "2.0",
  "id": "example",
  "method": "getblockchaininfo",
  "params": []
}
```

This is an illustrative JSON-RPC-style request. Exact fields and behavior depend on the Bitcoin Core version and client; `bitcoin-cli` handles the details for you.

The fields mean:

- `method`: the operation to execute.
- `params`: arguments supplied to that operation.
- `id`: identifies the request so the response can be matched to it.
- `jsonrpc`: identifies the JSON-RPC version when that field is used.

### Step 2 — The client sends an HTTP request

The HTTP request is conceptually similar to:

```
POST / HTTP/1.1
Host: 127.0.0.1:18443
Content-Type: application/json
Authorization: Basic <credentials>

{"method":"getblockchaininfo","params":[],"id":"example"}
```

The `Authorization` header represents authentication; actual credentials should never be displayed or shared. Bitcoin Core's cookie authentication is commonly used by `bitcoin-cli`.

The HTTP message is transmitted over a TCP connection. The request is not sent directly to the P2P network.

### Step 3 — Bitcoin Core receives the request

The server performs several operations:

1. Receives the HTTP request.
2. Checks the RPC authentication credentials.
3. Parses the request body.
4. Identifies the method `getblockchaininfo`.
5. Checks whether the method and its parameters are valid.
6. Executes the corresponding RPC handler.

If authentication fails, the server rejects the request. If the method or parameters are invalid, it can return an error.

### Step 4 — The node executes the method

The method reads relevant internal state, such as:

- Current chain and network.
- Current block height.
- Best block hash.
- Difficulty.
- Synchronization information.

A read-only method such as `getblockchaininfo` does not create a transaction or mine a block.

### Step 5 — The server returns the response

A simplified response could look like this:

```
{
  "result": {
    "chain": "regtest",
    "blocks": 108,
    "bestblockhash": "example_hash"
  },
  "error": null,
  "id": "example"
}
```

The values are illustrative, not the actual output of your node.

Bitcoin Core returns the response over HTTP, TCP delivers the bytes to the client, and `bitcoin-cli` formats the result for your terminal.

## 5. Which port does Bitcoin RPC use?

| Network   | Default RPC port | Default P2P port |
| --------- | ---------------- | ---------------- |
| Mainnet   | `8332`           | `8333`           |
| Testnet 3 | `18332`          | `18333`          |
| Regtest   | `18443`          | `18444`          |

The important distinction is that the RPC port and P2P port serve different interfaces.

- RPC port `18443`: applications can query or control a regtest node.
- P2P port `18444`: regtest nodes can exchange Bitcoin network messages.

These ports are defaults and can be changed in the configuration.

For example, check the node's listening ports on Ubuntu:

```
sudo ss -lntp
```

To inspect the RPC-related configuration:

```
cat ~/.bitcoin/bitcoin.conf
```

If you use a custom data directory, inspect the configuration associated with that directory instead.

## 6. RPC versus SSH versus Bitcoin P2P

[The Linux command line for beginners - Ubuntu Desktop documentation](https://images.openai.com/static-rsc-4/TWruKNqYQumj6tFWCGD_KsTWJyjrJlhNxj9ugRN_86MnKsTNHpwk_DmgDaFGfFdUMB09yzXjoM7V1EqXSg-gi7b0a0e20tcA7JJMf1HDDOnd_EGOZ2LpaQT2sZOi4_d-5_-9TjPD4fbow_PAhALicZpBjXxKB3Epdblzp6q1G0U?purpose=inline)

SSH — remote computer access

```
ssh user@192.168.122.101
```

You authenticate to a remote machine and can open a shell to execute commands.

[What’s new in HTTPie for Terminal 3.0 - DEV Community](https://images.openai.com/static-rsc-4/n-vHrSfiBs5I2Bm0j600INuCOoZdsamq17-x2Yu9KyWqBW6PProRNKs8po50fAZjsD3FrsxdbjvncjDh7b6D4arCk6d0q2AjwRkwDo56IwyDYVW46mR8tKxmjy79-h2G5mL5yPdsHmkixURquSR5WgeWAnWuhiG1jfBzeP5_BVU?purpose=inline)

RPC — application control

```
bitcoin-cli -regtest getpeerinfo
```

You request a specific operation from Bitcoin Core and receive structured data.

[Peer-to-Peer (P2P) Architecture | Software System Design](https://images.openai.com/static-rsc-4/pU4vgEc0HrfzN89onfUV3SyjNqG6ZiJf7Zg3JDWou8ZS5KSRyNB_LVQLKlzZrTACizmfi-zQsE87bnzYN4Rjt834voqFypob5j3wlAajCFRDB_msfV9V9URcdSBpB-UDDNRobFDnWZ6X7JbCu-LHEVixyye9AEHQ9kcoTjd7udY?purpose=inline)

P2P — node-to-node communication

Bitcoin nodes exchange transactions, blocks, and other network messages with their peers.

SSH can be used to access a remote computer and run `bitcoin-cli` there. RPC can also be called remotely if the node is configured to permit that access. These are separate mechanisms, and you do not need SSH for ordinary local RPC calls.

## 7. Test the complete procedure in your lab

On Amine's node, run:

```
bitcoin-cli -regtest getblockchaininfo
bitcoin-cli -regtest getnetworkinfo
bitcoin-cli -regtest getpeerinfo
```

Then compare the results with the other nodes.

To see the difference between RPC and P2P in your lab:

- Use `getpeerinfo` to inspect peer connections through RPC.
- Use `getrawmempool` to query which unconfirmed transactions a node currently knows about.
- Observe the P2P connections to understand how the nodes exchange data.

The central idea: RPC defines how your application asks Bitcoin Core to perform an operation. HTTP carries the request, TCP transports it reliably, IP routes it, and Bitcoin Core executes the operation and returns a response.


# API vs RPC: What's the Difference?

The most important point is that API and RPC are not opposites. An API is an interface that lets software interact with other software, while RPC is a communication mechanism that allows a program to request an operation from another program.

An RPC interface is one type of API.

## 1. Main comparison

| Feature             | API                                   | RPC                                                                                |
| ------------------- | ------------------------------------- | ---------------------------------------------------------------------------------- |
| Full name           | Application Programming Interface     | Remote Procedure Call                                                              |
| Meaning             | Defines how software interacts        | A mechanism for requesting remote operations                                       |
| Main purpose        | Expose functionality or data          | Call a function or method on another system                                        |
| Communication       | Can use HTTP, libraries, events, etc. | Can use HTTP, TCP, gRPC, and other transports                                      |
| Examples            | REST API, GraphQL API, library API    | JSON-RPC, XML-RPC, gRPC                                                            |
| Data format         | Depends on the API                    | Depends on the RPC protocol                                                        |
| Network required?   | Not always                            | Remote RPC normally involves communication between processes, often over a network |
| Typical interaction | Depends on the interface              | Invoke a named operation with parameters and receive a result                      |

Remember: API describes the interface; RPC describes a way of invoking operations remotely.

## 2. REST API vs RPC

Let's compare two ways to interact with a server.

## A. REST API

You interact with resources using HTTP methods and URLs.

HTTP request

`GET /users/42`

Meaning

Retrieve the user identified by `42`.

The URL identifies a resource, and the HTTP method indicates the intended action.

## B. RPC

You request that the server execute a named operation.

Example JSON-RPC request

```
{
  "method": "getUser",
  "params": [42],
  "id": 1
}
```

The method identifies the operation, and the parameters supply its inputs.

Both can use HTTP and JSON. The difference is mainly how the interface models the interaction, not necessarily the underlying network transport.

## 3. How this applies to Bitcoin Core

In your Bitcoin lab, you use `bitcoin-cli` to communicate with Bitcoin Core through its RPC interface.

For example:

```
bitcoin-cli -regtest getblockchaininfo
```

This command asks Bitcoin Core to execute the `getblockchaininfo` RPC method.

Conceptually, the request is:

```
{
  "method": "getblockchaininfo",
  "params": [],
  "id": 1
}
```

The actual client handles the HTTP request, authentication, and response parsing.

Now compare that with a hypothetical REST-style interface:

```
GET /blockchain/info
```

Both interfaces could return blockchain information, but Bitcoin Core exposes this operation through its RPC interface rather than that hypothetical REST endpoint.

## 4. How the protocols fit together

Application

Your Python wallet dashboard

API interface

The operations available to the application

RPC protocol

JSON-RPC request and response format

HTTP → TCP → IP

Transport and network delivery

Bitcoin Core

Executes the requested operation

This is a conceptual stack: RPC is itself an API style, not necessarily a separate layer below every API. HTTP carries the request, TCP transports the bytes, and IP routes the packets.

## 5. What about GraphQL and gRPC?

| Technology | What it is                                                  |
| ---------- | ----------------------------------------------------------- |
| REST       | An architectural style commonly used for HTTP APIs          |
| GraphQL    | A query language and execution model for APIs               |
| JSON-RPC   | A protocol for invoking named methods using JSON            |
| XML-RPC    | An RPC protocol that encodes requests using XML             |
| gRPC       | An RPC framework commonly using Protocol Buffers and HTTP/2 |

These technologies solve related but different problems. For example, GraphQL lets clients request specific data shapes, whereas gRPC commonly defines typed service methods and messages.

## 6. Which should you use?

- REST: A good default for conventional web services organized around resources.
- GraphQL: Useful when clients need flexible queries across related data.
- JSON-RPC: Useful when you want a simple method-call interface, as in Bitcoin Core.
- gRPC: Useful for strongly typed service-to-service communication, particularly in distributed systems.

For your Bitcoin wallet dashboard, your Streamlit application can call Bitcoin Core's JSON-RPC interface to get balances, generate addresses, and submit transactions.

Final takeaway: An API is the interface; RPC is one way to design that interface; JSON-RPC specifies a request-and-response protocol; HTTP and TCP can carry those messages across a network.


--------------------------------------------------------------------------------------------------------------------------------------------------------
You're asking exactly the right question: if REST API and RPC both let Machine B use a function implemented on Machine A, why do we need RPC?

At a high level, both allow remote communication. The key difference is how they model the interaction.

- RPC: “Execute this operation on the remote machine.”
- REST: “Access or manipulate this resource on the remote machine.”

These are conceptual differences, not absolute rules. REST APIs can trigger operations, and RPC systems can exchange data about resources.

## 1. The same application implemented in three ways

Suppose Machine A runs a service that adds two numbers.

Local Python function

```
result = add(10, 20)
```

Direct function call inside the same process.

RPC

```
result = server.add(10, 20)
```

Calls a remote procedure through an RPC client or proxy.

REST API

```
response = requests.post(    "http://machine-a:8000/add",    json={"a": 10, "b": 20})result = response.json()["result"]
```

Sends an HTTP request to an endpoint and parses its response.

All three can produce the same result: `30`.

So, what changes? The calling model, protocol conventions, data representation, tooling, and sometimes performance.

## 2. The real difference: RPC is a communication model, REST is an architectural style

| Aspect            | RPC                                              | REST                                            |
| ----------------- | ------------------------------------------------ | ----------------------------------------------- |
| Main abstraction  | Procedures / operations                          | Resources                                       |
| Typical request   | `calculate(10, 20)`                              | `GET /calculations/123` or `POST /calculations` |
| Interface         | Named remote methods                             | Resource URLs and standardized HTTP methods     |
| Data format       | Depends on RPC system: JSON, XML, Protobuf, etc. | Often JSON, but not limited to it               |
| Transport         | Depends on implementation                        | Usually HTTP                                    |
| Client experience | Often resembles a local method call              | Explicit HTTP request and response              |
| Typical use       | Internal services, commands, streaming           | Web applications, public APIs, CRUD             |

REST's HTTP methods have defined semantics; for example, `GET` retrieves a resource representation, while `POST` commonly submits data or triggers a state change.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://developer.mozilla.org\&sz=32)

MDN

+1



## 3. Why use RPC if REST already works?

The special value becomes clearer when your system has many services that need to call each other.

Imagine your HPIS project has these services:

- ECG classification service
- Sleep analysis service
- Stress detection service
- User management service

The ECG service needs to ask the stress service to classify a signal.

With an RPC framework such as gRPC, you can define a typed service contract:

```
service StressService {
  rpc PredictStress(StressRequest)
      returns (StressResponse);
}
```

A client can then call the generated method:

```
response = stress_client.PredictStress(request)
```

The framework handles message serialization, network communication, and response decoding. With gRPC, Protocol Buffers provide a defined message schema, and HTTP/2 supports streaming and efficient communication between services.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://grpc.io\&sz=32)

gRPC

+1



You could implement the same operation with REST:

```
response = requests.post(    "http://stress-service/predict",    json={"hr": 95, "rmssd": 22.4})
```

Both approaches work. RPC is attractive when you want a strongly defined service interface, generated clients, and efficient communication between backend services.

## 4. The important distinction: RPC does not automatically mean faster

Choose REST when

- You expose a web API to browsers or external developers.
- You want easy testing with `curl`, Postman, or a browser.
- You work mainly with resources such as users, transactions, and reports.

Choose gRPC when

- Backend services make frequent, structured calls to each other.
- You need generated, typed clients across languages.
- You need bidirectional streaming or compact binary messages.

Actual performance depends on message size, serialization, connection reuse, server processing, and network conditions. A well-designed REST API can outperform a poorly designed RPC service.

## 5. One final distinction: RPC is not a single protocol

XML-RPC, JSON-RPC, and gRPC are different implementations of the RPC model. For example:

- XML-RPC: XML messages, commonly over HTTP.
- JSON-RPC: JSON messages with named methods and parameters.
- gRPC: service definitions, Protocol Buffers by default, and HTTP/2.

My recommendation for your learning: implement the same `add(a, b)` operation using both FastAPI (REST) and gRPC in Python. Comparing the client code, message format, service definition, and network traffic will make the distinction concrete.

---------------------------------------------------------------------------------------------------------------------------------------------------------------------
Yes! RPC can be used over the Internet in web development. It allows a web application to request operations from a remote server, just as your Bitcoin wallet dashboard communicates with Bitcoin Core.

However, web developers also commonly use REST APIs and GraphQL APIs.

## 1. How RPC works in a web application

Imagine you build a web application where users can check their Bitcoin wallet balance.

1\. Frontend — Angular / React

User clicks "Check Balance"

2\. Internet — HTTPS

Request and response travel over the network

3\. Backend — FastAPI

Receives the request and calls Bitcoin RPC

4\. Bitcoin Core

Executes `getbalance` and returns the result

There are actually two possible API/RPC interactions here:

- Frontend → Backend: commonly a REST API over HTTPS.
- Backend → Bitcoin Core: JSON-RPC over HTTP, usually on a private machine or network.

The backend should handle Bitcoin RPC credentials. Never expose your Bitcoin Core RPC credentials to browser JavaScript.

## 2. REST API vs RPC in web development

Suppose your frontend wants to retrieve a user's profile.

Option A — REST API

```
GET https://api.example.com/users/42
```

The request identifies a resource: user 42.

Option B — JSON-RPC

```
POST https://api.example.com/rpc
Content-Type: application/json
```

```
{
  "jsonrpc": "2.0",
  "method": "getUser",
  "params": [42],
  "id": 1
}
```

The request identifies an operation: `getUser`.

Both can run over the Internet using HTTPS. The difference is the interface and message convention, not whether the communication is online.

## 3. Where is RPC used in real web development?

| Technology or use case    | How RPC is used                                               |
| ------------------------- | ------------------------------------------------------------- |
| gRPC microservices        | Services invoke methods on other services                     |
| Blockchain applications   | Applications call node methods through JSON-RPC               |
| Internal backend services | One service requests an operation from another                |
| Distributed systems       | Components communicate through remote procedure calls         |
| Real-time systems         | RPC can complement WebSockets for request-response operations |

For example, gRPC is frequently used for communication between backend services, while REST is common for public web APIs.

## 4. Is RPC always over the Internet?

No. RPC can operate:

- On the same machine, using local sockets.
- Across a local network.
- Across the Internet.
- Between cloud services inside a private network.

The word remote means another process, not necessarily another country or a public Internet connection.

For your projects: use REST or another suitable web API between Angular and FastAPI, then use JSON-RPC between FastAPI and Bitcoin Core. This separates the public web interface from the node's privileged control interface.