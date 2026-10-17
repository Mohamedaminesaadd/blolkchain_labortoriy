
#include <iostream>
#include <string>
#include <unordered_set>

using namespace std;

unordered_set<string> seen_messages;

bool process_message(const string& message) {
    size_t separator = message.find('|');

    if (separator == string::npos) {
        cout << "Invalid message: " << message << '\n';
        return false;
    }

    string type = message.substr(0, separator);
    string id = message.substr(separator + 1);

    // Has this message ID already been seen?
    if (seen_messages.count(id)) {
        cout << "Duplicate ignored: " << id << '\n';
        return false;
    }

    // Remember the message ID.
    seen_messages.insert(id);

    cout << "New message received\n";
    cout << "Type: " << type << '\n';
    cout << "ID: " << id << '\n';

    if (type == "PING") {
        cout << "Action: reply PONG and forward if appropriate\n";
    } else if (type == "PONG") {
        cout << "Action: process PONG\n";
    } else {
        cout << "Unknown message type\n";
    }

    return true;
}

int main() {
    process_message("PING|42");
    cout << '\n';

    process_message("PING|42");
    cout << '\n';

    process_message("PONG|43");
    cout << '\n';

    process_message("PING|44");

    return 0;
}
