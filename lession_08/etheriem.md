# Ethereum: A Blockchain Engineering Perspective

## 1. Introduction: What Is Ethereum?

Imagine that you want to build an application where users can transfer money, exchange digital assets, or execute financial agreements without depending on a central company, bank, or server.

With a traditional application, you usually need a backend server, a database, and an organization responsible for enforcing the application's rules.

Ethereum introduces a different model: a decentralized network that executes programs and maintains a shared state across thousands of independent computers.

Ethereum is a decentralized, programmable blockchain. It allows developers to deploy programs called smart contracts, which are executed according to predefined rules by the network's participants.

Ethereum was proposed by Vitalik Buterin in 2013 and launched in 2015.

From an engineering perspective, Ethereum combines several important concepts:

- Distributed systems
- Peer-to-peer networking
- Cryptography and digital signatures
- Distributed state machines
- Virtual machines and program execution
- Economic incentives and consensus protocols

To understand Ethereum properly, you should not think of it merely as a cryptocurrency. Think of it as a distributed computing platform with a native economic system.

## 2. Ethereum vs. Bitcoin

You have already explored Bitcoin nodes, wallets, transactions, UTXOs, and regtest. These concepts provide an excellent foundation for understanding Ethereum.

The fundamental difference is in their primary design goals.

Bitcoin

Primarily designed as a decentralized peer-to-peer payment system and monetary network. Its transaction model is based on UTXOs, and its scripting system is intentionally limited.

Ethereum

Designed as a general-purpose programmable blockchain. Its account-based state model and virtual machine enable smart contracts, decentralized applications, and programmable digital assets.

Here is the technical comparison:

| Feature               | Bitcoin                    | Ethereum                         |
| --------------------- | -------------------------- | -------------------------------- |
| Primary purpose       | Decentralized money        | Programmable blockchain          |
| State model           | UTXO                       | Account-based                    |
| Programmability       | Bitcoin Script             | EVM bytecode and smart contracts |
| Native asset          | BTC                        | ETH                              |
| Execution environment | Bitcoin Script interpreter | Ethereum Virtual Machine (EVM)   |
| Consensus today       | Proof of Work              | Proof of Stake                   |
| Transaction fees      | Paid in BTC                | Paid in ETH                      |
| Typical applications  | Payments, settlement       | DeFi, tokens, DAOs, applications |

An important distinction: Bitcoin also supports programmable transactions, while Ethereum's execution environment is designed to support more general-purpose smart contract logic.

## 3. The Architecture of Ethereum

To understand Ethereum as an engineer, separate the system into its major components.

Decentralized Application (dApp)

Web interface, mobile application, or script

Application Interface

JSON-RPC, libraries, wallet, or node provider

Ethereum Node

Networking, transaction validation, execution, and blockchain data

Execution Layer

Accounts, EVM, transactions, state

Consensus Layer

Proof of Stake, validators, finality

These components cooperate to maintain a common blockchain state.

### 3.1. The Peer-to-Peer Network

Ethereum is not hosted on one central server.

Instead, nodes communicate with other nodes to exchange information about blocks, transactions, and the network's current state.

A node can perform tasks such as:

- Receiving and validating transactions.
- Sharing transactions with peers.
- Receiving and validating blocks.
- Executing transactions to verify their results.
- Maintaining blockchain data and state.

This is closely related to the P2P networking concepts you have studied in your C++ file-sharing project.

However, there is a critical difference: a torrent peer primarily exchanges file pieces, while an Ethereum node participates in a protocol that maintains a globally consistent ledger and executes deterministic state transitions.

### 3.2. Execution Layer

The execution layer handles Ethereum's transaction processing and smart contract execution.

Its responsibilities include:

- Managing account balances and contract storage.
- Validating transaction execution rules.
- Executing EVM instructions.
- Computing gas consumption.
- Producing the resulting state changes.

Execution clients include Geth, Nethermind, Besu, and Erigon.

### 3.3. Consensus Layer

