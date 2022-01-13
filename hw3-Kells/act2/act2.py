# Sean Kells
# CSEC.380.01
# Professor Chaim Sanders
# act2.py - Crawls to collect emails from a specified site.  Writes to a CSV

# How to Use:
#
# docker-compose build --no-cache # Building Image
# docker-compose up # Running Image

import socket, ssl, concurrent.futures, time, multiprocessing, re
from bs4 import BeautifulSoup

VISITEDLINKS = set()

class Crawler:

    def __init__(self, url, port, depth, limit_domain):
        """
        self.url: the full URL of the crawled site
        self.port: the port of the crawled site
        self.depth: scope of traversal
        self.limit_domain: Stay inside first domain: 1, Don't care: 0
        self.protocol: http or https
        self.domain: the domain the crawl
        self.request_uri: the path and potential paramters
        self.response: the body of the response
        
        """
        self.url = url
        self.port = port
        self.depth = depth
        self.limit_domain = limit_domain

        protDomReqList = parseURL(url)
        self.protocol = protDomReqList[0]
        self.domain = protDomReqList[1]
        self.request_uri = protDomReqList[2]

        # Will be defined during data retrieval
        self.response = ''


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
        # Returned result
        result = 0

        # Construct Base Socket
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # IF HTTPS
        if self.protocol == 'https':
            # Creating SSL Socket
            context = ssl.create_default_context()
            context.options &= ~ssl.OP_NO_SSLv3
            client = context.wrap_socket(client, server_hostname=self.domain)

        client.connect((self.domain, int(self.port)))

        try:
            # Sending request
            client.send(self.createRequest().encode())

            # Setting timeout
            client.settimeout(time.time() + 10)

            # Receiving Response
            getResponse = ''

            while True:
                data = client.recv(4096).decode()
                if ( len(data) < 1 ) :
                    break
                getResponse += data

        except socket.error as err:
            # Find out the error
            print("An error was detected with: " + self.domain + self.request_uri)
            print(err)

            result = 1

        if result == 0:
            # Assigning response body to self
            self.response = getResponse.split('\r\n\r\n',1)[1]

        # Closing Socket
        client.close()

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


    def soup(self, EMAILS, todoLinks):
        """
        soup serves as the central function for parsing response bdoy data.  It locates the URLs on the site and the emails and
        adds them to their respective lists: TODOLINKS AND EMAILS

        self: the class parameters
        EMAILS: the shared list between processes of emails
        todoLinks: the links the crawler needs to traverse

        Return: Nothing, but will add to the EMAILS and todoLinks
        """
         # Create Soup
        soup = BeautifulSoup(self.response, 'lxml')

        # Find TODOLINKS and EMAILS
        for hrefParent in soup.find_all(['a', 'link']): # Gathers both 'a' tags and 'link' tags
            if hrefParent.has_attr('href') and len(hrefParent.get('href')) > 1 and hrefParent.get('href')[0] != '#':
                href = hrefParent.get('href') # Either the full URL, Request-URI or Email

                # EMAIL
                if "mailto" in href:
                    emails = re.findall("([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)", href)
                    for email in emails:
                        EMAILS.append(email)
                    continue

                # DEPTH == 0
                elif self.depth == 0:
                    continue

                # TODOLINK
                elif href[0] == '/': # If not complete URL, make complete
                    href = self.protocol + "://" + self.domain + href
                
                # Finally, add link if not in visited or todo
                if href not in todoLinks and href not in VISITEDLINKS and href[:-1] not in VISITEDLINKS and href[:-1] not in todoLinks and self.limitDomain(href):
                    todoLinks.add(href)


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

    
def crawler_worker(url, port, depth, limit_domain, EMAILS, todoLinks):
    """
    crawler_worker is the main crawling function that constructs connections, parses output, and creates more threads
    These threads will run on on crawler_worker until either depth reaches 0 or no links are found.

    url: the full URL of the crawled site
    port: the port of the crawled site
    depth: scope of traversal
    limit_domain: Stay inside first domain: 1, Don't care: 0
    EMAILS: shared list resource containing all unwritten emails
    
    Return: Nothing
    """
    # Add to VISITEDLINKS
    VISITEDLINKS.add(url)
    # Reset todoLinks
    todoLinks = set()
    
    # Form crawler
    crawler = Crawler(url, port, depth, limit_domain)
    
    # Form connection and receive document
    if crawler.construct_connection() == 1:
        # Error has occured
        print("The initial crawler FAILED!  Review your inputs and/or check if the site is down")
        return
    
    # Parse document
    crawler.soup(EMAILS, todoLinks)

    # End if depth is 0
    if crawler.depth == 0:
        return

    # Multi-Threading execution
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=50)
    futures = []
    for i in range(len(todoLinks)):
        futures.append(executor.submit(crawler_worker, todoLinks.pop(), port, int(depth) - 1, limit_domain, EMAILS, todoLinks))
    concurrent.futures.wait(futures)


