# scraping

Python script to scrape all UWO courses on the academic calendar.

## Output
Output of script(s) is a Json file in the following format:

```js
{
  "courses": [{
    "code": "Computer Science 1027A/B",
    "name": "COMPUTER SCIENCE FUNDAMENTALS II",
    "desc": "A continuation for both Computer Science 1025A/B and Computer Science 1026A/B. Data organization and manipulation; abstract data types and their implementations in a modern programming language; lists, stacks, queues, trees; recursion; file handling and storage.",
    "anti": "Computer Science 1037A/B, Computer Science 2121A/B, Digital Humanities 2221A/B."
    "pre": "Computer Science 1025A/B, Computer Science 1026A/B, Data Science 1200A/B, or Engineering Science 1036A/B, (in each case with a mark of at least 65%)."
    "extra": "3 lecture hours, 1 laboratory/tutorial hour."
    "loc": "Western Main Campus" 
  }]
}
```

## Usage
1. Run `extract.py` to update the list of course categories, located in `categories.txt`.
2. Run `scrape.py` to scrape all current courses related information. Output is written to `output.json`.

### Dependencies
- re : Regex
- bs4 : [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- requests : HTTP requests
- json : Json
