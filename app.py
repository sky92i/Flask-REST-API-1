import os, sys
from flask import Flask, jsonify, abort
from pymongo.errors import OperationFailure
from pymongo import MongoClient

app = Flask(__name__)

try:
    # connect mongodb with the environment variables
    client = MongoClient(f'mongodb://{os.environ.get("MONGO_USERNAME")}:{os.environ.get("MONGO_PASSWORD")}@{os.environ.get("MONGO_SERVER_HOST")}:{os.environ.get("MONGO_SERVER_PORT")}/university?authSource=admin')
    client.server_info() # check database connection
except Exception as e: # print error and exit
    print ("[x] Database connection error")
    if e.code == 18: print ("[x] Database authentication failed.")
    print ("Error details: ", e.details)
    sys.exit(1)

db = client['university'] # use university database

# defines the /students, /students/<student_id> GET route of the API
@app.route("/students", defaults={'student_id': None})
@app.route("/students/", defaults={'student_id': None})
@app.route("/students/<student_id>", methods=['GET'])
def return_students_data(student_id):
    key = None if student_id == None else {"student_id": student_id}
    student_data = [{"dept_name": stu["dept_name"], "gpa": stu["gpa"], "name": stu["name"], "student_id": stu["student_id"]} 
    for stu in db.student.find(key).sort("student_id")]
    if student_data == []:
        abort(404, description="not found")
    return jsonify(student_data)

# defines the /takes, /takes/<student_id> GET route of the API
@app.route("/takes", defaults={'student_id': None})
@app.route("/takes/", defaults={'student_id': None})
@app.route("/takes/<student_id>", methods=['GET'])
def return_takes_data(student_id):
    key = None if student_id == None else {"student_id": student_id}
    student_data = [{"dept_name": stu["dept_name"], "gpa": stu["gpa"], "name": stu["name"], "student_id": stu["student_id"], 
    "student_takes": [{"course_id": take["course_id"], "credits": take["credits"]} 
    for take in db.takes.find({"student_id": stu["student_id"]}).sort("course_id")]} 
    for stu in db.student.find(key).sort("student_id")]
    if student_data == []:
        abort(404, description="not found")
    return jsonify(student_data)

# 404 error handler
@app.errorhandler(404)
def resource_not_found(e):
    return {"error": "not found"}, 404

# my information
@app.route('/me')
def my_info():
    return jsonify({"name": "Chan Tai Man", "student_id": "12345678D"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=15000) # listen 0.0.0.0:15000
