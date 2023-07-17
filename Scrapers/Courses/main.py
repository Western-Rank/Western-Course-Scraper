import psycopg2
import time
from databaseFunctions import *
from helper import *
from courseScraper import scrapeFromAcademicCalendar
import pandas as pd
import ast

scrapeData = True
updateDB = False
insertRequisites = False
insertCats = False
printData = False

if updateDB:
    conn, cursor = databaseConnection()

# scrapes the academic calendar and stores it in 'course_data.csv'
if scrapeData:
    scrapeFromAcademicCalendar()

# need to delete existing requisite columns before inserting new data
if insertRequisites and updateDB:
    deleteRequisiteRows(cursor=cursor, conn=conn)

if updateDB:
    uploadCsvToDatabase(insertRequisites=insertRequisites,
                        insertCats=insertCats, conn=conn, cursor=cursor)

# print results from certain course
if printData:
    printResults("")

if updateDB:
    cursor.close()
    conn.close()
