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
    print(cat)
    if SKIP_SCRAPE:
        break
    url = f"https://www.westerncalendar.uwo.ca/Courses.cfm?Subject={cat}&SelectedCalendar=Live&ArchiveID="

    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    for panel in soup.find_all(class_="panel-default")[2:]:
        prereqs = []  # [string, link?, bold?]
        antireqs = []
        coreqs = []
        preAndCoreqs = []
        coreqFlag = False
        pcreqFlag = False
        title = panel.find_all(class_="courseTitleNoBlueLink")[
            0].get_text().strip()
        desc = panel.find_all(
            class_="col-xs-12")[0].get_text().strip().replace("\n", "").replace("\r", "")
        location = panel.find_all("img")[0]["alt"]
        for child in panel.find_all(class_="col-xs-12"):
            if child.find_all("strong"):
                if child.find_all("strong")[0].get_text() == "Antirequisite(s):":
                    for item in child.children:
                        if hasattr(item, "children"):
                            for req in item.children:
                                reqTraits = [req.get_text().strip().replace(
                                    "\n", "").replace("\r", ""), False]
                                if not reqTraits[0]:
                                    continue
                                if type(req) == Tag:
                                    if req.name == "a":
                                        reqTraits[1] = True
                                antireqs.append(reqTraits)
                elif child.find_all("strong")[0].get_text() == "Prerequisite(s):":
                    for item in child.children:
                        if hasattr(item, "children"):
                            for req in item.children:
                                reqTraits = [req.get_text().strip().replace(
                                    "\n", "").replace("\r", ""), False]
                                if not reqTraits[0]:
                                    continue
                                if "Prerequisite(s):" in reqTraits[0]:
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
                                    preAndCoreqs.append(reqTraits)
                                elif coreqFlag:
                                    coreqs.append(reqTraits)
                                else:
                                    prereqs.append(reqTraits)
        # if antireqs:
        #     print("ANTI", antireqs)
        # if prereqs:
        #     print("PRE", prereqs)
        # if coreqs:
        #     print("CO", coreqs)
        # if preAndCoreqs:
        #     print("PRECO", preAndCoreqs)
        # print("="*20)
