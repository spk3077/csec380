# Sean Kells
# CSEC.380.01
# Professor Chaim Sanders
# act2.py - Find flag2

import socket, ast

port = 82
host = "csec380-core.csec.rit.edu"
CRLF = "\r\n\r\n"

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client.connect((host, port))

# Create the request

# POST /getSecure HTTP/1.1
# Host: csec380-core.csec.rit.edu
# Content-Type: application/x-www-form-urlencoded
# Content-Length: 12
#
# user=spk3077
hostHeader = "Host: " + host + "\r\n"
contentTypHeader = "Content-Type: application/x-www-form-urlencoded\r\n"
contentLenHeader = "Content-Length: 12\r\n"
parameters = "\r\nuser=spk3077"
postRequest = "POST /getSecure HTTP/1.1\r\n" + hostHeader + contentTypHeader + contentLenHeader + parameters

# Send request for token
client.send(postRequest.encode())
# Retrieving incoming response
postResponse = client.recv(4096)

# Splicing output to get body only (for token)
body = postResponse.decode().split(CRLF, 1)[1]
token = ast.literal_eval(body)['token']


# Create another request

# POST /getFlag2 HTTP/1.1
# Host: csec380-core.csec.rit.edu
# Content-Type: application/x-www-form-urlencoded
# Content-Length: len(token) + 19
#
# user=spk3077&token=token

contentLenHeader = "Content-Length: " + str(19 + len(token)) + "\r\n" # 19 extra characters from 'user=spk3077&token='
parameters += "&token=" + token
postRequest = "POST /getFlag2 HTTP/1.1\r\n" + hostHeader + contentTypHeader + contentLenHeader + parameters

# Send request for flag2
client.send(postRequest.encode())
# Received response
postResponse = client.recv(4096)

#Print the Flag
print(postResponse)

# Closing socket
client.shutdown(socket.SHUT_RDWR)
client.close()