def email_worker(depth, EMAILS):
    """
    email_work is the second process meant to add emails while threading is occuring in the other

    depth: the initially defined depth
    EMAILS: shared list resource containing all unwritten emails

    Return: Nothing, but will write out all EMAILS to emaildepth#.txt
    """
    filename = "emaildepth" + str(depth) + ".txt"
    file = open(filename, 'w')
    time.sleep(5)

    written = set()
    # Loop Start
    while True:
        time.sleep(.2)
        EMAIL_LEN = len(EMAILS)
        if EMAIL_LEN == 0:
            time.sleep(5)
            if len(EMAILS) == 0:
                print("\nFinished Writing Emails")
                break

        email = EMAILS.pop(0)

        #To prevent duplicates
        if email not in written:
            file.write(email)
            written.add(email)
            file.write("\n")



def startcrawler(url, port, depth, limit_domain):
    """
    startcrawler is the initiator of the crawler process and the email process

    url: the full URL of the crawled site
    port: the port of the crawled site
    depth: scope of traversal
    limit_domain: Stay inside first domain: 1, Don't care: 0
    
    Return: Nothing
    """

    # Note printed to USER
    print("\n** NOTE: THE PROGRAM IS SUITED FOR HIGH DEPTH RATES, MAY NOT BE IDEAL FOR SHORT DEPTH RATES **\n")

    # Let's share resources, Manager
    manager = multiprocessing.Manager()
    EMAILS = manager.list()

    todoLinks = set()

    # Creating processes
    crawler = multiprocessing.Process(target=crawler_worker, args=(url, port, depth, limit_domain, EMAILS, todoLinks))
    email_writing = multiprocessing.Process(target=email_worker, args=(depth, EMAILS,))
  
    # starting processes
    crawler.start()
    email_writing.start()
  
    # process IDs
    print("ID of process p1: {}".format(crawler.pid))
    print("ID of process p2: {}".format(email_writing.pid))
  
    # wait until processes are finished
    crawler.join()
    email_writing.join()
  
    # both processes finished
    print("Both processes finished execution!")

    return


def main():
    """
    main the entrance of the email searching user-agent
    Three arguments are required: 'act2.py (string) URL (int) port (int) Depth'")

    arg: URL
    arg: Port
    arg: Depth

    return: Nothing
    """
    # NOTE These inputs can be used alternatively
    # url = input("Please enter the starting URL(ex:https://www.rit.edu): ")
    # if url == '':
    #     url = "https://www.rit.edu"

    # port = input("Please enter the port(ex:443): ")
    # if port == '':
    #     port = 443

    # depth = input("Please enter the depth(ex:0-4): ")
    # if depth == '':
    #     depth = 1

    # limit_domain = input("Will we limit this domain?(1: True, 0: False) ")
    # if limit_domain == '' or limit_domain == '1':
    #     limit_domain = True
    # else:
    #     limit_domain = False

    # Defining Core Parameters
    url = "https://www.rit.edu"
    port = 443
    limit_domain = True

    # DEPTH 0
    startTime = time.time()
    # Starting crawler
    startcrawler(url, int(port), 0, limit_domain)
    # Ending time
    print("\n\nThe total run time for DEPTH 0 is: ", str(time.time() - startTime))


    # DEPTH 1
    startTime = time.time()
    # Starting crawler
    startcrawler(url, int(port), 1, limit_domain)
    # Ending time
    print("\n\nThe total run time for DEPTH 1 is: ", str(time.time() - startTime))


    # DEPTH 2
    startTime = time.time()
    # Starting crawler
    startcrawler(url, int(port), 2, limit_domain)
    # Ending time
    print("\n\nThe total run time for DEPTH 2 is: ", str(time.time() - startTime))


    # DEPTH 3
    startTime = time.time()
    # Starting crawler
    startcrawler(url, int(port), 3, limit_domain)
    # Ending time
    print("\n\nThe total run time for DEPTH 3 is: ", str(time.time() - startTime))


    # DEPTH 4
    startTime = time.time()
    # Starting crawler
    startcrawler(url, int(port), 4, limit_domain)
    # Ending time
    print("\n\nThe total run time for DEPTH 4 is: ", str(time.time() - startTime))

    return

main()
