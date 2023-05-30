# COURSE SCRAPER
# Oscar Yu 2022 ©

from dotenv import load_dotenv
import psycopg2
import sys
import threading
import itertools
import os
import time
import re
import requests
import pandas as pd
from bs4 import BeautifulSoup
ANIMATE = True
UPDATE_DB = True
SKIP_SCRAPE = False


# Scraping
# Animation
# Database
load_dotenv()

# Record start time
startTime = time.time()

# Animation
status = "Loading"
if ANIMATE:
    def animate():
        for c in itertools.cycle(['-', '\\', '|', '/']):
            if done:
                break
            sys.stdout.write(
                f'\r{status} {c}' + f' Time elapsed: {round(time.time() - startTime, 2)} seconds')
            sys.stdout.flush()
            time.sleep(0.1)
        sys.stdout.write('\rDone!     ')

    done = False
    t = threading.Thread(target=animate)
    t.daemon = True
    t.start()

# Import categories
file = open("categories.txt", "r")
catList = [line.rstrip("\n") for line in file.readlines()]
file.close()

# Create pandas dataframe
courses = pd.DataFrame(columns=[
    "course_code",
    "course_name",
    "antirequisites",
    "prerequisites",
    "description",
    "location",
    "extra_info"])

scrapeCount = 0
status = "Scraping"

for cat in catList:
    if SKIP_SCRAPE:
        break
    url = f"https://www.westerncalendar.uwo.ca/Courses.cfm?Subject={cat}&SelectedCalendar=Live&ArchiveID="

    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    for panel in soup.find_all(class_="panel-default")[2:]:
        title = panel.find_all(class_="courseTitleNoBlueLink")[
            0].get_text().strip()
        desc = panel.find_all(
            class_="col-xs-12")[0].get_text().strip().replace("\n", "").replace("\r", "")
        location = panel.find_all("img")[0]["alt"]

        # check for anti
        antireqs = ""
        prereqs = ""
        extra = ""
        for child in panel.find_all(class_="col-xs-12"):
            if child.find_all("strong"):
                strong = child.find_all("strong")[0].get_text()
                if strong == "Antirequisite(s):":
                    antireqs = child.get_text().replace(
                        "Antirequisite(s):", "").strip().replace("\n", "").replace("\r", "")
                elif strong == "Prerequisite(s):":
                    prereqs = child.get_text().replace(
                        "Prerequisite(s):", "").strip().replace("\n", "").replace("\r", "")
                elif strong == "Extra Information:":
                    extra = child.get_text().replace("Extra Information:",
                                                     "").strip().replace("\n", "").replace("\r", "")

        # parse title
        codePattern = re.compile(r"([0-9]{4}[A-Z/]*) ")
        altPattern = re.compile(r"([0-9]{4}[A-Z/]*)")
        namePattern = re.compile(r"[0-9]{4}[A-Z/]*\s(.*)")
        code = re.findall(codePattern, title)
        if len(code) == 0:
            code = re.findall(altPattern, title)
        code = code[0]
        name = re.findall(namePattern, title)[
            0] if re.findall(namePattern, title) else ""

        code = cat + " " + code

        # look for existing code in dataframe
        if code in courses["course_code"].values:
            c = courses["course_code"] == code
            if location == "Western Main Campus":
                courses.loc[c, "prerequisites"] = prereqs.replace("\n", "")
            courses.loc[c, "location"] += f",{location}"
            continue

        else:
            row = pd.DataFrame({
                "course_code": code,
                "course_name": name,
                "antirequisites": antireqs,
                "prerequisites": prereqs,
                "description": desc,
                "location": location,
                "extra_info": extra}, index=[0])
            courses = pd.concat([row, courses.loc[:]],
                                axis=0).reset_index(drop=True)
        # print()

if not SKIP_SCRAPE:
    status = "Writing to CSV"
    csvFile = open("output.csv", "w")
    courses.to_csv(csvFile, sep="|", header=False,
                   index=False, line_terminator="\n")
    csvFile.close()

if UPDATE_DB:
    # Load database connection data from env
    hostname = os.environ.get("DB_HOST_NAME")
    port = os.environ.get("DB_PORT")
    dbName = os.environ.get("DB_NAME")
    user = os.environ.get("DB_USER_NAME")
    password = os.environ.get("DB_PASSWORD")

    # Create postgres connection
    status = "Connecting"
    conn = psycopg2.connect(
        host=hostname,
        port=port,
        database=dbName,
        user=user,
        password=password)

    # Verify connection
    curr = conn.cursor()
    curr.execute("SELECT version();")
    dbVersion = curr.fetchone()
    curr.close()
    print(f"\n{dbVersion[0]}\n")
    status = "Writing to DB"
    csvFile = open("output.csv")
    curr = conn.cursor()
    curr.copy_from(csvFile, "courses", sep="|")

    csvFile.close()
    curr.close()
    conn.commit()
    conn.close()

if ANIMATE:
    done = True

print(f"\nProcess complete in {round(time.time() - startTime, 2)} seconds")
