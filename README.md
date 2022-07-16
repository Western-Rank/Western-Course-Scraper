# scraping

Python script to scrape all UWO courses on the academic calendar.

## Output
Output of script(s) is a `.csv` file in the following format:

```js
course_code|course_name|antirequisites|prerequisites|description|location|extra_info
```

## Usage
All necessary packages can be installed with `pip install -r requirements.txt`.

1. Run `extract.py` to update the list of course categories, located in `categories.txt`.
2. Run `scrape.py` to scrape all current courses related information. Output is written to `output.csv`.

Optional flags for `scrape.py` are as follows.
- `ANIMATE`: Controls loading animation while process is running. You can turn this this to `False` if you want the fastest possible performance.
- `UPDATE_DB`: **For internal use**. If valid `.env` file is present, setting this flag to `True` will read `output.csv` and insert into the linked database. 
- `SKIP_SCRAPE`: Controls whether the scraping process is skipped or not. This should only be used in conjunction with `UPDATE_DB`, when you want to write to the DB from an existing `.csv` file without regenerating it.

## Core Dependencies
### Scraping
- bs4 : [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- pandas : [Pandas](https://github.com/pandas-dev/pandas)
- requests : HTTP requests
- re : Regex
- time : time
- os : os
### Loading Animation
- itertools
- threading
- sys
### Database
- psycopg2 : [psychopg2](https://www.psycopg.org/docs/)
- python-dotenv : [python-dotenv](https://pypi.org/project/python-dotenv/)
