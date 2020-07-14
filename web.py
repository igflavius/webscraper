#!/usr/bin/python3

__author__ = "Flavius Ion"
__email__ = "igflavius@odyssee.ro"
__license__ = "MIT"
__version__ = "v1.3"

import argparse
import requests
import logging
import itertools
import threading
import queue
import sys
import os
import re
from bs4 import BeautifulSoup
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
    parser = argparse.ArgumentParser(add_help=False, description='Web Scraper ' + __version__)
    required = parser.add_argument_group('required arguments')
    optional = parser.add_argument_group('optional arguments')
    required.add_argument("-i", "--ip", dest="ip", type=check_file, required=True, help='ip list file')
    required.add_argument("-p", "--path", dest="path", type=check_file, required=True, help='path list file',)
    optional.add_argument("-l", "--log", dest="log", default="results.txt", help="save the results (default: results.txt)")
    optional.add_argument("--port", dest="port", type=int, default=80, help="port number (default: 80)")
    optional.add_argument("--threads", dest="num_threads", type=int, default=100, help="number of threads (default: 100)")
    optional.add_argument("--ssl", dest="ssl", action="store_true", help="use ssl (default: none)")
    optional.add_argument("-h", "--help", action="help", help="show this help message and exit")
    arg = parser.parse_args()
    return arg

def main():
    """ 
        This is where we begin. We create a nested loop with 
        itertools.product() and we put in the queue().
        Set first part to break the loop. 
    """
    threads = []
    num_threads = arg.num_threads
    port = str(arg.port)
    
    # Multithread
    for thread in range(num_threads):
        th = threading.Thread(target = scanner, daemon=True)
        threads.append(th)
        th.start()

    # add url, port and path in queue() 
    with open(arg.ip) as file1, open(arg.path) as file2:
        for url, path in itertools.product(file1, file2):
            url = url.rstrip().strip()
            path = path.rstrip().strip()
            threads_queue.put(url + ":" + port + path)

    # add None to the end queue() to break the loop
    for thread in threads:
        threads_queue.put(None)
    for thread in threads:
        thread.join()

def scanner():
    """ 
        Get urls from the queue.
        And find the keywords in the urls.
        And break the loop with an if statment.
    """    
    logging.basicConfig(format='%(message)s', level=logging.INFO, handlers=[logging.FileHandler(arg.log), logging.StreamHandler(sys.stdout)])

    headers = requests.utils.default_headers()
    headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36'})

    keywords = ["Powered by WordPress", "Powered by Joomla"]

    while True:
        url = threads_queue.get()
        ssl = arg.ssl
       
        if url is None:
            break
        if ssl is False:         
            try:
                req = requests.get("http://" + url, headers=headers, timeout=3, allow_redirects=True, verify=False)
                soup = BeautifulSoup(req.text, 'html.parser')

                if soup.find_all(string=re.compile('|'.join(keywords))):
                    logging.info("http://%s", url)
            except requests.RequestException:
                pass
        else:
            try:
                req = requests.get("https://" + url, headers=headers, timeout=3, allow_redirects=True, verify=False)
                soup = BeautifulSoup(req.text, 'html.parser')

                if soup.find_all(string=re.compile('|'.join(keywords))):
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
        