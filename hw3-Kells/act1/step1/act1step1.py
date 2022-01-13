# Sean Kells
# CSEC.380.01
# Professor Chaim Sanders
# act1step1.py - Extracting all COurses with respective numbers and names from-
# https://www.rit.edu/study/computing-security-bs
# Output in CSV File

# How to Use:
#
# docker-compose build --no-cache # Building Image
# docker-compose up # Running Image


import csv, socket, ssl, re
from bs4 import BeautifulSoup

def extracting_courses(site_path):
    """
    extracting_courses extracts all courses from the site path of RIT that have both 
    numbers and names and adds them to a CSV

    site_path: path of www.rit.edu to extract from

    Return: Nothing, but outputs a file in the local directory
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
    getRequest = "GET " + site_path + " HTTP/1.1\r\n" + hostHeader + connectionHeader + "\r\n"

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

    # Setting up CSV File
    csvfile = open('courses.csv', 'w')
    filewriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)

    # Parsing with BeautifulSoup
    for tr in soup.find_all('tr'):
        if tr.has_attr('class') and tr['class'][0] == 'hidden-row':

            # Array of TDs
            tds = tr.find_all('td')

            # First TD (Course Number)
            courseNum = re.sub(r'\n\s*\n', r'\n\n', tds[0].string.strip(), flags=re.M)
            if len(courseNum) == 0 or len(courseNum) > 8:
                continue

            # Second TD (Course Name)
            courseName = re.sub(r'\n\s*\n', r'\n\n', tds[1].div.string.strip(), flags=re.M)

            # Writing to CSV
            filewriter.writerow([courseNum, courseName])

    # Closing CSV File
    csvfile.close()
    print("Finished CSV Writing")


def main():
    """
    main function where extracting_courses is called

    Returns: Nothing
    """
    site_path = "/study/computing-security-bs"
    extracting_courses(site_path)

main()
