# COURSE SCRAPER
# Oscar Yu 2022 ©

from bs4 import BeautifulSoup
import requests
import json
import re

file = open("categories.txt", "r")
catList = [line.rstrip("\n") for line in file.readlines()]
file.close()
#print(catList)

newFile = open("output.json", "w")

courseList = []
for cat in catList:
    url = f"https://www.westerncalendar.uwo.ca/Courses.cfm?Subject={cat}&SelectedCalendar=Live&ArchiveID="

    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    for panel in soup.find_all(class_="panel-default")[2:]:
        courseDict = {}
        title = panel.find_all(class_="courseTitleNoBlueLink")[0].get_text().strip()
        desc = panel.find_all(class_="col-xs-12")[0].get_text().strip()
        location = panel.find_all("img")[0]["alt"]

        # check for anti
        antireqs = ""
        prereqs = ""
        extra = ""
        for child in panel.find_all(class_="col-xs-12"):
            if child.find_all("strong"):
                strong = child.find_all("strong")[0].get_text()
                if strong == "Antirequisite(s):":
                    antireqs = child.get_text().replace("Antirequisite(s):", "").strip()
                elif strong == "Prerequisite(s):":
                    prereqs = child.get_text().replace("Prerequisite(s):", "").strip()
                elif strong == "Extra Information:":
                    extra = child.get_text().replace("Extra Information:", "").strip()

        # parse title
        codePattern = re.compile(r"(.*[0-9]{4}[A-Z/]*)")
        namePattern = re.compile(r"[0-9]{4}[A-Z/]*\s(.*)")
        code = re.findall(codePattern, title)[0]
        name = re.findall(namePattern, title)[0] if re.findall(namePattern, title) else ""
        
        courseDict["code"] = code
        courseDict["name"] = name
        courseDict["desc"] = desc
        courseDict["anti"] = antireqs
        courseDict["pre"] = prereqs
        courseDict["extra"] = extra
        courseDict["loc"] = location
        print(courseDict)
        print()
        courseList.append(courseDict)
jsonDict = {"courses":courseList}
json.dump(jsonDict, newFile)
newFile.close()
print("done")

"""
    for item in soup.find_all(class_="courseTitleNoBlueLink"):
        title = (item.get_text().strip()+"\n")
"""