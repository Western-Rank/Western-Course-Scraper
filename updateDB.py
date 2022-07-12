# DB UPDATE TOOL
# Oscar Yu 2022 ©

ANIMATE = True

import time
import json
import psycopg2
import os
from dotenv import load_dotenv
load_dotenv()

startTime = time.time()

hostname = os.environ.get("DB_HOST_NAME")
port = os.environ.get("DB_PORT")
dbName = os.environ.get("DB_NAME")
user = os.environ.get("DB_USER_NAME")
password = os.environ.get("DB_PASSWORD")

conn = psycopg2.connect(
    host = hostname,
    port = port,
    database = dbName,
    user = user,
    password = password
)

curr = conn.cursor()
curr.execute("SELECT version();")
dbVersion = curr.fetchone()
curr.close()
print(dbVersion[0])

jsonFile = open("output.json")
jsonDict = json.load(jsonFile)
courseList = jsonDict["courses"]

def updateCourses():
    for course in courseList:
        # CHECK IF COURSE EXISTS IN DB
        curr = conn.cursor()
        checkExist = f"""SELECT count(*) from courses
        WHERE course_code = '{course["code"]}' and location = '{course["loc"].replace("'", "''")}'
        """

        curr.execute(checkExist)
        exists = curr.fetchone()[0]
        curr.close()
        if not exists == 0:
            print(exists)
            print(f"""\ncourse {course['code']} already exists at {course['loc'].replace("'", "''")}\n""")
            continue

        # INSERT COURSE
        curr = conn.cursor()
        insertSQL = f"""INSERT INTO courses(course_code, course_name, antirequisites, prerequisites, description, num_reviews, location, extra_info)
        VALUES ('{course["code"]}', '{course["name"].replace("'", "''")}', '{course["anti"].replace("'", "''")}', '{course["pre"].replace("'", "''")}', '{course["desc"].replace("'", "''")}', 0, '{course["loc"].replace("'", "''")}', '{course["extra"].replace("'", "''")}')
        """

        curr.execute(insertSQL)
        curr.close()
        conn.commit()

# DO NOT USE UNLESS NECESSARY
def clearTable():
    curr = conn.cursor()
    clearSQL = "TRUNCATE TABLE courses"
    curr.execute(clearSQL)
    curr.close()

def checkCourse(code):
    curr = conn.cursor()
    selectSQL = f"SELECT * from courses WHERE course_code = '{code}'"
    curr.execute(selectSQL)
    print(curr.fetchone())
    curr.close()

def addCourse(code):
    insertSQL = f"""INSERT INTO courses(course_code) VALUES ('{code}')"""
    curr = conn.cursor()
    curr.execute(insertSQL)
    curr.close()

# I forgot the first time, now depreciated
def addExtraInfo():
    for course in courseList:
        # ADD EXTRA INFO
        curr = conn.cursor()
        updateSQL = f"""UPDATE courses SET extra_info = '{course["extra"].replace("'", "''")}' WHERE course_code = '{course["code"]}' and location = '{course["loc"].replace("'", "''")}' """
        curr.execute(updateSQL)
        curr.close()
        conn.commit()

if ANIMATE:
    import itertools
    import threading
    import sys

    done = False
    def animate():
        for c in itertools.cycle(['|', '/', '-', '\\']):
            if done:
                break
            sys.stdout.write('\rloading ' + c + f' time elapsed: {round(time.time() - startTime, 2)} seconds')
            sys.stdout.flush()
            time.sleep(0.1)
        sys.stdout.write('\rDone!     ')

    t = threading.Thread(target=animate)
    t.daemon=True
    t.start()

# Call functions here
updateCourses()

# END
conn.commit()
conn.close()

if ANIMATE:
    done = True

print(f"\nProcess complete in {round(time.time() - startTime, 2)} seconds")