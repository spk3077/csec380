# Sean Kells
# Python Script for Requesting 'https://csec.rit.edu'
import requests

# Sending and retrieving a response from an HTTP GET
r = requests.get('https://csec.rit.edu')

# Did we suceed?
if r.status_code == 200:
    print("We successfully received a 200 response!")
else:
    print("Our GET Request Failed!.  The error was ", r.status_code)