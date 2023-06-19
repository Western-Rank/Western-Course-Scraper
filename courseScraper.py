# from dotenv import load_dotenv
# import psycopg2
# import os
from bs4 import BeautifulSoup, NavigableString, Tag
import requests
import re
from databaseFunctions import *
import json
from helper import *
import time

courseIndex = 0
coursesCSV = pd.DataFrame(columns=[
    "course_name",
    "course_code",
    "prerequisites_text",
    "antirequisites_text",
    "corequisites_text",
    "precorequisites_text",
    "prerequisites_link",
    "antirequisites_link",
    "corequisites_link",
    "precorequisites_link",
    "description",
    "location",
    "extra_info",
    "weight",
    "category"])
catData = []


def addToCSV(name, code, prereqs, antireqs, coreqs, precoreqs, prereqsLink, antireqsLink, coreqsLink, precoreqsLink, desc, location, extra, weight, category):
    global courseIndex
    coursesCSV.loc[courseIndex] = {"course_name": name, "course_code": code, "prerequisites_text": prereqs, "antirequisites_text": antireqs, "corequisites_text": coreqs, "precorequisites_text": precoreqs, "prerequisites_link": prereqsLink,
                                   "antirequisites_link": antireqsLink, "corequisites_link": coreqsLink, "precorequisites_link": precoreqsLink, "description": desc, "location": location, "extra_info": extra, "weight": weight, "category": category}
    courseIndex += 1


def scrapeFromAcademicCalendar(startAt=0, endAt=len(catList)):
    print("Scraping Categories")
    baseUrl = 'https://www.westerncalendar.uwo.ca/Courses.cfm?SelectedCalendar=Live&ArchiveID='
    basePage = requests.get(baseUrl)
    baseSoup = BeautifulSoup(basePage.text, "html.parser")
    table = baseSoup.find('tbody')
    for index, catPanel in enumerate(table.find_all("tr")):
        atag = catPanel.find_all("a")[0]
        catDiv = catPanel.find_all("td")[1]
        curCat = re.findall(r"Subject=(.*?)&", atag['href'])[0]
        curCatName = atag.get_text().strip().replace("\n", "").replace("\r", "")
        catBreadth = ""
        try:
            catBreadth = re.findall(r"CATEGORY\s+(\w+)", catDiv.get_text())
        except Exception as e:
            if curCat == "HUMANIT":
                catBreadth = ["B"]
            else:
                print(e)
        print(curCat, curCatName, catBreadth, index)
        catData.append([curCat, curCatName, catBreadth])
    catCSV = pd.DataFrame(
        catData, columns=['category_code', 'category_name', 'breadth'])
    catCSV.to_csv("western-course-scraper/cat_data.csv")
    coursesScraped = set()
    # scraping logic
    print("Scraping Courses")
    start = time.time()
    for index, cat in enumerate(catList[startAt:endAt]):
        print(cat, index, "/", endAt)
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
            weight = 0
            for child in panel.find_all(class_="col-xs-12"):
                if child.find_all("strong"):
                    strongText = child.find_all("strong")[0].get_text()
                    if strongText == "Antirequisite(s):":
                        for item in child.children:
                            if hasattr(item, "children"):
                                for req in item.children:
                                    reqTraits = [req.get_text().strip().replace(
                                        "\n", "").replace("\r", ""), False]
                                    trailingComma = False
                                    if not reqTraits[0] or "Antirequisite(s):" in reqTraits[0]:
                                        continue
                                    if reqTraits[0].strip()[-1] == ",":
                                        trailingComma = True
                                    if type(req) == Tag and req.name == "a":
                                        reqTraits[1] = True
                                        reqTraits[0] = formatLink(reqTraits[0])
                                        antireqsLink.append(reqTraits[0])
                                    antireqs.append(
                                        {"text": reqTraits[0], "isLink": reqTraits[1]})
                                    if trailingComma:
                                        antireqs.append(
                                            {"text": ",", "isLink": False})
                    elif strongText == "Prerequisite(s):" or "Corequisite(s):" in strongText:
                        for item in child.children:
                            if hasattr(item, "children"):
                                for req in item.children:
                                    trailingComma = False
                                    reqTraits = [req.get_text().strip().replace(
                                        "\n", "").replace("\r", ""), False]
                                    if not reqTraits[0] or "Prerequisite(s):" in reqTraits[0]:
                                        continue
                                    if reqTraits[0].strip()[-1] == ",":
                                        trailingComma = True
                                    if "Pre-or Corequisite(s)" in reqTraits[0]:
                                        pcreqFlag = True
                                    elif "Corequisite(s)" in reqTraits[0]:
                                        coreqFlag = True
                                    if type(req) == Tag:
                                        if req.name == "a":
                                            reqTraits[1] = True
                                            reqTraits[0] = formatLink(
                                                reqTraits[0])
                                    if pcreqFlag and coreqFlag:
                                        print(title + " EXCEPTION")
                                        raise Exception("BOTH FLAGS ACTIVE")
                                    elif pcreqFlag:
                                        if reqTraits[1]:
                                            preAndCoreqsLink.append(
                                                reqTraits[0])
                                        preAndCoreqs.append(
                                            {"text": reqTraits[0], "isLink": reqTraits[1]})
                                        if trailingComma:
                                            preAndCoreqs.append(
                                                {"text": ",", "isLink": False})
                                    elif coreqFlag:
                                        if reqTraits[1]:
                                            coreqsLink.append(
                                                reqTraits[0])
                                        coreqs.append(
                                            {"text": reqTraits[0], "isLink": reqTraits[1]})
                                        if trailingComma:
                                            coreqs.append(
                                                {"text": ",", "isLink": False})
                                    else:
                                        if reqTraits[1]:
                                            prereqsLink.append(
                                                reqTraits[0])
                                        prereqs.append(
                                            {"text": reqTraits[0], "isLink": reqTraits[1]})
                                        if trailingComma:
                                            prereqs.append(
                                                {"text": ",", "isLink": False})

                    elif strongText == "Extra Information:":
                        extra = child.get_text().replace("Extra Information:",
                                                         "").strip().replace("\n", "").replace("\r", "")
                    elif "Course Weight" in strongText:
                        weight = child.get_text().replace("Course Weight:", "").replace(
                            "\n", "").replace("\r", "").replace("More details", "").strip()
                        if weight != "":
                            weight = float(weight)
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
            addToCSV(name=newTitle, code=code, prereqs=prereqs, antireqs=antireqs,
                     coreqs=coreqs, precoreqs=preAndCoreqs, prereqsLink=list(set(prereqsLink)), coreqsLink=list(set(coreqsLink)), antireqsLink=list(set(antireqsLink)), precoreqsLink=list(set(preAndCoreqsLink)), desc=desc, location=location, extra=extra, weight=weight, category=cat)
    end = time.time()
    totTime = end-start
    print("DONE SCRAPING IN", totTime //
          60, "MINUTES AND", round(totTime % 60, 2), "SECONDS")

    coursesCSV.to_csv("western-course-scraper/course_data.csv")
    print("WROTE TO CSV")
