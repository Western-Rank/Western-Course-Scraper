from dotenv import load_dotenv
import psycopg2
import os
import json
from pprint import pprint

load_dotenv()

hostname = os.environ.get("DB_HOST_NAME")
port = os.environ.get("DB_PORT")
dbName = os.environ.get("DB_NAME")
user = os.environ.get("DB_USER_NAME")
password = os.environ.get("DB_PASSWORD")


errorCourses = """
(AH 2634F/G)
(BIOCHEM 4484E)
(EPID 4310A/B)
(GSWS 2290F/G)
(GSWS 2291F/G)
(GSWS 2440F/G)
(GSWS 3440F/G)
(GSWS 3460F/G)
(INDIGSTU 4806F/G)
(INDIGSTU 2676A/B)
(INDIGSTU 2682F/G)
(INDIGSTU 2807F/G)
(HISTORY 4806F/G)
(KINESIOL 4301F/G)
(NEURO 3996F/G)
(NEURO 3996F/G)
(PSYCHOL 4873E)
(PSYCHOL 4874E)
(SA 2676A/B)
"""


def addJsonToTable(cursor, conn, courseCode, columnName, data):

    # Convert the Python dictionary to a JSON string
    json_data = json.dumps(data)

    update_query = f"UPDATE \"Course\" SET {columnName} = %s WHERE course_code = %s;"
    cursor.execute(update_query, (json_data, courseCode))
    conn.commit()


def insertCourseIntoDatabase(name, code, prereqs, antireqs, coreqs, precoreqs, desc, location, extra, conn, cursor):

    prereqJson = json.dumps(prereqs)
    antireqJson = json.dumps(antireqs)
    coreqJson = json.dumps(coreqs)
    precoreqJson = json.dumps(precoreqs)


#  insert_query = f'INSERT INTO "Course" (course_name, course_code, prerequisites_text, antirequisites_text, corequisites_text, precorequisites_text, description, location, extra_info) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);'

    updateCourseInfo_query = f'UPDATE "Course" SET course_name = %s, prerequisites_text = %s, antirequisites_text = %s, corequisites_text = %s, precorequisites_text = %s, description = %s, location = %s, extra_info = %s WHERE course_code = %s;'
    cursor.execute(updateCourseInfo_query, (
        name, prereqJson, antireqJson, coreqJson, precoreqJson, desc, location, extra, code
    ))
    conn.commit()


def insertRequisiteRows(code, prereqsLink, antireqsLink, coreqsLink, precoreqsLink, conn, cursor):
    prereqsLink = list(set(prereqsLink))
    antireqsLink = list(set(antireqsLink))
    coreqsLink = list(set(coreqsLink))
    precoreqsLink = list(set(precoreqsLink))
    try:
        if (prereqsLink):
            insertPrereqLinkQuery = 'INSERT INTO "_CoursePrerequisite" ("B", "A") VALUES '
            for index, _ in enumerate(prereqsLink):
                if (index == len(prereqsLink) - 1):
                    insertPrereqLinkQuery += f'(\'{code}\', %s);'
                else:
                    insertPrereqLinkQuery += f'(\'{code}\', %s), '
            cursor.execute(insertPrereqLinkQuery, tuple(prereqsLink))

        if (antireqsLink):
            insertAntireqLinkQuery = 'INSERT INTO "_CourseAntirequisite" ("B", "A") VALUES '
            for index, _ in enumerate(antireqsLink):
                if (index == len(antireqsLink) - 1):
                    insertAntireqLinkQuery += f'(\'{code}\', %s);'
                else:
                    insertAntireqLinkQuery += f'(\'{code}\', %s), '
            cursor.execute(insertAntireqLinkQuery, tuple(antireqsLink))

        if (coreqsLink):
            insertCoreqLinkQuery = 'INSERT INTO "_CourseCorequisite" ("B", "A") VALUES '
            for index, _ in enumerate(coreqsLink):
                if (index == len(coreqsLink) - 1):
                    insertCoreqLinkQuery += f'(\'{code}\', %s);'
                else:
                    insertCoreqLinkQuery += f'(\'{code}\', %s), '

            cursor.execute(insertCoreqLinkQuery, tuple(coreqsLink))

        if (precoreqsLink):
            insertPrecoreqLinkQuery = 'INSERT INTO "_CoursePrecorequisite" ("B", "A") VALUES '
            for index, _ in enumerate(precoreqsLink):
                if (index == len(precoreqsLink) - 1):
                    insertPrecoreqLinkQuery += f'(\'{code}\', %s);'
                else:
                    insertPrecoreqLinkQuery += f'(\'{code}\', %s), '

            cursor.execute(insertPrecoreqLinkQuery, tuple(precoreqsLink))
    except Exception as e:
        print(e)
    conn.commit()


def deleteRequisiteRows(cursor, conn):
    deletePrereqQuery = f'DELETE FROM "_CoursePrerequisite"'
    deleteAntireqQuery = f'DELETE FROM "_CourseAntirequisite"'
    deleteCoreqQuery = f'DELETE FROM "_CourseCorequisite"'
    deletePrecoreqQuery = f'DELETE FROM "_CoursePrecorequisite"'
    cursor.execute(deletePrereqQuery)
    cursor.execute(deleteAntireqQuery)
    cursor.execute(deleteCoreqQuery)
    cursor.execute(deletePrecoreqQuery)

    conn.commit()


"""
ADD A NEW COLUMN

table_name = "Course"  # Replace with the name of your table
column_name = "precorequisites_text"  # Replace with the name of the new column

alter_query = f'ALTER TABLE "Course" ADD COLUMN {column_name} JSON;'

cursor.execute(alter_query)

conn.commit()
"""
