import os
import json
from flask import Flask, abort, make_response, request
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api
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
    student=db.relationship("Student", secondary="enrollments")

class Enrollments(db.Model):
    __tablename__ = "enrollments"
    enrollment_id=db.Column(db.Integer,primary_key=True,nullable=False)
    student_id = db.Column(db.Integer,db.ForeignKey("student.student_id"),nullable=False)
    course_id = db.Column(db.Integer,db.ForeignKey("course.course_id"),nullable=False)
    
    
# Custom Error Handling
class ResourceValidationError(HTTPException):
    def __init__(self, status_code, error_code, error_message):
        message = {"error_code": error_code, "error_message": error_message}
        self.response = make_response(json.dumps(message), status_code)


# API Resource Implementation
class Students(Resource):
    def get(self, student_id):
        student = Student.query.filter(Student.student_id == student_id).first()
        if student:
            return {"student_id": student.student_id, 
                    "roll_number": student.roll_number, 
                    "first_name": student.first_name, 
                    "last_name": student.last_name}
        else:
            abort(404, "Student not found")
    
    def post(self):
        args = request.json
        roll_number = args.get("roll_number")
        first_name = args.get("first_name")
        last_name = args.get("last_name")

        student = Student.query.filter(Student.roll_number == roll_number).first()
        if student:
            abort(409, "Student already exist")
        elif roll_number is None or len(roll_number)==0:
            raise ResourceValidationError(400, "STUDENT001", "Roll Number required")
        elif first_name is None  or len(first_name)==0:
            raise ResourceValidationError(400, "STUDENT002", "First Name is required")
        else:
            new_student = Student(roll_number=roll_number, first_name=first_name, last_name=last_name)
            db.session.add(new_student)
            db.session.commit()
            return ({
                "student_id": new_student.student_id,
                "first_name": new_student.first_name,
                "last_name": new_student.last_name,
                "roll_number": new_student.roll_number
            }), 201
            
    def delete(self, student_id):
        student = Student.query.filter(Student.student_id == student_id).first()
        if not student:
            abort(404, "Student not found")
        else:
            Enrollments.query.filter(Enrollments.student_id == student_id).delete()
            db.session.delete(student)
            db.session.commit()
        return {"message":"Successfully Deleted"}
        
    def put(self, student_id):
        student = Student.query.filter(Student.student_id == student_id).first()
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
        else:
            student.roll_number = roll_number
            student.first_name = first_name
            student.last_name = last_name
            db.session.commit()
        return ({
            "student_id": student.student_id,
            "first_name": student.first_name,
            "last_name": student.last_name,
            "roll_number": student.roll_number
        })
            
            
class Courses(Resource):
    def get(self, course_id):
        course = Course.query.filter(Course.course_id == course_id).first()
        if course:
            return {"course_id": course.course_id,
                    "course_name": course.course_name,
                    "course_code": course.course_code,
                    "course_description": course.course_description}
        else:
            abort(404, "Course not found")
            
    def post(self):
        args = request.json
        course_code = args.get("course_code")
        course_name = args.get("course_name")
        course_description = args.get("course_description")
        
        course_exists = Course.query.filter(Course.course_code == course_code).first()
        if course_code is None or len(course_code)==0:
            raise ResourceValidationError(400, "COURSE002", "Course Code is required")
        elif course_name is None  or len(course_name)==0:
            raise ResourceValidationError(400, "COURSE001", "Course Name is required")
        elif course_exists:
            abort(409, "course_code already exist")
        else:
            new_course = Course(course_code=course_code, course_name=course_name, course_description=course_description)
            db.session.add(new_course)
            db.session.commit()
            return ({
                "course_id": new_course.course_id,
                "course_name": new_course.course_name,
                "course_code": new_course.course_code,
                "course_description": new_course.course_description
            })
    
    def delete(self, course_id):
        course = Course.query.filter(Course.course_id == course_id).first()
        if course:
            enrollments = Enrollments.query.filter(Enrollments.course_id == course_id).all()
            for enrolled_course in enrollments:
                db.session.delete(enrolled_course)
            db.session.delete(course)
            db.session.commit()
            return {"message":"Successfully Deleted"}
        else:
            abort(404, "Course not found")
    
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
            return ({
                "course_id": course.course_id,
                "course_name": course.course_name,
                "course_code": course.course_code,
                "course_description": course.description
            })

    
class EnrollmentList(Resource):
    def get(self, student_id):
        enrollments = Enrollments.query.filter(Enrollments.student_id == student_id).all()
        student = Student.query.filter(Student.student_id == student_id).first()
        enrolled_courses_list = []
        if student and len(enrollments) == 0:
            abort(404, "Student is not enrolled in any course")
        elif student and len(enrollments) != 0:
            for enrollment in enrollments:
                enrolled_courses_list.append({"enrollment_id": enrollment.enrollment_id, 
                                              "student_id": enrollment.student_id, 
                                              "course_id": enrollment.course_id})
        else:
            raise ResourceValidationError(400, "ENROLLMENT002", "Student does not exist.")
        return enrolled_courses_list
    
    def post(self, student_id):
        args = request.json
        course_id = args.get("course_id")
        student = Student.query.filter(Student.student_id == student_id).first()
        course = Course.query.filter(Course.course_id == course_id).first()
        enrollments = Enrollments.query.filter(Enrollments.student_id == student_id).all()
        new_enrollment_list = []
        
        if not student:
            abort(404, "Student not found")
        elif not course:
            raise ResourceValidationError(400, "ENROLLMENT001", "Course does not exist")
        else:
            new_enrollment = Enrollments(student_id=student_id, course_id=course_id)
            db.session.add(new_enrollment)
            db.session.commit()
            response_data = [
                {
                    "enrollment_id": new_enrollment.enrollment_id,
                    "student_id": new_enrollment.student_id,
                    "course_id": new_enrollment.course_id
                }
            ]

        return response_data
    
    def delete(self, student_id, course_id):
        student = Student.query.filter(Student.student_id == student_id).first()
        course = Course.query.filter(Course.course_id == course_id).first()
        enrollment = Enrollments.query.filter(Enrollments.student_id == student_id, Enrollments.course_id == course_id).first()
        
        if not student:
            raise ResourceValidationError(400, "ENROLLMENT002", "Student does not exist")
        elif not course:
            raise ResourceValidationError(400, "ENROLLMENT001", "Course does not exist")
        if not enrollment:
            abort(404, "Enrollment for the student not found")
        else:
            db.session.delete(enrollment)
            db.session.commit()
        return {"message":"Successfully Deleted"}
        

# Api Routing
api.add_resource(Students, '/api/student', '/api/student/<int:student_id>')
api.add_resource(Courses, '/api/course', '/api/course/<int:course_id>')
api.add_resource(EnrollmentList, '/api/student/<int:student_id>/course/<int:course_id>', '/api/student/<int:student_id>/course')

# Run
if __name__ == "__main__":
    app.run(debug=True)