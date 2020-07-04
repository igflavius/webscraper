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
import re
from bs4 import BeautifulSoup as BS
from urllib3.exceptions import InsecureRequestWarning
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
    parser.add_argument("-p", "--path", dest="path", type=check_file, required=True, help='path list file',)
    parser.add_argument("-l", "--log", dest="log", default="results.txt", help="save the results (default: results.txt)")
    parser.add_argument("--port", dest="port", type=int, default=80, help="port number (default: 80)")
    parser.add_argument("-t", "--threads", dest="num_threads", type=int, default=100, help="number of threads (default: 100)")
    parser.add_argument("--ssl", dest="ssl", action="store_true", help="use ssl (default: none)")
    arg = parser.parse_args()
    return arg

def main():
    """ 
        This is where we begin. We create a nested loop with 
        itertools.product() and we put in the queue().
        And setup first part to break the loop. 
    """
    threads = []
    num_threads = arg.num_threads
    port = str(arg.port)
    
    # Multithread
    for thread in range(num_threads):
        th = threading.Thread(target = scanner, daemon=True)
        threads.append(th)
        th.start()

    with open(arg.ip) as file1, open(arg.path) as file2:
        for url, path in itertools.product(file1, file2):
            url = url.rstrip().strip()
            path = path.rstrip().strip()
            threads_queue.put(url + ":" + port + path)

    for thread in threads:
        threads_queue.put(None)

    for thread in threads:
        thread.join()

def scanner():
    """ 
        In the scanner() function we get url from the queue.
        And find the match in the urls.
        And break the loop with an fif statment.
    """    
    logging.basicConfig(format='%(message)s', level=logging.INFO, handlers=[logging.FileHandler(arg.log), logging.StreamHandler(sys.stdout)])

    headers = requests.utils.default_headers()
    headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36'})

    match = ["Powered by Wordpress"]

    while True:
        url = threads_queue.get()
        ssl = arg.ssl
       
        if url is None:
            break
        if ssl is False:         
            try:
                req = requests.get("http://" + url, headers=headers, timeout=3, allow_redirects=True, verify=False)
                soup = BS(req.text, 'html.parser')

                if soup.find_all(string=re.compile('|'.join(match))):
                    logging.info("http://%s", url)
            except requests.RequestException:
                pass
        else:
            try:
                req = requests.get("https://" + url, headers=headers, timeout=3, allow_redirects=True, verify=False)
                soup = BS(req.text, 'html.parser')

                if soup.find_all(string=re.compile('|'.join(match))):
                    logging.info("https://%s", url)
            except requests.RequestException:
                pass


if __name__ == '__main__':
    try:
        threads_queue = queue.Queue(maxsize=0)
        arg = arguments()
        main()
    except KeyboardInterrupt:
        sys.exit(0)
        print("[+] Ctrl + C ... Exiting")