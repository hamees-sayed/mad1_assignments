import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
current_dir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(current_dir, 'database.db')}"
db = SQLAlchemy()
db.init_app(app)
app.app_context().push()

class Course(db.Model):
    __tablename__ = 'course'
    course_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    course_code = db.Column(db.String, nullable=False)
    course_name = db.Column(db.String, nullable=False)
    course_description = db.Column(db.String)

class Student(db.Model):
    __tablename__ = 'student'
    student_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    roll_no = db.Column(db.String, unique=True, nullable=False)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String)

class Enrollments(db.Model):
    __tablename__ ='enrollments'
    enrollment_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    estudent_id = db.Column(db.Integer, db.ForeignKey('student.student_id'), nullable=False)
    ecourse_id = db.Column(db.Integer, db.ForeignKey('course.course_id'), nullable=False)
    student = db.relationship('Student', backref='enrollments')
    course = db.relationship('Course', backref='enrollments')



@app.route('/')
def home():
    students = Student.query.all()
    return render_template('home.html', students=students, len=len(students))

@app.route('/student/create', methods=['GET', 'POST'])
def add_student():
    if request.method == 'GET':
        return render_template('add_student.html')
    elif request.method == 'POST':
        roll_no = request.form.get('roll')
        f_name = request.form.get('f_name')
        l_name = request.form.get('l_name')
        enrolled_courses = request.form.getlist('courses')

        existing_student = Student.query.filter(Student.roll_no == roll_no).first()
        if existing_student:
            return render_template('already_exists.html')

        new_student = Student(roll_no=roll_no, first_name=f_name, last_name=l_name)
        db.session.add(new_student)
        db.session.commit()

        for enrolled_course in enrolled_courses:
            course_id = int(enrolled_course.split('_')[1])
            new_enrollment = Enrollments(estudent_id=new_student.student_id, ecourse_id=course_id)
            db.session.add(new_enrollment)
            db.session.commit()

        return redirect('/')

@app.route('/student/<int:student_id>/update', methods=['GET', 'POST'])
def update_student(student_id):
    student = Student.query.filter(Student.student_id == student_id).first()
    if request.method == 'GET':
        return render_template('update_student.html', student=student)
    elif request.method == 'POST':
        student.first_name = request.form.get('f_name')
        student.last_name = request.form.get('l_name')

        updated_enrollment = request.form.getlist('courses')
        Enrollments.query.filter(Enrollments.estudent_id == student_id).delete()

        for enrolled_course in updated_enrollment:
            course_id = int(enrolled_course.split('_')[1])
            new_enrollment = Enrollments(estudent_id=student.student_id, ecourse_id=course_id)
            db.session.add(new_enrollment)

        db.session.commit()

        return redirect('/')

@app.route('/student/<int:student_id>/delete')
def delete_student(student_id):
    student = Student.query.filter(Student.student_id == student_id).first()
    Enrollments.query.filter(Enrollments.estudent_id == student.student_id).delete()

    db.session.delete(student)
    db.session.commit()

    return redirect('/')

@app.route('/student/<int:student_id>')
def get_student_detail(student_id):
    student = Student.query.filter(Student.student_id == student_id).first()
    enrolled_courses = Course.query.join(Enrollments).filter(Enrollments.estudent_id == student_id).all()
    return render_template('student_detail.html', student=student, enrolled_courses=enrolled_courses)


if __name__ == '__main__':
    app.run(debug=True)