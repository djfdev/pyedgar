import requests
import re
import sys
import csv
import json
import click
import time

from urlparse import urljoin
from urllib import urlencode
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

# Output CSV headers
HEADERS = [
    'ticker',
    'event_date',
    'filing_type',
    'search_term',
    'filing_date',
    'report_date',
    'url'
]
DELIMITER = ','
BASE_URL = 'https://www.sec.gov'
SEARCH_URL = BASE_URL + '/cgi-bin/browse-edgar'
RANGE = 10
RATE_LIMIT = 1
TICKER_SYMBOL = '.'

@click.command()
@click.option('--input', help='Path to CSV search input file', required=True)
@click.option('--output', help='Path to CSV output file', required=True)

def main(input, output):
    with open(input, 'rb') as infile, open(output, 'wb') as outfile:
        writer = csv.writer(outfile, delimiter = DELIMITER)
        reader = csv.reader(infile, delimiter = DELIMITER)

        reader.next() # skip the old headers
        writer.writerow(HEADERS) # write the new headers

        for row in reader:
            writer.writerow(process_row(row))
            sys.stdout.write(TICKER_SYMBOL)
            sys.stdout.flush()
            time.sleep(RATE_LIMIT)

def process_row(row):
    ticker = row[0]
    event_date = row[1]
    filing_type = row[2]
    search_terms = row[3].split('|')

    result = find_filing(ticker, event_date, filing_type, search_terms)

    return [
        ticker,
        event_date,
        filing_type,
        [term.encode('utf8') for term in search_terms],
        result.get('filing_date'),
        result.get('report_date'),
        result.get('url')
    ]

def find_filing(ticker, event_date, type, search_terms):
    filing_url = None
    start = 0

    while not filing_url:
        # grab the first page of search results
        filings = search_filings(ticker, type, search_terms, start)

        # if no results were found, return None
        if not filings:
            return {}

        # otherwise, let's look for the next filing within the provided range
        date = parse_date(event_date)
        margin = timedelta(days=RANGE)
        for filing in filings:
            filing_date = parse_date(filing['filing_date'])
            if date <= filing_date <= date + margin:
                filing_url = filing['url']
                break

        start += 100

    filing_html = requests.get(filing_url).content
    return parse_filing(filing_html)

def search_filings(ticker, type, search_terms, start=None):
    query = {
        'CIK': ticker,
        'type': type,
        'start': start,
        'count': 100,
        'owner': 'exclude'
    }

    html_doc = requests.get(SEARCH_URL, params=query).content
    soup = BeautifulSoup(html_doc, 'html.parser')
    search_results_container = soup.find('div', id='seriesDiv')
    
    if not search_results_container:
        return []
    rows = search_results_container.find_all('tr')
    rows.pop(0) # remove the table header row
    results = []

    for row in rows:
        cells = row.find_all('td')
        description = cells[2].text
        match = None

        for term in search_terms:
            if description.find(term) > -1:
                match = True
            else:
                p = re.compile(term)
                if p.match(description):
                    match = True

        if match:
            results.append({
                'url': format_url(cells[1].find('a').get('href')),
                'filing_date': clean_date(cells[3].text)
            })
    
    reversed(results)
    return results

def parse_filing(html_doc):
    soup = BeautifulSoup(html_doc, 'html.parser')
    result = {}

    path = soup.table.find_all('a')[0].get('href')
    result['url'] = format_url(path)

    filing_date_node = soup.find('div', text='Filing Date')
    result['filing_date'] = clean_date(filing_date_node.find_next_sibling().text)

    report_date_node = soup.find('div', text='Period of Report')
    if report_date_node:
        result['report_date'] = clean_date(report_date_node.find_next_sibling().text)
    else:
        result['report_date'] = None

    return result

def format_url(path):
    return urljoin(BASE_URL, path)

def clean_date(str):
    return str.replace('-', '')

def parse_date(datestring):
    return datetime.strptime(datestring, '%Y%m%d')

if __name__ == '__main__':
    main()
