# Western Course Scraper

Python script to scrape all UWO courses on the academic calendar.

## Output

Output of script(s) is a `.csv` file in the following format:

```js
course_name,
  course_code,
  prerequisites_text,
  antirequisites_text,
  corequisites_text,
  precorequisites_text,
  prerequisites_link,
  antirequisites_link,
  corequisites_link,
  precorequisites_link,
  description,
  location,
  extra_info,
  weight,
  category,
  level;
```

## Usage

All necessary packages can be installed with `pip install -r requirements.txt`.

1. Run `main.py` with the `scrapeData = True` flag set, this will write out all scraped data to `course_data.csv`.

- `updateDB` and `insertRequisites` flags are for internal use.

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