Ethereum uses Proof of Stake rather than Bitcoin's Proof of Work.

Validators stake ETH and participate in proposing blocks and attesting to blocks proposed by other validators. The consensus protocol coordinates agreement about the canonical chain and its finality.

Consensus clients include Lighthouse, Prysm, Teku, Nimbus, and Lodestar.

On a normal Ethereum node, an execution client and a consensus client work together.

## 4. What Is the Ethereum Virtual Machine?

The Ethereum Virtual Machine (EVM) is one of the most important concepts in Ethereum.

Consider a normal backend application:

```
balance = 100balance = balance - 10
```

When you run this code on your computer, your CPU executes machine instructions and modifies local memory.

Now imagine that the same business logic must produce the same result across many independent computers, even when those computers have different operating systems and hardware.

Ethereum addresses this problem with a deterministic execution environment: the EVM.

The EVM defines how smart contract bytecode is interpreted, how storage is accessed, and how execution consumes gas.

For a valid transaction and the same starting state, compliant execution clients must produce the same result.

This deterministic behavior is essential for blockchain consensus.

### How does it work?

1. A developer writes a smart contract, often in Solidity.
2. A compiler converts the source code into EVM bytecode.
3. The bytecode is deployed to Ethereum.
4. A transaction calls the contract.
5. Ethereum nodes execute the relevant instructions.
6. The resulting state changes are checked and incorporated into the blockchain through the protocol.

Unlike an ordinary centralized backend, a smart contract's execution rules are enforced through the Ethereum protocol rather than being controlled solely by the application developer's server.

## 5. What Is a Smart Contract?

A smart contract is a program deployed at an address on Ethereum.

It can store information, receive transactions, enforce conditions, transfer assets, and call other contracts.

For example, imagine a contract that stores the number of votes received by each candidate.

A simplified Solidity example:

```
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract SimpleVoting {
    mapping(string => uint256) public votes;

    function vote(string calldata candidate) external {
        votes[candidate] += 1;
    }
}
```

This contract maintains a mapping between candidate names and vote counts.

When someone calls `vote("Alice")`, the contract increments Alice's counter in persistent contract storage.

Anyone can query the public mapping through the generated getter function.

However, this example is for learning only. It does not prevent people from voting multiple times, and a production voting system would need a carefully designed identity, eligibility, privacy, and security model.

### Important engineering properties

- Determinism: Contract execution follows protocol-defined rules.
- Persistent storage: Contracts can retain state between transactions.
- Public verifiability: On a public chain, contract code and state are generally inspectable.
- Composability: One contract can interact with another.
- Limited execution resources: Gas prevents unrestricted computation.

A smart contract is not automatically secure merely because it runs on a blockchain. Bugs in contract logic can cause permanent financial losses.

## 6. What Is ETH?

ETH is Ethereum's native asset.

It has several roles in the network:

1\. Transaction fees

Users pay for computation and other transaction execution costs using ETH.

2\. Staking

Validators stake ETH to participate in Ethereum's Proof-of-Stake consensus mechanism.

3\. Economic security

Staking incentives and penalties help encourage validators to follow protocol rules.

4\. Value transfer

ETH can be transferred between accounts like a digital asset.

One ETH is divisible into \\(10^{18}\\) wei.

\\[ 1\ \mathrm{ETH}=10^{18}\ \mathrm{wei} \\]

Wei is the smallest denomination used by Ethereum's protocol.

Do not confuse ETH with ERC-20 tokens. ETH is native to the protocol, while ERC-20 tokens are assets implemented by smart contracts.

## 7. How Does an Ethereum Transaction Work?

Suppose Alice wants to send 1 ETH to Bob.

The transaction passes through several stages.

1. Transaction creation

   Alice's wallet constructs a transaction containing the recipient address, value, nonce, gas parameters, and other required fields.
2. Digital signature

   Alice's wallet signs the transaction using her private key. The signature allows nodes to verify authorization without revealing the private key.
