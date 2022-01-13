# Sean Kells
# CSEC.380.01
# Professor Chaim Sanders
# act1.py - Find Flag1

import socket

port = 82
host = "csec380-core.csec.rit.edu"

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client.connect((host, port))

# Create the request

# POST / HTTP/1.1
# Host: csec380-core.csec.rit.edu
# Content-Type: application/x-www-form-urlencoded
# Content-Length: 12
#
# user=spk3077
hostHeader = "Host: " + host + "\r\n"
contentTypHeader = "Content-Type: application/x-www-form-urlencoded\r\n"
contentLenHeader = "Content-Length: 12\r\n"
parameters = "\r\nuser=spk3077"
postRequest = "POST / HTTP/1.1\r\n" + hostHeader + contentTypHeader + contentLenHeader + parameters

# Checking Post Request
print(postRequest)

# Let's send!
client.send(postRequest.encode())

# Retrieving incoming response
postResponse = client.recv(4096)

# Print Response
print(postResponse)

# Closing socket
client.shutdown(socket.SHUT_RDWR)
client.close()