# Sean Kells
# CSEC.380.01
# Professor Chaim Sanders
# act4.py - Brute force find path of a website

# How to Use:
#
# docker-compose build --no-cache # Building Image
# docker-compose up # Running Image

import socket, ssl, concurrent.futures, time, multiprocessing, more_itertools
from bs4 import BeautifulSoup

VISITEDLINKS = set()

class Crawler:

    def __init__(self, url, depth, limit_domain, port):
        """
        self.url: the full URL of the crawled site
        self.depth: scope of traversal
        self.limit_domain: Stay inside first domain: 1, Don't care: 0
        self.port: the port of the crawled site
        self.protocol: http or https
        self.domain: the domain the crawl
        self.request_uri: the path and potential paramters
        self.response_header: the header of the response
        self.response_body: the body of the response
        """
        self.url = url
        self.depth = depth
        self.limit_domain = limit_domain

        protDomReqList = parseURL(url)
        self.protocol = protDomReqList[0]
        self.domain = protDomReqList[1]
        self.request_uri = protDomReqList[2]

        # Hooli website
        self.port = port

        # Will be defined during data retrieval
        self.response_header = ''
        self.response_body = ''


    def send_receive(self, client):
        """
        send_receive is a helper function that takes in a socket to both send and receive a response with a GET request

        self: the class paramters
        client: the socket

        Return: the data retrieved from the site, if the data returns '', it has failed
        """
        try:
            client.connect((self.domain, int(self.port)))
            
            # Sending request
            client.send(self.createRequest().encode())

            # Receiving Response
            getResponse = ''

            deadline = time.time() + 20
            while True:
                # Setting timeout
                client.settimeout(deadline - time.time())
                data = client.recv(4096).decode()
                if ( len(data) < 1 ) :
                    break
                getResponse += data
        except (socket.error, UnicodeDecodeError, ssl.SSLCertVerificationError) as err:
            # Find out the error
            #print(self.domain, self.request_uri, " has errored due to ", err, "\n")
            getResponse = ''
        
        # Closing Socket
        client.close()

        return getResponse


    def createRequest(self):
        """
        createRequest is a helper function to construct_connection.  Forms the desired headers to return a HTTP GET request for crawling
        
        self: the class parameters

        Return: the generated GET Request message
        """
        # Creating Request
        hostHeader = "Host: " + self.domain + "\r\n"
        connectionHeader = "Connection: close\r\n"
        getRequest = "GET " + self.request_uri + " HTTP/1.1\r\n" + hostHeader + connectionHeader + "\r\n"
        
        return getRequest


    def construct_connection(self):
        """
        construct_connection serves as the central function for sending and receving HTTP traffic.  It determines whether socket
        will be wrapped or not, sends requests, handles request errors, forms request (with helper createRequest), sends request,
        and receives input

        self: the class parameters

        Return: 1 if fails and 0 if success.  If successful self.response is defined
        """
        # Result
        result = 0

        # Construct Base Socket
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # IF HTTPS
        if self.protocol == 'https':
            # Creating SSL Socket
            context = ssl.create_default_context()
            # context.options &= ~ssl.OP_NO_SSLv3
            client = context.wrap_socket(client, server_hostname=self.domain)

        getResponse = self.send_receive(client)
        
        # Splitting response
        response = getResponse.split('\r\n\r\n',1)
        
        if getResponse != '':
            # Assigning response header to self
            self.response_header = response[0]
            self.response_body = response[1]
        else:
            result = 1

        return result


    def limitDomain(self, href):
        """
        insideDomain is a support function for soup which determines if the imposed domain_limit boolean is correct
        Ex: if we enable domain_limit and the href domain matches the class domain it is True

        self: the class parameters
        href: A full URL
        
        Return: True if the same domain, False if not the same domain
        """
        href_domain = parseURL(href)[1]
        if href_domain == self.domain and self.limit_domain == 1:
             return True
        elif href_domain != self.domain and self.limit_domain == 0:
            return True
        else:
            return False


    def soup(self, VALIDPATHS, todoLinks):
        """
        soup serves as the central function for parsing response bdoy data.  It locates the URLs on the site and the emails and
        adds them to their respective lists: TODOLINKS AND EMAILS

        self: the class parameters
        VALIDPATHS: a shared parameter with the other process to inform it real-time of valid paths found
        todoLinks: the links that crawler needs to traverse

        Return: Nothing, but will add to the URLS and todoLinks
        """
         # Create Soup
        soup = BeautifulSoup(self.response_body, 'lxml')

        # Find TODOLINKS and EMAILS
        for hrefParent in soup.find_all(['a', 'link']): # Gathers both 'a' tags and 'link' tags
            if hrefParent.has_attr('href') and len(hrefParent.get('href')) > 1 and hrefParent.get('href')[0] != '#':
                href = hrefParent.get('href') # Either the full URL, Request-URI

                # EMAIL, hashtag, href javascript tags
                if "mailto:" in href or href[0] == '#' or href[0] == '?' or 'javascript:' in href or 'tel:' in href:
                    continue

                # TODOLINK
                elif href[0] == '/': # If not complete URL, make complete
                    href = self.protocol + "://" + self.domain + href
                
                # Finally, add link if not in visited or todo
                if href[0:4] == 'http' and href not in todoLinks and href not in VISITEDLINKS and href[:-1] not in VISITEDLINKS and href[:-1] not in todoLinks and self.limitDomain(href):
                    todoLinks.add(href)
                    VALIDPATHS.append(href)


    def brute_parse(self, VALIDPATHS):
        """
        brute_soup is the function for examining response headers to see if a path is valid

        self: the class parameters
        VALIDPATHS: the shared paramter between processes that holds successful paths

        Return: Nothing, just adds to VALIDPATHS
        """
        # Splitting response for headers    
        if '200' in self.response_header[:14]:
            VALIDPATHS.append(self.url)



