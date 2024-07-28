from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from password import my_password
from flask_marshmallow import Marshmallow
from marshmallow import fields
from marshmallow import ValidationError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+mysqlconnector://root:{my_password}@localhost/gym'
db = SQLAlchemy(app)
ma = Marshmallow(app)

class MemberSchema(ma.Schema):
    id = fields.Integer(required=True)
    name = fields.String(required=True)
    age = fields.Integer(required=True)

    class Meta:
        fields = ("id", "name", "age")

member_schema = MemberSchema()
members_schema = MemberSchema(many=True)

class WorkoutSchema(ma.Schema):
    member_id = fields.Integer(required=True)
    session_id = fields.Integer(required=True)
    date = fields.Date(required=True)
    duration_minutes = fields.Integer(required=True)
    calories_burned = fields.Integer(required=True)
    
    class Meta:
        fields = ("member_id", "session_id", "date", "duration_minutes", "calories_burned")

workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many=True)

class Member(db.Model):
    __tablename__ = 'Members'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    age = db.Column(db.Integer)

class WorkoutSession(db.Model):
    __tablename__ = 'Workoutsessions'
    member_id = db.Column(db.Integer,  db.ForeignKey('Members.id'), primary_key=True)
    session_id = db.Column(db.Integer)
    date = db.Column(db.Date)
    duration_minutes = db.Column(db.Integer)
    calories_burned = db.Column(db.Integer)

@app.route('/')
def home():
    return 'Sup asshole'

@app.route('/members', methods=['GET'])
def get_members():
    members = Member.query.all()
    return members_schema.jsonify(members)

@app.route('/members', methods=['POST'])
def add_member():
    try:
        member_data = member_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400

    new_member = Member(id=member_data['id'], name=member_data['name'], age=member_data['age'])
    db.session.add(new_member)
    db.session.commit()
    return jsonify({"message": "New member added successfully"}), 201

@app.route('/members/<int:id>', methods=['PUT'])
def update_member(id):
    member = Member.query.get_or_404(id)
    try:
        member_data = member_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    member.id = member_data['id']
    member.name = member_data['name']
    member.age = member_data['age']
    db.session.commit()
    return jsonify({"message": "Member details updated successfully"}), 200

@app.route('/members/<int:id>', methods=['DELETE'])
def delete_member(id):
    member = Member.query.get_or_404(id)
    db.session.delete(member)
    db.session.commit()
    return jsonify({"message": "Member removed successfully"}), 200

@app.route('/workoutsessions', methods=['GET'])
def get_workout_sessions():
    workoutsessions = WorkoutSession.query.all()
    return workouts_schema.jsonify(workoutsessions)

@app.route('/workoutsessions', methods=['POST'])
def add_workoutsession():
    try:
        workout_data = workout_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400

    new_workoutsession = WorkoutSession(member_id=workout_data['member_id'], session_id=workout_data['session_id'], date=workout_data['date'], duration_minutes=workout_data['duration_minutes'], calories_burned=workout_data['calories_burned'])
    db.session.add(new_workoutsession)
    db.session.commit()
    return jsonify({"message": "New workout session added successfully"}), 201

@app.route('/workoutsessions/<int:id>', methods=['PUT'])
def update_workout(id):
    workout = WorkoutSession.query.get_or_404(id)
    try:
        workout_data = workout_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    workout.member_id = workout_data['member_id']
    workout.session_id = workout_data['session_id']
    workout.date = workout_data['date']
    workout.duration_minutes = workout_data['duration_minutes']
    workout.calories_burned = workout_data['calories_burned']
    db.session.commit()
    return jsonify({"message": "Workout details updated successfully"}), 200

@app.route('/workoutsessions/<int:id>', methods=['DELETE'])
def delete_workout(id):
    workout = WorkoutSession.query.get_or_404(id)
    db.session.delete(workout)
    db.session.commit()
    return jsonify({"message": "Workout removed successfully"}), 200

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)