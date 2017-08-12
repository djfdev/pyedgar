import csv
import json
import click
from lib import find_filing

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

if __name__ == '__main__':
    main()
