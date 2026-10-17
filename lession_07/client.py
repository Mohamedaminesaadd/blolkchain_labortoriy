import xmlrpc.client

server = xmlrpc.client.ServerProxy(
    "http://localhost:8000/"
)
# 2. Call functions implemented on Machine A
result1 = server.add(10, 20)
result2 = server.multiply(5, 6)

print("Addition:", result1)
print("Multiplication:", result2)