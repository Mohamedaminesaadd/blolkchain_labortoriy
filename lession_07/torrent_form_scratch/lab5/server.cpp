
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
