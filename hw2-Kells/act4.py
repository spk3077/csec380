# Sean Kells
# CSEC.380.01
# Professor Chaim Sanders
# act4.py - Find flag4

import socket, ast, re

port = 82
host = "csec380-core.csec.rit.edu"
CRLF = "\r\n\r\n"

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client.connect((host, port))

# Create the request for token

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

# Create request for an Account

# POST /createAccount HTTP/1.1
# Host: csec380-core.csec.rit.edu
# Content-Type: application/x-www-form-urlencoded
# Content-Length:  36 + len(token)
# Accept: text/htl, application/xhtml+xml, image/jxr, */*
# Accept-Encoding: gzip, deflate\r\n
# Accept-Language: en-US,en;q=0.5
# User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko
#
# user=spk3077&token=token&username=spk3077
contentLenHeader = "Content-Length: " + str(36 + len(token)) + "\r\n" # 36 extra characters from 'user=spk3077&token=username=spk3077'
acceptHeader = "Accept: text/html, application/xhtml+xml, image/jxr, */*\r\n"
acceptEnHeader = "Accept-Encoding: gzip, deflate, chunked\r\n"
acceptLanHeader = "Accept-Language: en-US,en;q=0.5\r\n"
userAgentHeader = "User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko\r\n"
parameters += "&token=" + token + "&username=spk3077"
postRequest = "POST /createAccount HTTP/1.1\r\n" + hostHeader + contentTypHeader + contentLenHeader + acceptHeader + acceptEnHeader +  \
    acceptLanHeader + userAgentHeader + parameters

# Send request for Account Password
client.send(postRequest.encode())
# Retrieving response
postResponse = client.recv(4096)

# Splicing output to get body only (for password)
body = postResponse.decode().split(CRLF, 1)[1]
password = ast.literal_eval(body)["account_password"]

# Replacing special chars in password
password = password.replace('&', '%26')
password = password.replace('=', '%3D')

# Login

# POST /login HTTP/1.1
# Host: csec380-core.csec.rit.edu
# Content-Type: application/x-www-form-urlencoded
# Content-Length:  36 + len(token)
# Accept: text/htl, application/xhtml+xml, image/jxr, */*
# Accept-Encoding: gzip, deflate, chunked\r\n
# Accept-Language: en-US,en;q=0.5
# User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko
#
# token=token&username=spk3077&password=password
contentLenHeader = "Content-Length: " + str( 46 + len(token) + len(password)) + "\r\n" # 45 extra characters from 'user=spk3077&token=&username=spk3077&password='
acceptEnHeader = "Accept-Encoding: chunked\r\n"
parameters = "\r\nuser=spk3077&token=" + token + "&username=spk3077&password=" + password
postRequest = "POST /login HTTP/1.1\r\n" + hostHeader + contentTypHeader + contentLenHeader + acceptHeader + acceptEnHeader +  \
    acceptLanHeader + userAgentHeader + parameters

# Send request for Account Password
client.send(postRequest.encode())
# Retrieving response
postResponse = client.recv(4096)

print(postResponse)

# Closing socket
client.shutdown(socket.SHUT_RDWR)
client.close()