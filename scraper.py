# from dotenv import load_dotenv
# import psycopg2
# import os
from bs4 import BeautifulSoup, NavigableString, Tag
import pandas as pd
import requests
import re
from databaseFunctions import *
import json

# for uploading courses to database
updateDB = True
insertRequisites = True

mapCourseToCat = {}

file = open("western-course-scraper/categories.txt", "r")
catList = [line.rstrip("\n") for line in file.readlines()]
file.close()

# loading database connetion vairables
if updateDB:

    load_dotenv()
    hostname = os.environ.get("DB_HOST_NAME")
    port = os.environ.get("DB_PORT")
    dbName = os.environ.get("DB_NAME")
    user = os.environ.get("DB_USER_NAME")
    password = os.environ.get("DB_PASSWORD")
    print(hostname, port, dbName, user)
    conn = psycopg2.connect(
        host=hostname,
        port=port,
        database=dbName,
        user=user,
        password=password
    )
    cursor = conn.cursor()
    deleteRequisiteRows(cursor=cursor, conn=conn)

file_path = "western-course-scraper/catNameJson.json"

# Load the JSON file as a Python dictionary
with open(file_path, "r") as json_file:
    mapCourseToCat = json.load(json_file)


# prints the results from the scrape
def printResults(name, code, prereqs, antireqs, coreqs, precoreqs, prereqsLink, antireqsLink, coreqsLink, precoreqsLink, desc, location, extra):
    print("name:", name)
    print("code:", code)
    if prereqs:
        print("prereqs_text: ", prereqs)
        print("prereqs: ", prereqsLink)

    if antireqs:
        print("antireqs_text: ", antireqs)
        print("antireqs: ", antireqsLink)
    if coreqs:
        print("coreqs_text: ", coreqs)
        print("coreqs: ", coreqsLink)
    if precoreqs:
        print("precoreqs_text: ", precoreqs)
        print("precoreqs: ", precoreqsLink)
    print("description:", desc)
    print("location:", location)
    print("extra:", extra)
    print("}")
    return

# formats any course codes to make sure theres no leading or trailing symbols


catNamesSet = set(catList)


def formatLink(link):
    link = link.strip(" ")
    link = link.strip(".")
    link = link.strip(",")
    codePattern = re.compile(r"([0-9]{4}[A-Z/]*) ")
    altPattern = re.compile(r"([0-9]{4}[A-Z/]*)")
    catNamePattern = re.compile(r"^(.*?)\d")
    newcode = re.findall(codePattern, link)
    if len(newcode) == 0:
        newcode = re.findall(altPattern, link)
    catName = re.findall(catNamePattern, link)[0].strip()
    newcode = newcode[0]
    if catName in mapCourseToCat:
        catName = catName
        cat = mapCourseToCat[catName]
    elif catName in catNamesSet:
        cat = catName
    else:
        print(catName, link)
        raise Exception("THIS FUCKIN ERROR AGAIN")
    link = cat + " " + newcode
    return link


"""
for cat in catList:
    print(cat)
    url = f"https://www.westerncalendar.uwo.ca/Courses.cfm?Subject={cat}&SelectedCalendar=Live&ArchiveID="

    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    courseName = soup.find(
        class_="text-center purple").get_text().strip().replace("\n", "")
    mapCourseToCat[courseName] = cat

with open("catNameJson.json", "w") as json_file:
    json.dump(mapCourseToCat, json_file)
"""

coursesScraped = set()

