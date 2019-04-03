
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect, desc, and_
from flask import Flask, jsonify
import datetime as dt
import numpy as np
import pandas as pd

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
# We can view all of the classes that automap found
Base.classes.keys()
# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station
# Create our session (link) from Python to the DB
session = Session(engine)

# find the last date in the dataset
last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

# convert to datetime type
mydate = dt.datetime.strptime(last_date[0], "%Y-%m-%d")

# Calculate the date 1 year ago from the last data p]oint in the database
start_date = dt.date((int(mydate.strftime('%Y')) - 1), int(mydate.strftime('%m')), int(mydate.strftime('%d')))
busiestStation = session.query(Measurement.station, func.count(Measurement.tobs)).group_by(Measurement.station).order_by(desc(func.count(Measurement.tobs))).first()


app = Flask(__name__)


@app.route("/")
def root():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    columns=[Measurement.date, Measurement.prcp]
    results = session.query(*columns).filter(Measurement.date >= start_date).order_by(Measurement.date.desc()).all()
    return jsonify(dict(results))


@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    stations = session.query(Station.station).all()
    return jsonify(list(np.ravel(stations)))

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    columns=[Measurement.tobs]
    results = session.query(*columns).filter(Measurement.station == busiestStation[0]).filter(Measurement.date >= start_date).all()
    mylist = list(np.ravel(results))
    return jsonify(mylist)

@app.route("/api/v1.0/<start_date>")
def start_temps(start_date):
    # return temps after start date
    session = Session(engine)
    try:
        start_date = dt.date(start_date)
    except:
        print ("There is a problem with the start date")

    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    result = session.query(*sel).filter(Measurement.date >= start_date).all()
    return jsonify(list(np.ravel(result)))

@app.route("/api/v1.0/<start_date>/<end_date>")
def start_end_temps (start_date, end_date):
    session = Session(engine)
    try:
        start_date = dt.date(start_date)
    except:
        print ("There is a problem with the start date")
    try:
        end_date = dt.date(end_date)
    except:
        print ("There is a problem with the end date")

    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    result = session.query(*sel).filter(and_(Measurement.date >= start_date, Measurement.date <= end_date)).all()
    return jsonify(list(np.ravel(result)))
    # return temps after start date

if __name__ == "__main__":
    app.run(debug=True)
