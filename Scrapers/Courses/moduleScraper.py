from bs4 import BeautifulSoup, NavigableString, Tag
import requests
import re
import time


def scrapeAllModules():
    url = "https://www.westerncalendar.uwo.ca/Modules.cfm?SelectedCalendar=Live&ArchiveID="
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    moduleTable = soup.find("tbody")
    moduleRows = moduleTable.find_all("tr")
    for row in moduleRows[0:3]:
        moduleCols = row.find_all("td")
        name = moduleCols[0].get_text().strip().replace(
            "\n", "").replace("\r", "")
        faculty = moduleCols[1].get_text().strip().replace(
            "\n", "").replace("\r", "")
        if "admission discontinued" in name:
            continue
        modules = moduleCols[3].find_all("a")
        print(name, faculty)
        for module in modules:
            moduleUrl = module['href'].strip(".")
            scrapeModule(moduleUrl)
        print("="*40)


def scrapeModule(url):
    modUrl = f'https://www.westerncalendar.uwo.ca{url}'
    modPage = requests.get(modUrl)
    modSoup = BeautifulSoup(modPage.text, "html.parser")
    modName = modSoup.find("h2")
    smallTag = modName.find('small')
    smallTag.extract()
    name = modName.get_text().strip().replace(
        "\n", "").replace("\r", "")
    print("\t", name)
    admissionRequirementsText = modSoup.find(
        id="AdmissionRequirements").get_text()
    moduleReqs = modSoup.find(class_="moduleInfo")
    for div in moduleReqs:
        print(div.get_text().strip().replace(
            "\n", "").replace("\r", ""))
        print("GAPOPP")


scrapeAllModules()
