from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from helper import formatLink
import pandas as pd

"""
#CODE TO GET HTML FILES WITH BREADTH CATEGORIES

breadthCat = "C"
driver = webdriver.Chrome()  # Or specify the appropriate webdriver for your browser
driver.get('https://www.westerncalendar.uwo.ca/AllCourses.cfm')

checkbox = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, 'CategoryFilter_CATEGORY ' + breadthCat)))
checkbox.click()

button = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.NAME, 'searchWithBoxes')))
button.click()

updated_html = driver.page_source

# Specify the desired file path
file_path = f'western-course-scraper/breadth{breadthCat}.html'
with open(file_path, 'w', encoding='utf-8') as file:
    file.write(updated_html)


driver.quit()
"""
breadthCats = ["A", "B", "C"]

courseCsv = pd.read_csv("western-course-scraper/course_data.csv")

with open(f'western-course-scraper/breadthA.html', 'r', encoding='utf-8') as file:
    html_content = file.read()

soup = BeautifulSoup(html_content, 'html.parser')

for panel in soup.find_all(class_="panel-default")[2:15]:
    title = panel.find_all(class_="courseTitleNoBlueLink")[
        0].get_text().strip()
    courseCode = formatLink(title)
    print(courseCode)
    row = courseCsv.index[courseCsv['course_code'] == courseCode]
    courseCsv.at[row, "breadth"] = "A"
courseCsv.to_csv("western-course-scraper/course_data.csv")
