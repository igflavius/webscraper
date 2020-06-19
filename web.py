#!/usr/bin/env python3

import argparse
import requests
import logging
import itertools
from multiprocessing import Pool
from bs4 import BeautifulSoup
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

    scanner(args.ip, args.path, args.log)

def debug(info, log):
    logging.basicConfig(format='%(message)s', filename=log, level=logging.INFO)
    logging.info(info)

def scanner(ip, path, log):

    headers = requests.utils.default_headers()
    headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36'})

    match = ["Default Web Site Page", "It works!", "Univention Portal"]

    with open(ip) as f1, open(path) as f2:
            for url, uri in itertools.product(f1, f2):
                (url, uri) = url.rstrip(), uri.rstrip()
                try:
                    req = requests.get(url + uri, headers=headers, timeout=3, allow_redirects=True, verify=False)
                    session = requests.session()
                    soup = BeautifulSoup(req.text, 'html.parser')

                    if soup.findAll(string=match):
                        print("-> " + url + uri)
                        debug(url + uri, log)
                except requests.ConnectionError:
                    pass

if __name__ == '__main__':
    main()


