# Sean Kells
# CSEC.380.01
# Professor Chaim Sanders
# act1step2.py - Threading to quickly save all pictures from a site

# How to Use:
#
# docker-compose build --no-cache # Building Image
# docker-compose up # Running Image

import socket, ssl, concurrent.futures, time, os
from bs4 import BeautifulSoup
from threading import Thread

def save_picture(name, url):
    """
    save_pictures takes in URL to a picture to save with a name for the picture

    name: Intended name for the picture
    url: destination URL of the picture

    Return: Nothing, but results in saved image on the local machine
    """
    # URL Preparation
    divided_url = url.split("/")
    request_URI = "/" + "/".join(divided_url[3:])
    
    # Creating SSL Socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    context = ssl.create_default_context()
    context.options &= ~ssl.OP_NO_SSLv3
    client = context.wrap_socket(sock, server_hostname=divided_url[2])
    client.connect((divided_url[2], 443))

    # Creating Request
    hostHeader = "Host: " + divided_url[2] + "\r\n"
    acceptHeader= "Accept: image/webp\r\n"
    acceptEnHeader = "Accept-Encoding: gzip, deflate, br\r\n"
    connectionHeader = "Connection: close\r\n"
    getRequest = "GET " + request_URI + " HTTP/1.1\r\n" + hostHeader + acceptHeader + acceptEnHeader + connectionHeader + "\r\n"
    
    # Sending request
    client.send(getRequest.encode())

    # Receiving Response
    getResponse = bytearray()
    while True:
        data = client.recv(4096)
        if ( len(data) < 1 ) :
            break
        getResponse += data
    
    # Closing Socket
    client.close()

    # Parse out Body
    body = getResponse.split(b'\r\n\r\n',1)[1]

    # Writing Image
    script_dir = os.path.realpath(__file__)
    script_dir = script_dir[:len(script_dir) - len(__file__)]

    image_name = os.path.join(script_dir, "pictures/" + name.replace(" ", "") + ".jpg")
    
    with open(image_name, 'wb') as handler:
        handler.write(body)
    
    print(name + " finished downloading...")
    

def main():
    """
    main function where extracting_courses is called

    Returns: Nothing
    """
    # Creating SSL Socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    context = ssl.create_default_context()
    context.options &= ~ssl.OP_NO_SSLv3
    client = context.wrap_socket(sock, server_hostname="www.rit.edu")
    client.connect(("www.rit.edu", 443))

    # Creating Request
    hostHeader = "Host: www.rit.edu\r\n"
    connectionHeader = "Connection: close\r\n"
    getRequest = "GET /computing/directory?term_node_tid_depth=4919 HTTP/1.1\r\n" + hostHeader + connectionHeader + "\r\n"

    # Sending request
    client.send(getRequest.encode())

    # Receiving Response
    getResponse = ''
    while True:
        data = client.recv(4096).decode()
        if ( len(data) < 1 ) :
            break
        getResponse += data
    
    # Closing Socket
    client.close() 

    # Parse out Body
    body = getResponse.split('\r\n\r\n',1)[1]

    # Create Soup
    soup = BeautifulSoup(body, 'lxml')

    url_dict = {}
    # Find the image URLs
    for img in soup.find_all('img'):
        if img.has_attr('class') and img['class'][0] == 'card-img-top':
            url_dict[img['alt']] = img['data-src']

    # Time before IP Processing
    startTime = time.time()

    # Multi-Processing execution of the method scanIP(ipList)
    executor = concurrent.futures.ThreadPoolExecutor(len(url_dict))
    futures = [executor.submit(save_picture, person, url_dict[person]) for person in url_dict.keys()]
    concurrent.futures.wait(futures)
    
    # Ending time
    print("The total run time is: ", str(time.time() - startTime))

main()
