import sys
import matplotlib.pyplot as plt
from jinja2 import Template


data = []
with open('data.csv', 'r', encoding="utf-8") as data_file:
    data_file.readline()
    for i in data_file.readlines():
        data.append(list(map(int, i.strip('\n').split(','))))


def error_page():
    err_page = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body>
            <h1>Wrong Inputs</h1>
            <p>Something went wrong</p>
        </body>
        </html>"""

    with open('output.html', 'w', encoding="utf-8") as err_output:
        err_output.write(err_page)

def student_page(s_id):
    if s_id not in [i[0] for i in data]:
        error_page()
        return

    student = """<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body>
            <h1>Student Details</h1>
            <table border=1>
                <tr>
                    <th>Student ID</th>
                    <th>Course ID</th>
                    <th>Marks</th>
                </tr>
                {% for i in s_data %}
                <tr>
                    <td>{{ i[0] }}</td>
                    <td>{{ i[1] }}</td>
                    <td>{{ i[2] }}</td>
                </tr>
                {% endfor %}
                <tr>
                    <td colspan=2>Total Marks</td>
                    <td>{{ tot_marks }}</td>
                </tr>
            </table>
        </body>
        </html>"""

    s_data = []
    tot_marks = 0
    for s in data:
        if s[0] == s_id:
            s_data.append(s)
            tot_marks += s[2]

    with open('output.html', 'w', encoding="utf-8") as st_output:
        st_output.write(Template(student).render(s_data=s_data, tot_marks=tot_marks))

def course_page(c_id):
    if c_id not in[i[1] for i in data]:
        error_page()
        return

    course = """<!DOCTYPE html>
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
                    <td>{{ avg_marks }}</td>
                    <td>{{ max_marks }}</td>
                </tr>
            </table>
            <img src="hist_of_marks.png" alt="histogram of marks">
        </body>
        </html>"""

    c_marks = []
    for c in data:
        if c_id == c[1]:
            c_marks.append(c[2])

    plt.hist(c_marks)
    plt.xlabel('Marks')
    plt.ylabel('Frequency')
    plt.savefig('hist_of_marks.png')

    with open('output.html', 'w', encoding="utf-8") as c_output:
        c_output.write(Template(course).render(avg_marks=sum(c_marks)/len(c_marks), max_marks=max(c_marks)))

if __name__ == '__main__':
    if sys.argv[1] == '-s':
        student_page(int(sys.argv[2]))
    elif sys.argv[1] == '-c':
        course_page(int(sys.argv[2]))
    else:
        error_page()