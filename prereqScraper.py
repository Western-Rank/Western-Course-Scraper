from bs4 import BeautifulSoup, NavigableString, Tag
import pandas as pd
import requests
import re
file = open("western-course-scraper/categories.txt", "r")
catList = [line.rstrip("\n") for line in file.readlines()]
file.close()
SKIP_SCRAPE = False

courses = pd.DataFrame(columns=[
    "course_code",
    "course_name",
    "antirequisites",
    "prerequisites",
    "description",
    "location",
    "extra_info"])

for cat in catList:
    if SKIP_SCRAPE:
        break
    url = f"https://www.westerncalendar.uwo.ca/Courses.cfm?Subject={cat}&SelectedCalendar=Live&ArchiveID="

    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    for panel in soup.find_all(class_="panel-default")[2:]:
        prereqs = []  # [string, link?, bold?]
        antireqs = []
        title = panel.find_all(class_="courseTitleNoBlueLink")[
            0].get_text().strip()
        print(title)
        desc = panel.find_all(
            class_="col-xs-12")[0].get_text().strip().replace("\n", "").replace("\r", "")
        location = panel.find_all("img")[0]["alt"]
        for child in panel.find_all(class_="col-xs-12"):
            if child.find_all("strong"):

                # if child.find_all("strong")[0].get_text() == "Antirequisite(s):":
                #     print("="*20, "ANTIREQS")
                #     for item in child.children:
                #         print(item)
                #         print("*"*20)
                if child.find_all("strong")[0].get_text() == "Antirequisite(s):":
                    for item in child.children:
                        if hasattr(item, "children"):
                            for req in item.children:
                                reqTraits = [req.get_text().strip().replace(
                                    "\n", "").replace("\r", ""), False, False]
                                if not reqTraits[0]:
                                    continue
                                if type(req) == Tag:
                                    if req.name == "a":
                                        reqTraits[1] = True
                                    elif (req.name == "strong"):
                                        reqTraits[2] = True
                                antireqs.append(reqTraits)
                if child.find_all("strong")[0].get_text() == "Prerequisite(s):":
                    for item in child.children:
                        if hasattr(item, "children"):
                            for req in item.children:
                                reqTraits = [req.get_text().strip().replace(
                                    "\n", "").replace("\r", ""), False, False]
                                if not reqTraits[0]:
                                    continue
                                if type(req) == Tag:
                                    if req.name == "a":
                                        reqTraits[1] = True
                                    elif (req.name == "strong"):
                                        reqTraits[2] = True
                                prereqs.append(reqTraits)
        print(prereqs)
        print("="*20)
        print(antireqs)
        print("="*20)
    break
