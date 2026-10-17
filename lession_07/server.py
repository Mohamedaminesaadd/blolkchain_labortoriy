from xmlrpc.server import SimpleXMLRPCServer

#1.define the function on machine a 
def add(a,b):
    print(f"received request add({a},{b})")
    return a +b 

def multiply(a,b):
    print(f"received request multiply({a},{b})")
    return a*b


# create the server
server = SimpleXMLRPCServer(
    ("0.0.0.0",8000),
    allow_none=True
)

# register function that client can call 

server.register_function(add,"add")
server.register_function(multiply,"multiply")

print("RPC server listening on port 8000...")

# 4. Wait for client requests
server.serve_forever()