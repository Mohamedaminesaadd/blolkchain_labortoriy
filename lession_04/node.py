
import socket
import threading
import sys
import json
import uuid


class Node:

    def __init__(self, host, port, node_id):

        self.host = host
        self.port = port
        self.node_id = node_id

        # Connected peers
        self.peers = []

        # Prevent the same message from circulating forever
        self.seen_messages = set()

        # Protect shared peer list
        self.lock = threading.Lock()

        # TCP server
        self.server = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        self.server.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_REUSEADDR,
            1
        )

        self.server.bind((host, port))
        self.server.listen()

        print(f"[NODE {self.node_id}] Listening on {host}:{port}")

    # ============================================================
    # START NODE
    # ============================================================

    def start(self):

        # Thread responsible for accepting incoming connections
        thread = threading.Thread(
            target=self.accept_connections,
            daemon=True
        )

        thread.start()

        print()
        print("Commands:")
        print("  connect <host> <port>")
        print("  peers")
        print("  send <message>")
        print("  quit")
        print()

        while True:

            try:
                command = input(f"[{self.node_id}] > ")

                # --------------------------------------------
                # CONNECT
                # --------------------------------------------

                if command.startswith("connect"):

                    parts = command.split()

                    if len(parts) != 3:
                        print("Usage: connect <host> <port>")
                        continue

                    _, host, port = parts

                    self.connect_to_peer(
                        host,
                        int(port)
                    )

                # --------------------------------------------
                # SHOW PEERS
                # --------------------------------------------

                elif command == "peers":

                    self.show_peers()

                # --------------------------------------------
                # SEND MESSAGE
                # --------------------------------------------

                elif command.startswith("send"):

                    message = command[5:]

                    if not message:
                        print("Usage: send <message>")
                        continue

                    self.create_and_broadcast(message)

                # --------------------------------------------
                # QUIT
                # --------------------------------------------

                elif command == "quit":

                    print(f"[NODE {self.node_id}] Stopping...")
                    break

                else:

                    print("Unknown command.")

            except KeyboardInterrupt:

                print("\nStopping node...")
                break

    # ============================================================
    # ACCEPT CONNECTIONS
    # ============================================================

    def accept_connections(self):

        while True:

            try:

                connection, address = self.server.accept()

                print(
                    f"\n[NODE {self.node_id}] "
                    f"Incoming connection from {address}"
                )

                self.add_peer(connection)

                thread = threading.Thread(
                    target=self.handle_peer,
                    args=(connection,),
                    daemon=True
                )

                thread.start()

            except OSError:
                break

    # ============================================================
    # CONNECT TO PEER
    # ============================================================

    def connect_to_peer(self, host, port):

        connection = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        try:

            connection.connect((host, port))

            self.add_peer(connection)

            print(
                f"[NODE {self.node_id}] "
                f"Connected to {host}:{port}"
            )

            thread = threading.Thread(
                target=self.handle_peer,
                args=(connection,),
                daemon=True
            )

            thread.start()

        except ConnectionRefusedError:

            print(
                f"[ERROR] Could not connect to "
                f"{host}:{port}"
            )

            connection.close()

        except OSError as e:

            print(f"[ERROR] {e}")

            connection.close()

    # ============================================================
    # ADD PEER
    # ============================================================

    def add_peer(self, connection):

        with self.lock:

            if connection not in self.peers:
                self.peers.append(connection)

    # ============================================================
    # HANDLE PEER
    # ============================================================

    def handle_peer(self, connection):

        buffer = ""

        while True:

            try:

                data = connection.recv(4096)

                if not data:
                    break

                buffer += data.decode()

                # Messages are separated by newline
                while "\n" in buffer:

                    message, buffer = buffer.split(
                        "\n",
                        1
                    )

                    if message:
                        self.handle_message(
                            message,
                            connection
                        )

            except ConnectionResetError:

                break

            except OSError:

                break

        self.remove_peer(connection)

    # ============================================================
    # HANDLE MESSAGE
    # ============================================================

    def handle_message(self, raw_message, sender_connection):

        try:

            message = json.loads(raw_message)

        except json.JSONDecodeError:

            print(
                f"[NODE {self.node_id}] "
                f"Invalid message"
            )

            return

        message_id = message["id"]

        # --------------------------------------------------------
        # IMPORTANT:
        # If we already saw this message,
        # don't process it again.
        # --------------------------------------------------------

        if message_id in self.seen_messages:

            return

        self.seen_messages.add(message_id)

        print()
        print(
            f"[NODE {self.node_id}] "
            f"Received message:"
        )

        print(
            f"    ID      : {message_id}"
        )

        print(
            f"    Sender  : {message['sender']}"
        )

        print(
            f"    Content : {message['content']}"
        )

        # --------------------------------------------------------
        # GOSSIP
        #
        # Forward the message to other peers.
        # Do NOT send it back to the peer that sent it.
        # --------------------------------------------------------

        self.broadcast(
            raw_message,
            exclude=sender_connection
        )

    # ============================================================
    # CREATE MESSAGE
    # ============================================================

    def create_and_broadcast(self, content):

        message = {
            "id": str(uuid.uuid4()),
            "sender": self.node_id,
            "content": content
        }

        # Mark our own message as seen
        self.seen_messages.add(
            message["id"]
        )

        raw_message = json.dumps(message)

        print()
        print(
            f"[NODE {self.node_id}] "
            f"Sending: {content}"
        )

        self.broadcast(raw_message)

    # ============================================================
    # BROADCAST
    # ============================================================

    def broadcast(
        self,
        message,
        exclude=None
    ):

        dead_peers = []

        data = (message + "\n").encode()

        with self.lock:

            peers = list(self.peers)

        for peer in peers:

            # Don't send message back to sender
            if peer == exclude:
                continue

            try:

                peer.sendall(data)

            except OSError:

                dead_peers.append(peer)

        # Remove dead peers

        for peer in dead_peers:

            self.remove_peer(peer)

    # ============================================================
    # REMOVE PEER
    # ============================================================

    def remove_peer(self, peer):

        with self.lock:

            if peer in self.peers:

                self.peers.remove(peer)

        try:
            peer.close()

        except OSError:
            pass

    # ============================================================
    # SHOW PEERS
    # ============================================================

    def show_peers(self):

        with self.lock:

            print(
                f"[NODE {self.node_id}] "
                f"{len(self.peers)} connected peer(s)"
            )

            for peer in self.peers:

                try:

                    print(
                        f"    {peer.getpeername()}"
                    )

                except OSError:

                    pass


# ================================================================
# MAIN
# ================================================================

if __name__ == "__main__":

    if len(sys.argv) != 3:

        print(
            "Usage: python node.py <node_id> <port>"
        )

        print(
            "Example: python node.py A 5001"
        )

        sys.exit(1)

    node_id = sys.argv[1]

    port = int(sys.argv[2])

    node = Node(
        "127.0.0.1",
        port,
        node_id
    )

    node.start()