3. Transaction propagation

   Alice submits the transaction to a node, which may propagate it to peers. The transaction is usually placed in a transaction pool while awaiting inclusion.
4. Block proposal

   A validator proposes a block containing the transaction, subject to Ethereum's protocol rules.
5. Execution and validation

   Execution clients check the transaction and calculate its state changes, including the ETH transfer and fee accounting. Other nodes independently verify the block.
6. Consensus and finality

   Validators participate in consensus. A transaction included in a block is not necessarily immediately finalized; Ethereum's consensus protocol provides finality under its assumptions.

### What happens to the balances?

Conceptually, the value transfer changes the account state:

\\[ \begin{aligned} \mathrm{Balance}\_{Alice}' &= \mathrm{Balance}\_{Alice} - 1\ \mathrm{ETH} - \mathrm{fee}\\\ \mathrm{Balance}\_{Bob}' &= \mathrm{Balance}\_{Bob} + 1\ \mathrm{ETH} \end{aligned} \\]

The fee is separate from the transferred value. The actual protocol also checks the sender's nonce, signature, available balance, gas limit, and applicable transaction rules.

Unlike Bitcoin, Ethereum does not select individual UTXOs for a normal ETH transfer. It updates account balances in the global state.

## 8. What Is Gas?

Gas measures the computational work and certain resource costs required to execute an Ethereum transaction.

Consider two transactions:

- Transaction A transfers ETH to an externally owned account.
- Transaction B calls a smart contract that performs calculations and updates multiple storage slots.

The second transaction may consume substantially more gas because it performs more computation and storage operations.

Ethereum's transaction fee mechanism includes:

- Gas used: The amount of gas consumed by execution.
- Base fee: The protocol-determined fee per gas unit for a block.
- Priority fee: An optional additional fee that incentivizes block inclusion.
- Maximum fee per gas: The sender's configured upper bound for the effective gas price.

For a typical EIP-1559 transaction:

\\[ \text{Transaction fee}=\text{Gas used}\times\text{Effective gas price} \\]

The effective gas price depends on the base fee and the transaction's fee settings.

Gas is not the same as ETH: gas measures execution resources, while the fee is paid in ETH.

## 9. Ethereum's Account Model

Ethereum maintains a global state containing accounts.

There are two principal account categories.

| Account type                   | Description                                                 |
| ------------------------------ | ----------------------------------------------------------- |
| Externally owned account (EOA) | Controlled through a private key; can initiate transactions |
| Contract account               | Associated with deployed code and persistent storage        |

An account has fields including:

- Nonce
- ETH balance
- Storage root
- Code hash

For an externally owned account, contract code is absent. For a contract account, the code hash identifies the associated code in Ethereum's state model.

A contract account does not independently sign transactions using a private key. It executes when called through transactions or other contract executions.

### Compare this with Bitcoin

In Bitcoin, spending normally consumes existing UTXOs and creates new outputs.

In Ethereum, a standard ETH transfer updates account balances and the sender's nonce.

This difference influences how wallets, transaction validation, storage, and execution are implemented.

## 10. What Is Proof of Stake?

Ethereum switched from Proof of Work to Proof of Stake in September 2022.

In Proof of Work, Bitcoin miners compete by performing computational work to produce valid blocks.

In Ethereum's Proof-of-Stake system, validators stake ETH and participate in block proposals and attestations.

At a high level:

1. Validators deposit ETH through the staking mechanism.
2. The protocol selects validators for duties.
3. A selected proposer proposes a block.
4. Other validators attest to blocks they consider valid.
5. Consensus rules determine chain progression and finality.
6. Protocol rewards and penalties provide economic incentives.

Ethereum's security depends on more than simply owning ETH. It depends on the consensus protocol, validator participation, cryptographic assumptions, and economic incentives.

A finality mechanism helps make finalized blocks extremely difficult to reverse under the protocol's security assumptions.

## 11. What Can You Build on Ethereum?