def parseURL(url):
    """
    parseURL is a support function for several methods and it takes in a url and breaks it into a list of three paramters:
    protocol, domain, and request_uri

    url: a full URL

    Return: a list with protocol at the first index, domain at the second index, and request_uri at the third
    """
    divided_url = url.split("/")
    protocol = divided_url[0][:-1]
    domain = divided_url[2]
    request_uri = "/" + "/".join(divided_url[3:])

    # Creating list
    list = [protocol, domain, request_uri]
    return list


def parsePath(link):
    """
    parsePath is a helper fuction for path_worker.  It takes in a link and parses the URL for paths

    link: a full URL

    Return: A set containing all paths from that link
    """
    # Create SET
    pathSet = set()

    # Loop through divided link
    divided_link = link.split("/")
    for path in divided_link[3:]:
        # Account for Queries
        if '?' in path:
            path = path[:path.find('?')]
        # Account for Fragments
        elif '#' in path:
            path = path[:path.find('#')]
        elif path != divided_link[len(divided_link) - 1]:
            path += "/"

        # Lastly check if empty
        if len(path) != 0:
            pathSet.add(path)

    return pathSet

    
def crawler_worker(url, depth, limit_domain, port, VALIDPATHS):
    """
    crawler_worker is the main crawling function that constructs connections, parses output, and creates more threads
    These threads will run on on crawler_worker until either depth reaches 0 or no links are found.

    url: the full URL of the crawled site
    depth: scope of traversal
    limit_domain: Stay inside first domain: 1, Don't care: 0
    VALIDPATHS: a shared parameter with the other process to inform it real-time of valid paths found
    
    Return: Nothing
    """
    # Add to VISITEDLINKS
    VISITEDLINKS.add(url)
    # Reset todoLinks
    todoLinks = set()
    
    # Form crawler
    crawler = Crawler(url, depth, limit_domain, port)
    
    # Form connection and receive document
    if crawler.construct_connection() == 1:
        # Error has occured
        print("The initial crawler FAILED!  Review your inputs and/or check if the site is down")
        return
    
    # Parse document
    crawler.soup(VALIDPATHS, todoLinks)

    # End if depth is 0
    if crawler.depth == 0:
        return

    # Multi-Threading execution
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=70)
    futures = []
    for i in range(len(todoLinks)):
        futures.append(executor.submit(crawler_worker, todoLinks.pop(), int(depth) - 1, limit_domain, VALIDPATHS, todoLinks))
    concurrent.futures.wait(futures)


