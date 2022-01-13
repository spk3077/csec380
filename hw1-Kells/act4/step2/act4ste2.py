# Sean Kells
# Python Script for Scanning for anonymous HTTP Proxies
# act4ste2.py (string) startIP (string) endIP
import requests, sys, re, math, time
from ipaddress import ip_address
from threading import Thread
import concurrent.futures


def findIPs(start, end):
    """
    findIPs function returns a list of all valid ip addresses from the start ip and end ip provided

    start: starting ip address for the range
    end: ending ip address for the range

    return: list of ip addresses
    """
    start = ip_address(start)
    end = ip_address(end)
    result = []
    while start <= end:
        result.append(str(start))
        start += 1
    return result


def scanIP(ip):
    """
    scanIP function scans each ip address for a proxy
    NOTE The function is set up to only print working proxies

    ip: An IPv4 Address

    return: Nothing
    """
    proxy8080 = {"http" : "http://" + ip + ":8080"}
    proxy80 = {"http" : "http://" + ip + ":80"}
    try:
        r = requests.get('http://www.bing.com', timeout=5, proxies=proxy8080)
        if r.headers.get('Set-Cookie') is not None and r.headers.get('P3P') is not None: # NOTE We can't just check status code, sometimes retrieves 200 despite not being a proxy
            if r.headers.get('Via') is not None or r.headers.get('X-Forwarded-For') is not None: # Via and X-Forwarded-For are both possible indications of proxy (could be reverse too!)
                print("Found Proxy: ", ip + ":8080")
            else:
                print("Found Potential Anonymous Proxy: ", ip + ":8080")
    except:
        # Do nothing
        pass

    try:
        r = requests.get('http://www.bing.com', timeout=5, proxies=proxy80)
        if r.headers.get('Set-Cookie') is not None and r.headers.get('P3P') is not None:
            if r.headers.get('Via') is not None or r.headers.get('X-Forwarded-For') is not None:
                print("Found Proxy: ", ip + ":80")
            else:
                print("Found Potential Anonymous Proxy: ", ip + ":80")
    except:
        # Do nothing
        pass


def main():
    """
    main function where the arguments are collected from the CLI
    and passed into subsidary functions

    argv[1]: start ip
    argv[2]: end ip
    return: Nothing
    """
    if len(sys.argv) != 3:
        print("ERROR: Two arguments are required: 'act4ste2.py (string) startIP (string) endIP'")
        return 1
    startIP = sys.argv[1]
    endIP = sys.argv[2]
    start_check= re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", startIP)
    end_check = re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", endIP)
    if start_check == None or end_check == None:
        print("ERROR: Your IP arguments should look like x.x.x.x")
        return 1
    
    # Defining ipList and IPs assigned to each process
    ipList = findIPs(startIP, endIP)
    ipPerThread = math.ceil(len(ipList) / 10)
    if ipPerThread == 0:
        print("ERROR: The endIP should be larger than the startIP")
        return 1

    # Time before IP Processing
    startTime = time.time()

    # Multi-Processing execution of the method scanIP(ipList)
    executor = concurrent.futures.ThreadPoolExecutor(len(ipList))
    futures = [executor.submit(scanIP, ip) for ip in ipList]
    concurrent.futures.wait(futures)
    
    # Ending time
    print("The total run time is: ", str(time.time() - startTime))
    return 0


main()
