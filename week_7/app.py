import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy


# App Initialization
app = Flask(__name__)
current_dir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(current_dir, 'week7_database.sqlite3')}"
db = SQLAlchemy()
db.init_app(app)
app.app_context().push()


# DB Models
class Student(db.Model):
    __tablename__ = "student"
    student_id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    roll_number = db.Column(db.String,unique=True,nullable=False)
    first_name= db.Column(db.String,nullable=False)
    last_name= db.Column(db.String)

class Course(db.Model):
    __tablename__ = "course"
    course_id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    course_code = db.Column(db.String,unique=True,nullable=False)
    course_name= db.Column(db.String,nullable=False)
    course_description= db.Column(db.String)
    student=db.relationship("Student", secondary="enrollments")

class Enrollments(db.Model):
    __tablename__ = "enrollments"
    enrollment_id=db.Column(db.Integer,primary_key=True,nullable=False)
    estudent_id = db.Column(db.Integer,db.ForeignKey("student.student_id"),nullable=False)
    ecourse_id = db.Column(db.Integer,db.ForeignKey("course.course_id"),nullable=False)


# API Implementation

# Student API

# List of all Students GET
@app.route('/')
def home():
    students = Student.query.all()
    return render_template('index.html', students=students, len=len(students))

# Student Detail GET
@app.route('/student/<int:student_id>')
def get_student_detail(student_id):
    student = Student.query.filter(Student.student_id == student_id).first()
    enrolled_courses = Course.query.join(Enrollments).filter(Enrollments.estudent_id == student_id).all()
    return render_template('student_detail.html', student=student, enrolled_courses=enrolled_courses)

# Withdraw a Course GET
@app.route('/student/<int:student_id>/withdraw/<int:course_id>')
def withdraw_course(student_id, course_id):
    enrollment = Enrollments.query.filter(Enrollments.estudent_id == student_id, Enrollments.ecourse_id == course_id).first()
    if enrollment:
        db.session.delete(enrollment)
        db.session.commit()
    
    return redirect("/")

# Student Create GET/POST
@app.route('/student/create', methods=['GET', 'POST'])
def add_student():
    courses = Course.query.all()
    if request.method == 'GET':
        return render_template('add_student.html', courses=courses)
    elif request.method == 'POST':
        roll_number = request.form.get('roll')
        f_name = request.form.get('f_name')
        l_name = request.form.get('l_name')
        enrolled_courses = request.form.getlist('courses')

        existing_student = Student.query.filter(Student.roll_number == roll_number).first()
        if existing_student:
            return render_template('already_exists.html', flag='student')

        new_student = Student(roll_number=roll_number, first_name=f_name, last_name=l_name)
        db.session.add(new_student)
        db.session.commit()

        for enrolled_course in enrolled_courses:
            course_id = enrolled_course
            new_enrollment = Enrollments(estudent_id=new_student.student_id, ecourse_id=course_id)
            db.session.add(new_enrollment)
            db.session.commit()

        return redirect('/')

# Student Update GET/POST
@app.route('/student/<int:student_id>/update', methods=['GET', 'POST'])
def update_student(student_id):
    student = Student.query.filter(Student.student_id == student_id).first()
    courses = Course.query.all()
    if request.method == 'GET':
        return render_template('update_student.html', student=student, courses=courses)
    elif request.method == 'POST':
        student.first_name = request.form.get('f_name')
        student.last_name = request.form.get('l_name')

        updated_enrollment = request.form.getlist('courses')
        Enrollments.query.filter(Enrollments.estudent_id == student_id).delete()

        for enrolled_course in updated_enrollment:
            course_id = enrolled_course
            new_enrollment = Enrollments(estudent_id=student.student_id, ecourse_id=course_id)
            db.session.add(new_enrollment)

        db.session.commit()

        return redirect('/')

# Student Delete GET
@app.route('/student/<int:student_id>/delete')
def delete_student(student_id):
    student = Student.query.filter(Student.student_id == student_id).first()

    if student:
        Enrollments.query.filter(Enrollments.estudent_id == student.student_id).delete()

        db.session.delete(student)
        db.session.commit()

    return redirect('/')


# Course API

# List of all Courses GET
@app.route('/courses')
def get_courses():
    courses = Course.query.all()
    return render_template('course_list.html', courses=courses, len=len(courses))
    
# Course Detail GET
@app.route('/course/<int:course_id>')
def get_course_detail(course_id):
    course = Course.query.filter(Course.course_id == course_id).first()
    enrolled_students = Student.query.join(Enrollments).filter(Enrollments.ecourse_id == course_id).all()
    return render_template('course_detail.html', course=course, enrolled_students=enrolled_students)

# Course Create GET
@app.route('/course/create', methods=['GET', 'POST'])
def add_course():
    if request.method == 'GET':
        return render_template('add_course.html')
    elif request.method == 'POST':
        course_code = request.form.get('code')
        course_name = request.form.get('c_name')
        course_desc = request.form.get('desc')

        existing_course = Course.query.filter(Course.course_code == course_code).first()
        if existing_course:
            return render_template('already_exists.html')

        new_course = Course(course_code=course_code, course_name=course_name, course_description=course_desc)
        db.session.add(new_course)
        db.session.commit()

        return redirect('/courses')
    
# Course Update GET/POST
@app.route('/course/<int:course_id>/update', methods=['GET', 'POST'])
def update_course(course_id):
    course = Course.query.filter(Course.course_id == course_id).first()
    if request.method == 'GET':
        return render_template('update_course.html', course=course)
    elif request.method == 'POST':
        course.course_name = request.form.get('c_name')
        course.course_description = request.form.get('desc')
        db.session.commit()

    return redirect('/courses')

# Course Delete GET
@app.route('/course/<int:course_id>/delete')
def delete_course(course_id):
    course = Course.query.filter(Course.course_id == course_id).first()

    if course:
        Enrollments.query.filter(Enrollments.ecourse_id == course_id).delete()

        db.session.delete(course)
        db.session.commit()

    return redirect('/')
    

if __name__ == '__main__':
    app.run(debug=True)