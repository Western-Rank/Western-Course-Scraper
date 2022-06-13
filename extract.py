# Extract course code categories from main list
# https://www.westerncalendar.uwo.ca/Courses.cfm?SelectedCalendar=Live&ArchiveID=
import re
htmlfile = open("academic.html", "r")

pattern = re.compile(r"Subject=([A-Z]*)&")

file = open("new.txt", "w")
codes = re.findall(pattern, htmlfile.read())
for code in codes:
    file.write(code + "\n")
htmlfile.close()
file.close()
