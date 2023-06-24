import pandas as pd
from dotenv import load_dotenv
from databaseFunctions import *
import re
import time
import ast
file = open("western-course-scraper/categories.txt", "r")
catList = [line.rstrip("\n") for line in file.readlines()]
file.close()

catNamesSet = set(catList)


"""
FUNCTION FOR MAPPING COURSE NAMES TO CATEGORY NAMES
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

with open("western-course-scraper/catNameJson.json", "r") as json_file:
    mapCourseToCat = json.load(json_file)


def uploadCsvToDatabase(conn, cursor, insertRequisites=False, insertCats=False):
    print("UPLOADING TO DATABASE")
    fetchSetOfCourses(conn=conn, cursor=cursor)
    start = time.time()
    # category upload
    if insertCats:
        catCSV = pd.read_csv("western-course-scraper/cat_data.csv")
        for index, category in catCSV.iterrows():
            print(index, "Categories Uploaded")
            insertCategoryIntoDatabase(
                categoryCode=category["category_code"], categoryName=category["category_name"], breadth=ast.literal_eval(category["breadth"]), conn=conn, cursor=cursor)
        print("CATEGORIES UPLOADED")
    # course upload
    courseCsv = pd.read_csv("western-course-scraper/course_data.csv")
    courseCsvLen = courseCsv.shape[0]
    for index, course in courseCsv.iterrows():
        if index % 50 == 0:
            print(index, "/", courseCsvLen, "COURSES UPLOADED")
        insertCourseIntoDatabase(name=course["course_name"], code=course["course_code"], prereqs=ast.literal_eval(course["prerequisites_text"]), antireqs=ast.literal_eval(course["antirequisites_text"]),
                                 coreqs=ast.literal_eval(course["corequisites_text"]), precoreqs=ast.literal_eval(course["precorequisites_text"]), desc=course["description"], location=course["location"], extra=course["extra_info"], category=course["category"], level=course["level"], conn=conn, cursor=cursor)
    if insertRequisites:
        for index, course in courseCsv.iterrows():
            if index % 50 == 0:
                print(index, "/", courseCsvLen, "COURSES REQUISITES UPLOADED")
            insertRequisiteRows(code=course["course_code"], prereqsLink=ast.literal_eval(course["prerequisites_link"]), coreqsLink=ast.literal_eval(course["antirequisites_link"]),
                                antireqsLink=ast.literal_eval(course["corequisites_link"]), precoreqsLink=ast.literal_eval(course["precorequisites_link"]), conn=conn, cursor=cursor)
    end = time.time()
    totTime = end - start
    print("UPLOADED TO DATABASE IN", totTime //
          60, "MINUTES AND", round(totTime % 60, 2), "SECONDS")


def getLevel(code):
    return min(int(code[0]), 5)


def databaseConnection():
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

    return [conn, cursor]


def printResults(courseCode):
    courseCsv = pd.read_csv("western-course-scraper/course_data.csv")
    row = courseCsv.loc[courseCsv['course_code'] == courseCode]
    print("name:", row["course_name"])
    print("code:", row["course_code"])
    if prereqs:
        print("prereqs_text: ", row["prerequisites_text"])
        print("prereqs: ", row["prerequisites_link"])

    if antireqs:
        print("antireqs_text: ", row["antirequisites_text"])
        print("antireqs: ", row["antirequisites_link"])
    if coreqs:
        print("coreqs_text: ", row["corequisites_text"])
        print("coreqs: ", row["corequisites_link"])
    if precoreqs:
        print("precoreqs_text: ", row["precorequisites_text"])
        print("precoreqs: ", row["precorequisites_link"])
    print("description:", row["desc"])
    print("location:", row["location"])
    print("extra:", row["extra"])
    print("}")
    return


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
        print(catName, newcode)
        raise Exception("ERROR: category name does not exist")
    link = cat + " " + newcode
    return link
