# pyedgar

CLI for scraping data from the U.S. Securities and Exchange Commision's EDGAR database.

## Requirements

- Python 2.7
- pip

## Download

```
git clone https://github.com/djfdev/pyedgar.git
```

Or, simply export a zipfile from the the Github repository and unpack it somewhere on your machine.

## Setup

This tool uses a number of 3rd-party libraries, which you'll need to install to get up and running.

```
pip install -r requirements.txt
```

If you have permission denied, you may have to install with:

```
sudo pip install -r requirements.txt
```

## CLI usage

The CLI accepts arguments to specify the paths of (1) input file, and (1) output file. These are both CSV files. So if you have your input file located inside of the pyedgar folder, you might type:

```
python cli.py --input="./input.csv" --output="./output.csv"
```

### Input format

The input file should be a CSV with the following format:

```
ticker,event_date,filing_type,search_term
AAPL,20140228,8-K,5.07|items 5
```

Note the `search_term` column: this column accepts a pipe-delimited list of strings that the scraper will attempt to match a filings description against. If the term cannot be found as a string, the program will retry it as a *regular expression*. This allows you to do really powerful and flexible pattern matching against the search results.

## License

MIT

