from flask import Flask, jsonify
import datetime as dt
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base

######## DATABASE SETUP
# create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station
session = Session(engine)

######## FLASK SETUP
app = Flask(__name__)

######## FLASK ROUTES
# Define the base route
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )

# Precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    last_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    results = session.query(Measurement.date, Measurement.prcp)\
        .filter(Measurement.date >= last_year).all()
    session.close()
    precipitation_data = {date: prcp for date, prcp in results}
    return jsonify(precipitation_data)

# Stations route
@app.route("/api/v1.0/stations")
def stations():
    station_list = session.query(Station.station).all()
    session.close()
    stations_data = [station[0] for station in station_list]
    return jsonify(stations_data)

# Temperature observations route
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    last_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    most_active_station = session.query(Measurement.station)\
        .group_by(Measurement.station)\
        .order_by(func.count(Measurement.station).desc())\
        .first()[0]
    results = session.query(Measurement.date, Measurement.tobs)\
        .filter(Measurement.station == most_active_station)\
        .filter(Measurement.date >= last_year)\
        .all()
    session.close()
    temp_data = [{"date": date, "tobs": tobs} for date, tobs in results]
    return jsonify(temp_data)

# Start and end date route
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def temp_stats(start, end=None):
    session = Session(engine)
    if not end:
        end = dt.date(2017, 8, 23)
    temperature_stats = session.query(func.min(Measurement.tobs),
                                      func.avg(Measurement.tobs),
                                      func.max(Measurement.tobs))\
        .filter(Measurement.date >= start, Measurement.date <= end)\
        .first()
    session.close()
    temp_stats_dict = {
        "start_date": start,
        "end_date": end,
        "min_temperature": temperature_stats[0],
        "avg_temperature": temperature_stats[1],
        "max_temperature": temperature_stats[2]
    }
    return jsonify(temp_stats_dict)
if __name__ == '__main__':
    app.run()