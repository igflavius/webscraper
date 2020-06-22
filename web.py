#!/usr/bin/env python3

import argparse
import requests
import logging
import itertools
import threading
import queue
from bs4 import BeautifulSoup as BS
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def main(): 
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--ip", dest="ip", help='ip list file', required=True)
    parser.add_argument("-u", "--uri", dest="path", help='uri list file', required=True)
    parser.add_argument("-l", "--log", dest="log", help="log file", required=True)
    parser.add_argument("-p", "--port", dest="port", help="port number")
    parser.add_argument("-s", "--ssl", dest="ssl", help="use ssl or no")
    args = parser.parse_args()

    # scanner(args.ip, args.path, args.log)

def debug(info):
    logging.basicConfig(format='%(message)s', filename='vuln.txt', level=logging.INFO)
    logging.info(info)

def scanner():
    
    while True:
        url = threads_queue.get()
        if url is None:
            break

        url = url.strip()

        headers = requests.utils.default_headers()
        headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36'})

        match = ["Test", "It works!", "Univention Portal"]

        try:
            req = requests.get(url, headers=headers, timeout=3, allow_redirects=True, verify=False, stream=True)
            soup = BS(req.text, 'html.parser')

            if soup.findAll(string=match):
                print("-> " + url)
                debug(url)
        except requests.RequestException as e:
            pass

if __name__ == '__main__':
    
    # parser = argparse.ArgumentParser()
    # parser.add_argument("-i", "--ip", dest="ip", help='ip list file', required=True)
    # parser.add_argument("-u", "--uri", dest="path", help='uri list file', required=True)
    # parser.add_argument("-l", "--log", dest="log", help="log file", required=True)
    # parser.add_argument("-p", "--port", dest="port", help="port number")
    # parser.add_argument("-s", "--ssl", dest="ssl", help="use ssl or no")
    # args = parser.parse_args()

    args = main.parse_args()

    threads = []
    threads_queue = queue.Queue()

    for i in range(50):
        th = threading.Thread(target = scanner)
        threads.append(th)
        th.start()

    with open(args.ip) as f1, open(args.path) as f2:
        for url, uri in itertools.product(f1, f2):
            url = url.rstrip()
            uri = uri.rstrip()
            threads_queue.put(url + uri)

    for j in threads:
        threads_queue.put(None)

    for j in threads:
        j.join()



