# from dotenv import load_dotenv
# import psycopg2
# import os
from bs4 import BeautifulSoup, NavigableString, Tag
import pandas as pd
import requests
import re
# from databaseFunctions import *
file = open("western-course-scraper/categories.txt", "r")
catList = [line.rstrip("\n") for line in file.readlines()]
file.close()

""" 
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

# Query to retrieve table names from the database catalog
cursor = conn.cursor()
 """


def storeInDatabase(code, prereqs, antireqs, coreqs, precoreqs, prereqsLink, antireqsLink, coreqsLink, precoreqsLink):
    print("storing...\n{")
    print("code:", code)
    if prereqs:
        print("prereqs_text: ", prereqs)
        print("prereqs: ", prereqsLink)
        addJsonToTable(cursor=cursor, conn=conn, courseCode=code,
                       columnName="prerequisites_text", data=prereqs)
    if antireqs:
        print("antireqs_text: ", antireqs)
        print("antireqs: ", antireqsLink)
        addJsonToTable(cursor=cursor, conn=conn, courseCode=code,
                       columnName="antirequisites_text", data=antireqs)
    if coreqs:
        print("coreqs_text: ", coreqs)
        print("coreqs: ", coreqsLink)
        addJsonToTable(cursor=cursor, conn=conn, courseCode=code,
                       columnName="corequisites_text", data=coreqs)
    if precoreqs:
        print("precoreqs_text: ", precoreqs)
        print("precoreqs: ", precoreqsLink)
        addJsonToTable(cursor=cursor, conn=conn, courseCode=code,
                       columnName="precorequisites_text", data=precoreqs)

    print("}")
    return


def printResults(code, prereqs, antireqs, coreqs, precoreqs, prereqsLink, antireqsLink, coreqsLink, precoreqsLink):
    print("storing...\n{")
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

    print("}")
    return


def formatLink(link):
    link = link.strip(" ")
    link = link.strip(".")
    link = link.strip(",")
    return link


courses = pd.DataFrame(columns=[
    "course_code",
    "course_name",
    "antirequisites",
    "prerequisites",
    "description",
    "location",
    "extra_info"])

for cat in catList[43:]:
    print(cat)
    url = f"https://www.westerncalendar.uwo.ca/Courses.cfm?Subject={cat}&SelectedCalendar=Live&ArchiveID="

    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    for panel in soup.find_all(class_="panel-default")[2:]:
        prereqs = []  # [string, link?, bold?]
        antireqs = []
        coreqs = []
        preAndCoreqs = []
        prereqsLink = []  # [string, link?, bold?]
        antireqsLink = []
        coreqsLink = []
        preAndCoreqsLink = []
        coreqFlag = False
        pcreqFlag = False
        title = panel.find_all(class_="courseTitleNoBlueLink")[
            0].get_text().strip()
        desc = panel.find_all(
            class_="col-xs-12")[0].get_text().strip().replace("\n", "").replace("\r", "")
        location = panel.find_all("img")[0]["alt"]
        for child in panel.find_all(class_="col-xs-12"):
            if child.find_all("strong"):
                strongText = child.find_all("strong")[0].get_text()
                if strongText == "Antirequisite(s):":
                    for item in child.children:
                        if hasattr(item, "children"):
                            for req in item.children:
                                reqTraits = [req.get_text().strip().replace(
                                    "\n", "").replace("\r", ""), False]
                                if not reqTraits[0]:
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
                                if not reqTraits[0] and "Prerequisite(s):" in reqTraits[0]:
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
        codePattern = re.compile(r"([0-9]{4}[A-Z/]*) ")
        altPattern = re.compile(r"([0-9]{4}[A-Z/]*)")
        code = re.findall(codePattern, title)
        if len(code) == 0:
            code = re.findall(altPattern, title)
        code = code[0]
        code = cat + " " + code
        # storeInDatabase(code=code, prereqs=prereqs, antireqs=antireqs,
        #                 coreqs=coreqs, precoreqs=preAndCoreqs, prereqsLink=prereqsLink, coreqsLink=coreqsLink, antireqsLink=antireqsLink, precoreqsLink=preAndCoreqsLink
        printResults(code=code, prereqs=prereqs, antireqs=antireqs,
                     coreqs=coreqs, precoreqs=preAndCoreqs, prereqsLink=prereqsLink, coreqsLink=coreqsLink, antireqsLink=antireqsLink, precoreqsLink=preAndCoreqsLink)

        print("="*20)
    break

# cursor.close()
# conn.close()
