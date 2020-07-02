#!/usr/bin/python3

__author__ = "Flavius Ion"
__email__ = "igflavius@odyssee.ro"
__license__ = "MIT"
__version__ = "1.0"

import argparse
import requests
import logging
import itertools
import threading
import queue
import sys
import os
from bs4 import BeautifulSoup as BS
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def check_file(file):
    """
        Checks if file exists
    """
    if not os.path.exists(file):
        raise argparse.ArgumentTypeError("{0} does not exist".format(file))
    return file    

def arguments():
    """
        Obviously these are the arguments.
    """    
    parser = argparse.ArgumentParser(prog='web.py', description='Web Scraper v1.0')
    parser.add_argument("-i", "--ip", dest="ip", type=check_file, required=True, help='ip list file')
    parser.add_argument("-u", "--uri", dest="uri", type=check_file, required=True, help='uri list file',)
    parser.add_argument("-l", "--log", dest="log", default="results.txt", help="save the results (default: results.txt)")
    parser.add_argument("-p", "--port", dest="port", type=int, default=80, help="port number (default: 80)")
    parser.add_argument("-t", "--threads", dest="num_threads", type=int, default=100, help="number of threads (default: 100)")
    parser.add_argument("-s", "--ssl", dest="ssl", action="store_true", help="use ssl (default: none)")
    arg = parser.parse_args()
    return arg

def main():
    """
        This is where we begin. We create a nested loop with 
        itertools.product() and we put in the queue().
    """
    threads = []
    num_threads = arg.num_threads
    port = str(arg.port)
    
    # Multithread
    for i in range(num_threads):
        th = threading.Thread(target = scanner, daemon=True)
        threads.append(th)
        th.start()

    with open(arg.ip) as f1, open(arg.uri) as f2:
        for url, uri in itertools.product(f1, f2):
            url = url.rstrip().strip()
            uri = uri.rstrip().strip()
            threads_queue.put(url + ":" + port + uri)
    """
        This is the first part to break the loop.
        We add None to the list. To break the loop in 
        the scanner() function with an if statement.
    """ 
    for thread in threads:
        threads_queue.put(None)

    for thread in threads:
        thread.join()

def scanner():
    """ 
        In the scanner() function we get url from the queue.
        and find the string in the urls.
    """    
    logging.basicConfig(format='%(message)s', level=logging.INFO, handlers=[logging.FileHandler(arg.log), logging.StreamHandler(sys.stdout)])

    headers = requests.utils.default_headers()
    headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36'})

    match = ["Powered by WordPress"]

    while True:
        url = threads_queue.get()
        ssl = arg.ssl
        """
            This is the second part to break the loop.
            I'll try to find a better way to try break the loop.
        """        
        if url is None:
            break
        if ssl is False:         
            try:
                req = requests.get("http://" + url, headers=headers, timeout=3, allow_redirects=True, verify=False)
                soup = BS(req.content, 'html.parser')

                if soup.find_all(string=match):
                    logging.info("http://" + url)
            except requests.RequestException as err:
                pass
        else:
            try:
                req = requests.get("https://" + url, headers=headers, timeout=3, allow_redirects=True, verify=False)
                soup = BS(req.content, 'html.parser')

                if soup.find_all(string=match):
                    logging.info("https://" + url)
            except requests.RequestException as err:
                pass

if __name__ == '__main__':
    try:
        threads_queue = queue.Queue(maxsize=0)
        arg = arguments()
        main()
    except KeyboardInterrupt:
        sys.exit(0)
        print("[+] Ctrl + C ... Exiting")



