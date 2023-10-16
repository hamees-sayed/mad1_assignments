from flask import Flask
from flask import render_template
from flask import request
import matplotlib.pyplot as plt

app = Flask(__name__)

data = []
with open('data.csv', 'r', encoding="utf-8") as data_file:
    data_file.readline()
    for i in data_file.readlines():
        data.append(list(map(int, i.strip('\n').split(','))))


def error_page():
    return render_template("error.html")


def student_page(s_id):
    if s_id not in [i[0] for i in data]:
        error_page()
        return

    s_data = []
    tot_marks = 0
    for s in data:
        if s[0] == s_id:
            s_data.append(s)
            tot_marks += s[2]

    return render_template("student.html", s_data=s_data, tot_marks=tot_marks)

def course_page(c_id):
    if c_id not in[i[1] for i in data]:
        error_page()
        return

    c_marks = []
    for c in data:
        if c_id == c[1]:
            c_marks.append(c[2])

    plt.hist(c_marks)
    plt.xlabel('Marks')
    plt.ylabel('Frequency')
    plt.savefig('./static/hist_of_marks.png')

    return render_template("course.html", avg_marks=sum(c_marks)/len(c_marks), max_marks=max(c_marks))

@app.route('/', methods=["GET", "POST"])
def main():
    if request.method == "GET":
        return render_template('form.html')
    elif request.method == "POST":
        if request.form["ID"] == "student_id":
            student_page(int(request.form["id_value"]))
        elif request.form["ID"] == "course_id":
            course_page(int(request.form["id_value"]))
        else:
            error_page()
    else:
        error_page()


if __name__ == '__main__':
    app.debug=True
    app.run()