Ethereum supports applications in which shared state and publicly verifiable rules are useful.

[DeFi: Everything You Need To Know About The New World Of Cryptocurrency | Payperless - The Crypto Wallet App](https://images.openai.com/static-rsc-4/KAQxDnxYqbL58bM6V600IKVcOSTmn3hV1QP9-sKGDFF_n2i6kve92VY3MPhVo7ienVUn-2YbQalYP7DJup4QTO7SN14Fu1uhjaLcCqrMrl7MaVoxZwl6lWf0k7QuVQqe3q7FTHE_7wv4l1dqiJprJKCYDRYvqLigXX8qMm-H2lU?purpose=inline)

Decentralized Finance (DeFi)

Lending protocols, decentralized exchanges, collateral management, and automated financial operations.

[What  Are Halal Stocks](https://images.openai.com/static-rsc-4/3A7O1evCRRctxmAVIjSPy6JgEQdkVgsMJUeZSj8tbrAgVdOuvldDh8TBpIdopMwc3-D2rnRp12bFuw9-A-_jmhUmpHEk0mpUl7cqaQwVpjlv_cou1U_KA6qAmZ_OJjARt-8Jqc84gj4nL9P3NdQ8QazeOccMAj3pdAhUvJIQH_4?purpose=inline)

Digital Assets

NFTs and fungible tokens can represent collectibles, ownership records, or application-specific assets.

[DAO or Decentralized Autonomous Organization with smart contract to control leadership by code and blockchain](https://images.openai.com/static-rsc-4/9VaWRxoVhTFB057hMcX1zuxfHa537VhnRAlemPGjmX0l9utM6pUNGIOCxf6aispgwrwhrepH8gE2TNK0X2yZcGxT5sq9JkIWgKyHC6TEWMmq6d-Zbh8pKxvW4K3WE2oiqA81S4f_DhyT8F_pf-hZP8QfsTeF61calUErr6NjhhITsTZKy6LjF82LhRhG0x4C?purpose=inline)

Decentralized Governance

Smart contracts can implement voting, treasury management, and other governance mechanisms.

[Blockchain Beyond Cryptocurrency: Real- World Applications | by IEEE WIE MUJ | Medium](https://images.openai.com/static-rsc-4/_4ayYZzl3S7VRnXda3K3LZ-7evQknB0lOeMSh03OF-Tnw7hv5Vsveywmfa9LyHALCQkyDPK70432Bwz_9WnB5gRMWYiKzgCHw53Ok3caIoHmeel5eYYdNkhv_xMA-_sH0IAEjvN14u5VWZ8UIw4LmHQfQn_q1e6ohv1E4M_eyt0?purpose=inline)

Traceability and Registries

Applications can maintain verifiable records and shared business rules across organizations.

Not every application needs a blockchain. If a trusted organization can manage the database efficiently and no decentralized trust is required, a conventional database may be simpler, faster, and cheaper.

## 12. How Do You Interact with Ethereum as a Developer?

A practical Ethereum development stack can contain the following components:

| Component               | Example                               |
| ----------------------- | ------------------------------------- |
| Smart contract language | Solidity                              |
| Contract compiler       | `solc`                                |
| Development framework   | Foundry or Hardhat                    |
| Local blockchain        | Anvil                                 |
| Client interface        | JavaScript with `ethers.js`           |
| Node interface          | Ethereum JSON-RPC                     |
| Wallet                  | MetaMask or another compatible wallet |
| Blockchain explorer     | Etherscan                             |

For example, an application can query the balance of an account through the Ethereum JSON-RPC method `eth_getBalance`.

A developer can also call contract functions, deploy new contracts, inspect transactions, and listen for events.

The most important distinction is between reading and writing:

- A read-only contract call can usually be executed locally by a node without submitting a transaction or paying an on-chain fee.
- A state-changing operation requires a signed transaction, execution, and inclusion in the blockchain to persist its effects.

## 13. Ethereum and Your Existing Blockchain Knowledge

As a computer engineering student, you should connect Ethereum to concepts you already understand.

| Existing concept     | Ethereum connection                                   |
| -------------------- | ----------------------------------------------------- |
| C++ P2P networking   | Peer discovery, transaction propagation, block gossip |
| Bitcoin wallets      | Keys, signatures, addresses, transaction construction |
| Bitcoin regtest      | Local Ethereum chains and development networks        |
| Databases            | Account state, contract storage, state transitions    |
| Distributed systems  | Consensus, fault tolerance, replicated execution      |
| Virtual machines     | EVM instruction execution                             |
| API development      | JSON-RPC and smart contract interfaces                |
| Security engineering | Key management, contract audits, access control       |

One important lesson: a blockchain is not simply a distributed database. It combines a replicated state machine with a consensus protocol, cryptographic authorization, and incentives that allow independent participants to agree on state without relying entirely on a central operator.

## 14. Recommended Practical Roadmap

To move from theory to engineering practice, follow this order:

1. Ethereum fundamentals: Accounts, addresses, private keys, transactions, nonces, gas, blocks, and chain state.
2. Local environment: Install Foundry or Hardhat and run a local Ethereum development chain.
3. Solidity: Implement a counter, voting contract, and simple token.
4. EVM execution: Study bytecode, opcodes, memory, stack, storage, and gas consumption.
5. JSON-RPC: Use methods such as `eth_chainId`, `eth_getBalance`, `eth_getTransactionReceipt`, and `eth_call`.
6. dApp integration: Build a small frontend that reads contract state and submits signed transactions.
7. Security: Study reentrancy, access control, arithmetic, transaction ordering, and smart contract testing.
8. Node architecture: Explore execution clients, consensus clients, peer networking, and validator operation.

## Final perspective

Ethereum takes the idea of a blockchain beyond recording transfers of digital currency. It provides a shared execution environment in which independent participants can verify transactions and smart contract state changes according to the same protocol.

For an engineer, the central idea is this:

Ethereum is a decentralized, consensus-driven state machine whose programmable execution environment enables applications to operate without relying exclusively on a central authority.

Once you understand accounts, transactions, the EVM, gas, and Proof of Stake, you will have the foundations needed to study Ethereum's deeper internals and build your own decentralized applications.
-----------------------------------------------------------------
# The DAO Hack: Why Ethereum Split into Ethereum and Ethereum Classic

To understand this historical event, imagine that you are an engineer maintaining a blockchain used by thousands of independent computers. One day, a smart contract is exploited, and a large amount of users' funds is stolen.

You now face a difficult question:

Should the blockchain continue following its original history, including the theft, or should the protocol be changed to reverse its consequences?

In 2016, the Ethereum community faced exactly this dilemma. The disagreement led to a hard fork, creating two separate blockchain histories: Ethereum (ETH) and Ethereum Classic (ETC).

## 1. What was The DAO?

[The Dev files - File 003/The DAO](https://images.openai.com/static-rsc-4/KKYF0aVD0bYt6z8dJJ5yx0IGCvz5JNcF_VLLwqIesj1jpZK3YoR4jQTAqY6AnhRD-YSc9_24iDA8goybtrt-DoAvyTtiOu5VWP6gXiV3IxnoK4LdDJlSA1neAt_jR9dLih37ACF9c6RSjS1HwxVFqLuHvxdattb1jniGKukinTg?purpose=inline)

The DAO was a decentralized autonomous organization launched on Ethereum in 2016.

Its purpose was to pool money from investors and use smart contracts to manage funding for proposed projects. Participants could contribute ETH and participate in governance decisions.

The important engineering point is that The DAO was not the Ethereum blockchain itself. It was an application implemented using Ethereum smart contracts.

Investors sent ETH to The DAO's contracts, which contained the rules governing contributions, proposals, and withdrawals.

The DAO attracted substantial investment, but a vulnerability in its smart-contract logic allowed an attacker to withdraw a large amount of ETH.

## 2. How did the DAO hack work?

The vulnerability involved a pattern commonly called reentrancy.

Consider a simplified withdrawal function:

```
function withdraw(uint256 amount) external {
    require(balances[msg.sender] >= amount);

    // Send ETH to the caller.
    (bool success, ) = msg.sender.call{value: amount}("");
    require(success);

    // Update the recorded balance.
    balances[msg.sender] -= amount;
}
```

This example is intentionally vulnerable and is for education only.

The critical mistake is that the contract sends ETH before updating the user's recorded balance.

### Step-by-step execution

1. The attacker calls `withdraw()`. The contract checks that the attacker's recorded balance is sufficient.
2. The contract sends ETH to the attacker. The external call can execute code in the attacker's receiving contract.
3. The attacker's contract calls `withdraw()` again. Because the original call has not yet updated the balance, the balance check may still pass.
4. The process repeats. The contract can send additional ETH before the original withdrawal completes and updates the recorded balance.

This is a reentrancy attack: an external contract re-enters the vulnerable function before the first execution has finished.

A safer design generally follows the checks-effects-interactions pattern: validate conditions, update internal state, and only then make external calls. A reentrancy guard can provide additional protection.

The DAO incident exploited a more complex implementation of this class of vulnerability. Approximately 3.6 million ETH was diverted into a child DAO structure controlled by the attacker.

## 3. What is a hard fork?

A hard fork is a protocol change that is not backward-compatible: nodes running the old rules may reject blocks produced under the new rules.

Imagine a blockchain whose nodes all agree on the rules for executing transactions.

At a particular block height, some nodes upgrade their software and others do not.

- The upgraded nodes follow the new rules.
- The non-upgraded nodes continue following the old rules.
- If the rules produce incompatible outcomes, two separate chains can continue to exist.

A hard fork does not always create two permanent blockchains. If the community coordinates around the upgrade, the old chain may simply lose support. In the DAO incident, however, both chains continued.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://ethereum.org\&sz=32)

ethereum.org

+1



## 4. What happened on July 20, 2016?

The DAO fork activated at block 1,920,000. The new rules moved ETH held in designated DAO-related contracts into a recovery contract, allowing eligible DAO token holders to withdraw funds. This was an exceptional state change, not simply a normal smart-contract bug fix.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://blog.ethereum.org\&sz=32)

Ethereum Foundation Blog

+1



One Ethereum blockchain before the fork

Shared history through block 1,919,999

## Ethereum (ETH)

New rules

The forked chain applied the recovery state change. It retained the Ethereum name and subsequently moved to Proof of Stake in 2022.

## Ethereum Classic (ETC)

Original rules

This chain continued without the DAO recovery change. It retained the original transaction history, including the exploit, and continued using Proof of Work.

Both chains share the history before the split, but have different state histories after it.

Source: Ethereum Foundation and Ethereum Classic historical records.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://blog.ethereum.org\&sz=32)

Ethereum Foundation Blog

+2



## 5. Why did the community disagree?

There were two major positions.

Position A — Support the fork

Supporters argued that the attack had caused serious losses and that the community should provide a recovery mechanism for affected investors.

They accepted changing the blockchain's state through a special protocol intervention.

Position B — Reject the fork

Opponents argued that transactions valid under the existing protocol should not be selectively reversed because of an application's failure.

They emphasized immutability, predictable rules, and the principle commonly expressed as "Code is Law."

The disagreement was not simply about programming. It was about governance: who should have the authority to change the consequences of events on a decentralized blockchain?&#x20;

[image](https://www.google.com/s2/favicons?domain=https://ethereum.org\&sz=32)

ethereum.org

+1



Neither position eliminates every trade-off. A recovery intervention can protect users in exceptional circumstances, but it can also raise questions about neutrality and future interventions. Refusing intervention preserves the original history, but leaves losses caused by vulnerable applications in place.

## 6. What is the difference today?

| Property            | Ethereum (ETH) | Ethereum Classic (ETC)   |
| ------------------- | -------------- | ------------------------ |
| Origin              | DAO-fork chain | Original, non-fork chain |
| DAO recovery change | Applied        | Not applied              |
| Consensus mechanism | Proof of Stake | Proof of Work            |
| Smart contracts     | Supported      | Supported                |
| Native asset        | ETH            | ETC                      |

The two networks share their pre-fork history, but they are now independent networks with their own consensus, blocks, and native assets. ETH and ETC are not interchangeable, even though they originated from the same chain.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://ethereum.org\&sz=32)

ethereum.org

+1



## 7. The engineering lesson

As a blockchain engineer, remember three distinctions:

1. A smart contract vulnerability is a defect in application logic.
2. A hard fork is a protocol change that old software does not necessarily accept.
3. A chain split occurs when groups continue following incompatible rules.

The DAO incident demonstrates that blockchain immutability is not purely a technical property. It also depends on the decisions made by node operators, developers, validators or miners, users, and the wider ecosystem.

Think about this question: If you were developing Ethereum in 2016, would you have supported the DAO hard fork to recover users' funds, or would you have preserved the original blockchain history? What technical and ethical arguments would you use to defend your decision?
-----------------------------------------------------------------
# What Are dApps? — Decentralized Applications

As a computer engineering student, you already know how to build applications with a frontend, a backend, and a database. A dApp (decentralized application) is an application that uses a blockchain and smart contracts to implement some of its core logic without depending entirely on a central server.

The abbreviation means decentralized application.

Examples include decentralized exchanges, blockchain games, lending protocols, and digital asset marketplaces.

## 1. Traditional application vs. dApp

Imagine you build a money-transfer application.

## A. Traditional application

Frontend

React / Angular

Backend server

FastAPI / Spring Boot

Central database

PostgreSQL / MySQL

The organization operating the backend generally controls the application logic and database.

## B. Decentralized application

Frontend

React / Angular / HTML

Ethereum interface

Wallet + ethers.js + JSON-RPC

Smart contract on Ethereum

Shared state + blockchain execution

Core rules and state changes can be enforced by the blockchain rather than only by one company's backend.

Notice something important: a dApp can still have a frontend, APIs, and centralized infrastructure. What makes it decentralized is the role played by the blockchain in its core functionality, not the absence of every server.

## 2. How does a dApp work?

Suppose Alice wants to exchange one digital token for another using a decentralized exchange.

1. Alice opens the application. Her browser loads the frontend.
2. She connects her wallet. The wallet provides her public account address and can request authorization to sign transactions.
3. The application interacts with a smart contract. It reads exchange information and prepares a transaction.
4. Alice approves the transaction. Her wallet signs it with her private key, after she reviews and authorizes the requested operation.
5. The transaction reaches Ethereum. A node receives it, and it may be included in a block.
6. The smart contract executes. If the transaction succeeds and is included in the canonical chain, the blockchain state is updated according to the contract's rules.

The key distinction is that Alice does not need to trust a single exchange company's private database to enforce every exchange rule. She relies on the deployed contract and the blockchain's execution and consensus mechanisms.

She still needs to consider contract vulnerabilities, transaction fees, wallet security, and the possibility of malicious applications.

## 3. What are the main components of a dApp?

| Component       | Responsibility                                 | Example        |
| --------------- | ---------------------------------------------- | -------------- |
| Frontend        | User interface                                 | Angular, React |
| Wallet          | Account access and transaction signing         | MetaMask       |
| Web3 library    | Communicates with blockchain interfaces        | ethers.js      |
| Smart contract  | Implements application rules                   | Solidity       |
| Blockchain node | Reads chain data and submits transactions      | Geth           |
| Blockchain      | Maintains shared state and transaction history | Ethereum       |

Some dApps also use centralized APIs, off-chain databases, decentralized storage such as IPFS, or indexing services to make data retrieval faster.

## 4. A simple smart contract for a dApp

Let's build a tiny counter. It stores a number on Ethereum and allows users to increment it.

```
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract Counter {
    uint256 public count;

    function increment() external {
        count += 1;
    }
}
```

What happens here?

- `count` is stored in the contract's persistent state.
- `increment()` changes that state.
- `public` automatically provides a getter function called `count()`.
- Calling `count()` through a read-only call does not require an on-chain transaction.
- Calling `increment()` requires a transaction to change persistent state, and normally incurs a gas fee.

The contract alone is not a complete dApp. You would add a frontend that reads `count()` and provides a button to call `increment()` through a connected wallet.

## 5. Examples of real dApps

[Uniswap v2 Mainnet Launch](https://images.openai.com/static-rsc-4/Jqd45XZyftT7QRoxc1L5kRAYRnB-2L9SmzhqXHBM_CfoDYoUE2zO6vB-CZlp7MIXpEb4xMv9B96gM4wzntSurK_TLaDsxnxWcs-u2oJmllFxO2fYJVT5fnLu-rEkobWXZgWnQYbMwnIoh6zVfzEPdvKzvxC7_1uPDkTFWW3JhfM?purpose=inline)

Uniswap

A decentralized exchange protocol that uses smart contracts to facilitate token swaps.

[Ethereum Apps - Aave | ⁦ethereum.org⁩](https://images.openai.com/static-rsc-4/g9-NUVA4Q82Jbn2WqmYzafZ0ckla1ZpIqyPmuU4nkLyqHwxGZaZQt_h_t2pHRp4jBg6GAuHEOcqwLRIpZI6pVVG5SBObawLwzkz3L3A7E5K8iFKwIHdHxVVTgJwbqAxgvDbKIwzvMC1YPPVpSYONTCGrOU3-ep-WVw24YMy3JFs?purpose=inline)

Aave

A decentralized lending and borrowing protocol using smart contracts.

[Where Can You Buy (and Sell) NFTs? - Babypips.com](https://images.openai.com/static-rsc-4/YbFaPvAx0Ultkz9OmoJOYE-zTIkjyemHkzPYmNfw9_C2hEbOmYar25wOoQk_hnbEH7kF4I_C4YZKKoLCEBPi5SOMlOS049kjHOucyL9gOzkeWqDVfV1lZZVBcmN8esq-P6VPDCpUYL0Yfc2MMEQs7WQIEl6OvxiDcCPv17tp3hg?purpose=inline)

OpenSea

A digital asset marketplace that supports NFTs and blockchain-based asset trading.

These applications have different architectures and degrees of decentralization. A familiar website interface does not, by itself, guarantee that every part of the application is decentralized.

## 6. What are the advantages and disadvantages?

Advantages

- No single operator needs to control every core transaction rule.
- Blockchain state and transactions can be independently verified.
- Smart contracts can be composed with other protocols.
- Users can interact directly with on-chain applications using compatible wallets.

Disadvantages

- Transactions may incur gas fees and confirmation delays.
- Smart-contract bugs can cause irreversible financial losses.
- Private-key loss or theft can compromise assets.
- Frontends, RPC providers, governance, and other infrastructure can remain centralized.
- Public blockchains generally expose transaction activity, which creates privacy challenges.

## 7. Your first dApp engineering project

Since you have experience with Angular, Python, and blockchain fundamentals, a good first project would be a decentralized voting application.

Build it in these stages:

1. Write a Solidity contract to register candidates and record votes.
2. Test the contract locally using Foundry or Hardhat.
3. Deploy it to a local Ethereum development network.
4. Create an Angular interface.
5. Use `ethers.js` to connect the frontend to the contract.
6. Connect a wallet and submit transactions.
7. Read the contract state and display updated vote counts.

For a learning project, begin on a local network rather than spending real ETH.

The central concept to remember: a dApp combines a user interface with smart contracts and blockchain infrastructure. The frontend helps people use the application; the smart contracts enforce its on-chain rules; and the blockchain maintains the resulting shared state.