# scraping logic
for cat in catList:
    print(cat)
    url = f"https://www.westerncalendar.uwo.ca/Courses.cfm?Subject={cat}&SelectedCalendar=Live&ArchiveID="

    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    for panel in soup.find_all(class_="panel-default")[2:]:
        # holds the text with the requisite information in this format {text: string, isLink(if it links to another course): boolean}
        prereqs = []
        antireqs = []
        coreqs = []
        preAndCoreqs = []
        prereqsLink = []
        antireqsLink = []
        coreqsLink = []
        preAndCoreqsLink = []
        coreqFlag = False
        pcreqFlag = False
        title = panel.find_all(class_="courseTitleNoBlueLink")[
            0].get_text().strip()
        if title in coursesScraped:
            continue
        coursesScraped.add(title)
        desc = panel.find_all(
            class_="col-xs-12")[0].get_text().strip().replace("\n", "").replace("\r", "")
        location = panel.find_all("img")[0]["alt"]
        extra = ""
        for child in panel.find_all(class_="col-xs-12"):
            if child.find_all("strong"):
                strongText = child.find_all("strong")[0].get_text()
                if strongText == "Antirequisite(s):":
                    for item in child.children:
                        if hasattr(item, "children"):
                            for req in item.children:
                                reqTraits = [req.get_text().strip().replace(
                                    "\n", "").replace("\r", ""), False]
                                if not reqTraits[0] or "Antirequisite(s):" in reqTraits[0]:
                                    continue
                                if type(req) == Tag and req.name == "a":
                                    reqTraits[1] = True
                                    antireqsLink.append(
                                        formatLink(reqTraits[0]))
                                antireqs.append(
                                    {"text": reqTraits[0], "isLink": reqTraits[1]})
                elif strongText == "Prerequisite(s):" or "Corequisite(s):" in strongText:
                    for item in child.children:
                        if hasattr(item, "children"):
                            for req in item.children:
                                reqTraits = [req.get_text().strip().replace(
                                    "\n", "").replace("\r", ""), False]
                                if not reqTraits[0] or "Prerequisite(s):" in reqTraits[0]:
                                    continue
                                if "Pre-or Corequisite(s)" in reqTraits[0]:
                                    pcreqFlag = True
                                elif "Corequisite(s)" in reqTraits[0]:
                                    coreqFlag = True
                                if type(req) == Tag:
                                    if req.name == "a":
                                        reqTraits[1] = True
                                if pcreqFlag and coreqFlag:
                                    print(title + " EXCEPTION")
                                    raise Exception("BOTH FLAGS ACTIVE")
                                elif pcreqFlag:
                                    preAndCoreqs.append(
                                        {"text": reqTraits[0], "isLink": reqTraits[1]})
                                    if reqTraits[1]:
                                        preAndCoreqsLink.append(
                                            formatLink(reqTraits[0]))
                                elif coreqFlag:
                                    if reqTraits[1]:
                                        coreqsLink.append(
                                            formatLink(reqTraits[0]))
                                    coreqs.append(
                                        {"text": reqTraits[0], "isLink": reqTraits[1]})
                                else:
                                    if reqTraits[1]:
                                        prereqsLink.append(
                                            formatLink(reqTraits[0]))
                                    prereqs.append(
                                        {"text": reqTraits[0], "isLink": reqTraits[1]})
                elif strongText == "Extra Information:":
                    extra = child.get_text().replace("Extra Information:",
                                                     "").strip().replace("\n", "").replace("\r", "")
        codePattern = re.compile(r"([0-9]{4}[A-Z/]*) ")
        altPattern = re.compile(r"([0-9]{4}[A-Z/]*)")
        code = re.findall(codePattern, title)
        if len(code) == 0:
            code = re.findall(altPattern, title)
        code = code[0]
        code = cat + " " + code
        namePattern = re.compile(r"[0-9]{4}[A-Z/]*\s(.*)")
        newTitle = re.findall(namePattern, title)[
            0] if re.findall(namePattern, title) else ""
        if updateDB:
            insertCourseIntoDatabase(name=newTitle, code=code, prereqs=prereqs, antireqs=antireqs,
                                     coreqs=coreqs, precoreqs=preAndCoreqs, prereqsLink=list(set(prereqsLink)), coreqsLink=list(set(coreqsLink)), antireqsLink=list(set(antireqsLink)), precoreqsLink=list(set(preAndCoreqsLink)), desc=desc, location=location, extra=extra, insertRequisites=insertRequisites, conn=conn, cursor=cursor)

        # printResults(name=title, code=code, prereqs=prereqs, antireqs=antireqs,
        #              coreqs=coreqs, precoreqs=preAndCoreqs, prereqsLink=prereqsLink, coreqsLink=coreqsLink, antireqsLink=antireqsLink, precoreqsLink=preAndCoreqsLink, desc=desc, location=location, extra=extra)
cursor.close()
conn.close()
