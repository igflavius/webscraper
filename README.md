# Web Scraper

The main goal of program is to scrape urls based on keywords.\
It is more easy to find what you looking for.

#### Usage

To scan default http with default 100 threads

```
python3 web.py -i ip.txt -p path.txt
```

To scan https with 200 threads

```
python3 web.py -i ip.txt -p path.txt --port 443 --ssl --threads 200
```
