import csv
import json

import requests
from bs4 import BeautifulSoup
import re
from pydantic import BaseModel

class CourseScheduleEntry(BaseModel):
    term: None
    department: str
    course: str
    section: str
    class_number: str
    mode_of_instruction: str
    course_title: str
    satisfies: str
    units: int
    class_type: str
    days: str
    times: str
    instructor: str
    instructorEmail: str
    location: str
    dates: str
    open_seats: int
    notes: str


class DataExporter:
    @staticmethod
    def to_json(data):
        return [entry.dict() for entry in data]

    @staticmethod
    def json_dump(data,filename):
        with open(filename, 'w') as file:
            json.dump(data, file)
    @staticmethod
    def to_csv(data, filename):
        fieldnames = list(data[0].keys())
        with open(filename, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for entry in data:
                writer.writerow(entry)


class SJSUScraper:
    def __init__(self, url):
        self.url = url

    def getHTML(self):
        response = requests.get(self.url)
        response.raise_for_status()
        return response.content

    def parseHTML(self, html):
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("table", id="classSchedule")
        schedule_data = []

        for row in table.find_all("tr"):
            if row.find("th"):
                continue
            columns = row.find_all("td")

            department, course, section = columns[0].text.strip().split(" ", 2)
            section = re.findall(r"\d+", section)[0]
            class_number = columns[1].text.strip()
            mode_of_instruction = columns[2].text.strip()
            course_title = columns[3].text.strip()
            satisfies = columns[4].text.strip()
            units = int(float(columns[5].text.strip()))
            class_type = columns[6].text.strip()
            days = columns[7].text.strip()
            times = columns[8].text.strip()
            instructor = columns[9].text
            email_link_tag = columns[9].find('a')
            if email_link_tag and email_link_tag.has_attr('href'):
                instructorEmail = email_link_tag['href']
                instructorEmail = instructorEmail.replace("mailto:","")
            else:
                instructorEmail = ""
            print((instructorEmail))
            location = columns[10].text.strip()
            dates = columns[11].text.strip()
            open_seats = int(float(columns[12].text.strip()))
            notes = columns[13].text.strip()

            entry = CourseScheduleEntry(
                term=None,
                department=department,
                course=course,
                section=section,
                class_number=class_number,
                mode_of_instruction=mode_of_instruction,
                course_title=course_title,
                satisfies=satisfies,
                units=units,
                class_type=class_type,
                days=days,
                times=times,
                instructor=instructor,
                instructorEmail = instructorEmail,
                location=location,
                dates=dates,
                open_seats=open_seats,
                notes=notes,
            )
            schedule_data.append(entry)

        return schedule_data


url = "https://www.sjsu.edu/classes/schedules/spring-2024.php"
scraper = SJSUScraper(url)
content = scraper.getHTML()
class_schedule_data = scraper.parseHTML(content)

exporter = DataExporter()
jsonData = exporter.to_json(class_schedule_data)
print(jsonData)
exporter.to_csv(jsonData, 'ClassSchedule.csv')
exporter.json_dump(jsonData, 'ClassSchedule.json')
