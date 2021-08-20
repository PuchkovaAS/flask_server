import datetime
import sys

from flask import Flask, request, abort

from flask_restful import Api, Resource, reqparse, inputs, marshal_with
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
db = SQLAlchemy(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///name.db'
api = Api(app)
parser = reqparse.RequestParser()
parser.add_argument(
    'date',
    type=inputs.date,
    help="The event date with the correct format is required! The correct format is YYYY-MM-DD!",
    required=True
)
parser.add_argument(
    'event',
    type=str,
    help="The event name is required!",
    required=True
)


class EventByID(Resource):

    def get(self, event_id):
        event = Event.query.filter(Event.id == event_id).first()
        if event is None:
            abort(404, "The event doesn't exist!")
        return {
            'id': event.id,
            'event': event.name,
            'date': str(event.date)
        }

    def delete(self, event_id):
        event = Event.query.filter(Event.id == event_id).first()
        if event is None:
            abort(404, "The event doesn't exist!")
        Event.query.filter(Event.id == event_id).delete()
        db.session.commit()
        return {
            "message": "The event has been deleted!"
        }


class Event(db.Model):
    __tablename__ = 'events_table'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    date = db.Column(db.Date, nullable=False)


class HelloWorldResource(Resource):
    def get(self):
        # args = parser.parse_args()
        start_time = request.args.get('start_time', None)
        end_time = request.args.get('end_time', None)

        if request.path == '/event':
            if start_time and end_time:
                start_time_date = datetime.datetime.strptime(start_time, "%Y-%m-%d")
                end_time_date = datetime.datetime.strptime(end_time, "%Y-%m-%d")
                events = Event.query.filter(Event.date.between(start_time_date, end_time_date)).all()
            else:
                events = Event.query.all()
        elif request.path == '/event/today':
            events = Event.query.filter(Event.date == datetime.date.today()).all()

        return [{
            'id': event.id,
            'event': event.name,
            'date': str(event.date)
        } for event in events]

    def post(self):
        args = parser.parse_args()

        event = args['event']
        date = args['date']
        event_db = Event(name=event, date=date)
        db.session.add(event_db)
        db.session.commit()
        return {
            "message": "The event has been added!",
            "event": event,
            "date": str(date.date())
        }


api.add_resource(EventByID, '/event/<int:event_id>')
api.add_resource(HelloWorldResource, '/event', '/event/today')
db.create_all()
# do not change the way you run the program
if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg_host, arg_port = sys.argv[1].split(':')
        app.run(host=arg_host, port=arg_port)
    else:
        app.run()
