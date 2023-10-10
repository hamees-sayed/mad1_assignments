import sys
import csv
import matplotlib.pyplot as plt
from jinja2 import Template


# storing csv data in local data structure
s_id = []
c_id = []
marks = []
data = []

with open('data.csv', mode='r') as file:
    csvFile = csv.reader(file)
    for lines in csvFile:
        s_id.append(lines[0].strip())
        c_id.append(lines[1].strip())
        marks.append(lines[2].strip())
        data.append({"student_id": lines[0], "course_id": lines[1], "marks": lines[2]})

data = data[1:]
s_id = s_id[1:]
c_id = c_id[1:]
marks = marks[1:]
for d in data:
    for key, value in d.items():
        d[key] = value.strip()


def avg_marks(data, id):
    total_marks = 0
    count = 0
    for elem in data:
        if elem['course_id'] == id:
            total_marks += elem['marks']
            count += 1
    return total_marks / count if count > 0 else 0

def max_marks(data, id):
    max_marks = 0
    for elem in data:
        if elem['course_id'] == id:
            marks = elem['marks']
            if marks > max_marks:
                max_marks = marks
    return max_marks


# templating the file to generate
STUDENT = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body>
    <h1>Student Details</h1>
    <table border=1>
        <tr>
            <th>Student id</th>
            <th>Course id</th>
            <th>Marks</th>
        </tr>
        {% for elem in data if elem['student_id'] == id %}
        <tr>
            <td>{{elem['student_id']}}</td>
            <td>{{elem['course_id']}}</td>
            <td>{{elem['marks']}}</th>
        </tr>
        {% endfor %}
    </table>
</body>
</html>
"""


COURSE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body>
    <h1>Course Details</h1>
    <table border=1>
        <tr>
            <th>Average Marks</th>
            <th>Maximum Marks</th>
        </tr>
        <tr>
            <td>{{ avg_marks(data, id) }}</td>
            <td>{{ max_marks(data, id) }}</td>
        </tr>
    </table>
</body>
</html>
"""


def main(data, id, page):
    template = Template(page)
    f = open("output.html", "w")
    f.write(template.render(data=data, id=id))
    f.close()


def param(arg1, arg2):
    if (arg1 == '-c') and (arg2 in c_id):
        main(data, arg2, COURSE)
    elif (arg1 == '-s') and (arg2 in s_id):
        main(data, arg2, STUDENT)
    else:
        print('Invalid input')


if len(sys.argv) != 3:
    print("Usage: python script.py <option> <id>")
else:
    param(sys.argv[1], sys.argv[2])