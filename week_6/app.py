import os
import json
from flask import Flask, abort, make_response, request
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api, fields, marshal_with
from werkzeug.exceptions import HTTPException


# App and DB Initialization
app = Flask(__name__)
api = Api(app)
current_dir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(current_dir, 'api_database.sqlite3')}"
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
    student=db.relationship("Student", secondary="enrollment")

class Enrollment(db.Model):
    __tablename__ = "enrollment"
    enrollment_id=db.Column(db.Integer,primary_key=True,nullable=False)
    student_id = db.Column(db.Integer,db.ForeignKey("student.student_id"),nullable=False)
    course_id = db.Column(db.Integer,db.ForeignKey("course.course_id"),nullable=False)

# Response Marshal Format
student_response = {
    "student_id" : fields.Integer,
    "first_name" : fields.String,
    "last_name" : fields.String,
    "roll_number" : fields.String
}

course_response = {
    "course_id" : fields.Integer,
    "course_name" : fields.String,
    "course_code" : fields.String,
    "course_description" : fields.String
}

enroll_response = {
    "enrollment_id": fields.Integer,
    "student_id": fields.Integer,
    "course_id": fields.Integer
}

# Request parser
# args = reqparse.RequestParser()
    
# Custom Error Handling
class ResourceValidationError(HTTPException):
    def __init__(self, status_code, error_code, error_message):
        message = {"error_code": error_code, "error_message": error_message}
        self.response = make_response(json.dumps(message), status_code)


# API Resource Implementation
class Students(Resource):
    @marshal_with(student_response)
    def get(self, student_id):
        student = Student.query.filter(Student.student_id == student_id).first()
        if student is None:
            abort(404, "Student not found")
            
        return student, 200
    
    @marshal_with(student_response)
    def post(self):
        args = request.json
        roll_number = args.get("roll_number")
        first_name = args.get("first_name")
        last_name = args.get("last_name")

        student = student = Student.query.filter(Student.roll_number == roll_number).first()
        
        if roll_number is None or len(roll_number)==0:
            raise ResourceValidationError(400, "STUDENT001", "Roll Number required")
        if first_name is None  or len(first_name)==0:
            raise ResourceValidationError(400, "STUDENT002", "First Name is required")
        if student:
            abort(409, "Student already exist")

        new_student = Student(roll_number=roll_number, first_name=first_name, last_name=last_name)
        db.session.add(new_student)
        db.session.commit()
        return new_student, 201
            
    def delete(self, student_id):
        student = student = Student.query.filter(Student.student_id == student_id).first()
        if not student:
            abort(404, "Student not found")

        db.session.delete(student)
        db.session.commit()
        return "Successfully Deleted", 200
    
    @marshal_with(student_response)
    def put(self, student_id):
        student = student = Student.query.filter(Student.student_id == student_id).first()
        args = request.json
        roll_number = args.get("roll_number")
        first_name = args.get("first_name")
        last_name = args.get("last_name")
        
        if roll_number is None or len(roll_number)==0:
            raise ResourceValidationError(400, "STUDENT001", "Roll Number required")
        elif first_name is None  or len(first_name)==0:
            raise ResourceValidationError(400, "STUDENT002", "First Name is required")
        elif not student:
            abort(404, "Student not found")

        student.roll_number = roll_number
        student.first_name = first_name
        student.last_name = last_name
        db.session.commit()
        return student, 200
            
            
