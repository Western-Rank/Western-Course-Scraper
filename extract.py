# Extract course code categories from main list
# https://www.westerncalendar.uwo.ca/Courses.cfm?SelectedCalendar=Live&ArchiveID=
# Oscar Yu 2022 ©

import re
import requests

url = "https://www.westerncalendar.uwo.ca/Courses.cfm?SelectedCalendar=Live&ArchiveID="
page = requests.get(url)

pattern = re.compile(r"Subject=([A-Z]*)&")
codes = re.findall(pattern, str(page.content))

file = open("categories.txt", "w")
for code in codes:
    file.write(code + "\n")
file.close()
