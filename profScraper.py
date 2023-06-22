'''


# Read the HTML file
with open("profpage.html", "r", encoding="utf-8") as file:
    html_content = file.read()
# Create a BeautifulSoup object
soup = BeautifulSoup(html_content, "html.parser")

# Find all div elements with the specified string
div_elements = soup.select('div[class*="CardNumRating__CardNumRatingNumber"]')

for div in div_elements:
    print(div)

# Print the contents of the div elements
'''
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
# Set up the web driver (replace 'chrome' with 'firefox' or 'edge' if using a different browser)
driver = webdriver.Chrome()  # Make sure the web driver executable is in your PATH
wait = WebDriverWait(driver, 10)  # Wait for elements to load
# Replace with the actual website URL
website_url = "https://www.ratemyprofessors.com/search/professors/1491?q=*"
driver.get(website_url)
page_source = driver.page_source
count = 0
try:
    while True:
        try:
            # Replace 'button_selector' with the actual selector for the button element
            page_source = driver.page_source
            button = wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, "//button[text()='Show More']"))
            )
            button.click()
            count += 1
            if count == 728:
                break
        except Exception as e:
            print(e)
            # Break the loop if the button is no longer clickable
            break
except Exception as e:
    print(e)
    pass
ASD = "KALLIE TRESWESKI"


soup = BeautifulSoup(page_source, "html.parser")

# Find all div elements with the specified string
div_elements = soup.find_all(
    "a", class_=lambda value: value and "TeacherCard__StyledTeacherCard" in value)

profs = []

for div in div_elements:
    id = div["href"]
    rating = div.find(
        "div", class_=lambda value: value and "CardNumRating__CardNumRatingNumber" in value).get_text()
    name = div.find(
        "div", class_=lambda value: value and "CardName__StyledCardName" in value).get_text()
    profs.append({"id": id, "name": name, "rating": rating})
print(len(profs))
cont = input("continue: ") == "y"
if cont:
    with open("profsOutput.json", "w") as json_file:
        json.dump(profs, json_file)

print("ok", len(profs))
driver.quit()