class Courses(Resource):
    @marshal_with(course_response)
    def get(self, course_id):
        course = Course.query.filter(Course.course_id == course_id).first()
        if course: return course, 200
        else: abort(404, "Course not found")
    
    @marshal_with(course_response)       
    def post(self):
        args = request.json
        course_code = args.get("course_code")
        course_name = args.get("course_name")
        course_description = args.get("course_description")
        
        course_exists = Course.query.filter(Course.course_code == course_code).first()
        if course_code is None or len(course_code)==0:
            raise ResourceValidationError(400, "COURSE002", "Course Code is required")
        if course_name is None  or len(course_name)==0:
            raise ResourceValidationError(400, "COURSE001", "Course Name is required")
        if course_exists:
            abort(409, "course_code already exist")

        new_course = Course(course_code=course_code, course_name=course_name, course_description=course_description)
        db.session.add(new_course)
        db.session.commit()
        return new_course, 201
    
    def delete(self, course_id):
        course = Course.query.filter(Course.course_id == course_id).first()
        if not course:
            abort(404, "Course not found")
            
        db.session.delete(course)
        db.session.commit()

        return "Successfully Deleted", 200
    
    @marshal_with(course_response)
    def put(self, course_id):
        course = Course.query.filter(Course.course_id == course_id).first()
        args = request.json
        course_code = args.get("course_code")
        course_name = args.get("course_name")
        course_description = args.get("course_description")
        
        if not course:
            abort(404, "Course not found")
        elif course_code is None or len(course_code)==0:
            raise ResourceValidationError(400, "COURSE002", "Course Code is required")
        elif course_name is None  or len(course_name)==0:
            raise ResourceValidationError(400, "COURSE001", "Course Name is required")
        else:
            course.course_code = course_code
            course.course_name = course_name
            course.course_description = course_description
            db.session.commit()
            
        return course, 200

    
class EnrollmentList(Resource):
    @marshal_with(enroll_response)
    def get(self, student_id):
        student = student = Student.query.filter(Student.student_id == student_id).first()
        enrollments = Enrollment.query.filter(Enrollment.student_id == student_id).all()
        if not student:
            raise ResourceValidationError(400, "ENROLLMENT002", "Student does not exist.")
        if len(enrollments) == 0:
            abort(404, "Student is not enrolled in any course")
        if student and len(enrollments) != 0:
            response_data = [
                {
                    "enrollment_id": enrollment.enrollment_id,
                    "student_id": enrollment.student_id,
                    "course_id": enrollment.course_id
                }
                for enrollment in enrollments
            ]
            return response_data, 200
    
    @marshal_with(enroll_response)
    def post(self, student_id):
        args = request.json
        course_id = args.get("course_id")

        student = student = Student.query.filter(Student.student_id == student_id).first()
        if not student:
            raise ResourceValidationError(400, "ENROLLMENT002", "Student does not exist.")

        course = Course.query.filter(Course.course_id == course_id).first()
        if not course:
            raise ResourceValidationError(400, "ENROLLMENT001", "Course does not exist.")

        enrollment = Enrollment.query.filter(Enrollment.student_id == student_id, Enrollment.course_id == course_id).first()
        if enrollment:
            raise ResourceValidationError(409, "ENROLLMENT004", "Student is already enrolled in the course.")

        new_enrollment = Enrollment(student_id=student_id, course_id=course_id)
        db.session.add(new_enrollment)
        db.session.commit()

        enrollments = Enrollment.query.filter(Enrollment.student_id == student_id).all()
        response_data = [
            {
                    "enrollment_id": enrollment.enrollment_id,
                    "student_id": enrollment.student_id,
                    "course_id": enrollment.course_id
            }
            for enrollment in enrollments
        ]

        return response_data, 201
    
    def delete(self, student_id, course_id):
        student = student = Student.query.filter(Student.student_id == student_id).first()
        course = Course.query.filter(Course.course_id == course_id).first()
        enrollment = Enrollment.query.filter(Enrollment.student_id == student_id, Enrollment.course_id == course_id).first()
        
        if not student:
            raise ResourceValidationError(400, "ENROLLMENT002", "Student does not exist")
        if not course:
            raise ResourceValidationError(400, "ENROLLMENT001", "Course does not exist")
        if not enrollment:
            abort(404, "Enrollment for the student not found")

        db.session.delete(enrollment)
        db.session.commit()
        return "Successfully Deleted", 200
        

# Api Routing
api.add_resource(Students, '/api/student', '/api/student/<int:student_id>')
api.add_resource(Courses, '/api/course', '/api/course/<int:course_id>')
api.add_resource(EnrollmentList, '/api/student/<int:student_id>/course/<int:course_id>', '/api/student/<int:student_id>/course')

# Run
if __name__ == "__main__":
    app.run(debug=True)