def validpath_worker(VALIDPATHS, FINISHED):
    """
    path_worker is the second process that adds paths 

    VALIDPATHS: a shared parameter with the other process to inform it real-time of valid paths found
    FINISHED: Check if the web crawler is finished

    Return: Nothing, but will write out all unique parsed paths to file
    """
    file = open("validpaths.list", 'w')
    written_paths = set()
    
    time.sleep(10)
    # Loop Start
    while True:
        time.sleep(.1)
                
        # Checking if web crawler FINISHED
        if FINISHED[0] == 1:
            print("\nFinished Writing Paths...")
            file.close()
            break
        elif len(VALIDPATHS) == 0:
            time.sleep(10)
            continue

        # Calling helper
        link = VALIDPATHS.pop()
        pathSet = parsePath(link)

        for path in pathSet:
            if path not in written_paths:
                file.write(path)
                written_paths.add(path)
                file.write("\n")


def bruteforce_worker(url, builderPaths, pathslist, VALIDPATHS):
    """
    bruteforce_worker is the threading function used for applying paths to a specified url

    url: the URL to apply paths to
    builderPaths: the paths that will be used for starting off 
    pathlist: the list of paths to bruteforce with (serves as a dictionary)
    VALIDPATHS: the shared paramter between processes that holds successful paths
    
    Returns: Nothing
    """
    i = 0
    while i < len(builderPaths):
        # Form crawler
        crawler = Crawler(url, 4, True, 83)

        for path in pathslist:
            # Modify request_uri
            crawler.request_uri = "/" + builderPaths[i] + "/" + path

            # Form connection and receive document
            if crawler.construct_connection() == 1:
                # Error has occured
                print("The initial crawler FAILED!  Review your inputs and/or check if the site is down")
                return
            
            crawler.brute_parse(VALIDPATHS)
            
            



def start_crawler(VALIDPATHS, FINISHED):
    """
    start_crawler is the initiator of the crawler threads.  Takes in a list of URLs to scan

    VALIDPATHS: a shared parameter with the other process to inform it real-time of valid paths found
    FINISHED: a shared paramter with the other process to inform it when start_crawler process has ended
    
    Return: Nothing
    """
    # URL
    url = "http://csec380-core.csec.rit.edu"

    # Starting Time
    startTime = time.time()
    
    print("Starting crawling of: http://csec380-core.csec.rit.edu:83")

    # Start crawler worker
    crawler_worker(url, 4, True, 83, VALIDPATHS)

    # Ending Time
    print("\n\nThe total run time for http://csec380-core.csec.rit.edu:83: ", str(time.time() - startTime))

    # Now let's use the paths.list we generated prior in act3
    pathslist = set()
    file = open("paths.list", 'r')
    lines = file.readlines()

    for line in lines:
        line = line.replace("\n","")
        pathslist.add(line)

    # Let's also take our wonderful validpaths we just generated from the file
    validpathslist = set()
    file = open("validpaths.list", 'r')
    lines = file.readlines()

    for line in lines:
        line = line.replace("\n","")
        validpathslist.add(line)

    # Enable Threading for bruteforcing
    futures = []
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=70)
    for group in more_itertools.grouper(5, validpathslist):
        futures.append(executor.submit(bruteforce_worker, url, group, pathslist, VALIDPATHS))
    
    # Root of the site
    futures.append(executor.submit(bruteforce_worker, url, '/', pathslist, VALIDPATHS))

    concurrent.futures.wait(futures)

    FINISHED[0] = 1
    
    return


def main():
    """
    main the entrance URL Harvester

    return: Nothing
    """
    # List of Paths
    paths = []

    # Gathering list from file
    file = open("paths.list", 'r')

    for row in file.readlines():
        paths.append(row)

    file.close()

    # Starting Time
    startTime = time.time()

    # Let's share resources, Manager
    manager = multiprocessing.Manager()
    VALIDPATHS = manager.list()
    FINISHED = manager.list()
    FINISHED.append(0)

    # Starting Time
    startTime = time.time()

    # Creating processes
    crawler = multiprocessing.Process(target=start_crawler, args=(VALIDPATHS, FINISHED,))
    path_writing = multiprocessing.Process(target=validpath_worker, args=(VALIDPATHS, FINISHED))
    
    print("Starting Processes")
    # starting processes
    crawler.start()
    path_writing.start()
  
    # process IDs
    print("ID of main crawler process: {}".format(crawler.pid))
    print("ID of path writing process: {}".format(path_writing.pid))
  
    # wait until processes are finished
    crawler.join()
    path_writing.join()
  
    # both processes finished
    print("Both processes finished execution!")
    
    # Ending Time
    print("\n\nThe total run time: ", str(time.time() - startTime))

    return

main()
