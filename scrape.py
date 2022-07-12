# COURSE SCRAPER
# Oscar Yu 2022 ©

from bs4 import BeautifulSoup
import requests
import json
import re
import time

ANIMATE = True

if ANIMATE:
    import itertools
    import threading
    import sys
    def animate():
        for c in itertools.cycle(['|', '/', '-', '\\']):
            if done:
                break
            sys.stdout.write('\rloading ' + c + f' time elapsed: {round(time.time() - startTime, 2)} seconds')
            sys.stdout.flush()
            time.sleep(0.1)
        sys.stdout.write('\rDone!     ')
    
    done = False
    t = threading.Thread(target=animate)
    t.daemon=True
    t.start()

startTime = time.time()

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
        codePattern = re.compile(r"([0-9]{4}[A-Z/]*) ")
        altPattern = re.compile(r"([0-9]{4}[A-Z/]*)")
        namePattern = re.compile(r"[0-9]{4}[A-Z/]*\s(.*)")
        code = re.findall(codePattern, title)
        if len(code) == 0:
            code = re.findall(altPattern, title)
        code = code[0]
        name = re.findall(namePattern, title)[0] if re.findall(namePattern, title) else ""
        
        courseDict["code"] = cat + " " + code
        courseDict["name"] = name
        courseDict["desc"] = desc
        courseDict["anti"] = antireqs
        courseDict["pre"] = prereqs
        courseDict["extra"] = extra
        courseDict["loc"] = location
        # print(courseDict)
        # print()
        courseList.append(courseDict)
jsonDict = {"courses":courseList}
json.dump(jsonDict, newFile)
newFile.close()

if ANIMATE:
    done = True
    
print(f"\nProcess complete in {round(time.time() - startTime, 2)} seconds")