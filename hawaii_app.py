# Dependencies
# Numpy
import numpy as np
# SQL Alchemy
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
# Flask
from flask import Flask, jsonify

# Connect to Hawaii.sqlite database
engine = create_engine("sqlite:///raw_data/hawaii.sqlite?check_same_thread=False")

# Reflect the database
Base = automap_base()
Base.prepare(engine, reflect=True)

# Create the same table references used in the Exploratory Climate Analysis 
Measurement = Base.classes.measurement 
Station = Base.classes.station 

# Create a session for queries
session = Session(engine)

# Initialize Flask
hawaii_app = Flask(__name__)

# Setup Routes
# Landing Page
@hawaii_app.route("/")
def landing():
    return (
        f"Climate Data:<br/>"
        f"/api/v1.0/precipitation - The past year's precipitation data<br/>"
        f"/api/v1.0/stations - Local observation stations<br/>"
        f"/api/v1.0/tobs - The past year's temperature observatons<br/>"
        f"/api/v1.0/YYYY-MM-DD - Temperature statistics for all dates past and including the given <em>start date</em> (Please use YYYY-MM-DD)<br/>"
        f"/api/v1.0/YYYY-MM-DD/YYYY-MM-DD - Temperature statistics for the given <em>start date/end date</em> (Please use YYYY-MM-DD)<br/>"
    )

# Precipitation Page
@hawaii_app.route("/api/v1.0/precipitation")
def precip():
    # Run the query
    precip_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= '2016-08-23').all()

    # Store the query results in a list of dicts
    precip_list = []
    for item in precip_data:
        precip_dict = {}
        precip_dict[item.date] = item.prcp
        precip_list.append(precip_dict)

    # Jsonify the list
    return jsonify(precip_list)

# Stations Page
@hawaii_app.route("/api/v1.0/stations")
def station_data():
    # Run the query
    station_data = session.query(Station.name).all()

    # Convert the list of tuples into a normal list
    station_names = list(np.ravel(station_data))

    # Jsonify the list
    return jsonify(station_names)

# Temperature Observations Page
@hawaii_app.route("/api/v1.0/tobs")
def tobs():
    # Run the query
    temp_data = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= '2016-08-23').all()

    # Store the query results in a list of dicts
    temp_list = []
    for item in temp_data:
        temp_dict = {}
        temp_dict[item.date] = item.tobs
        temp_list.append(temp_dict)

    # Jsonify the list
    return jsonify(temp_list)

# Temp Stats (Start Date) Page
@hawaii_app.route("/api/v1.0/<start>")
def start_date(start):
    # Run the query
    calc_temps = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()

    # Store the query results in a list of dicts
    stats = []
    for item in calc_temps:
        stat_dict = {}
        stat_dict['Minimum Temp'] = item[0]
        stat_dict['Average Temp'] = item[1]
        stat_dict['Maximum Temp'] = item[2]
        stats.append(stat_dict)

    # Throw an error message for a bogus date/query. Jsonify the populated list if date is valid.
    for val in stats[0].values():
        if val is None:
            return jsonify({"Error": f"No data for {start} found"}), 404
        else:
            return jsonify(stats)

@hawaii_app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    # Run the query
    calc_temps = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start, Measurement.date <= end).all()

    # Store the query results in a list of dicts
    stats = []
    for item in calc_temps:
        stat_dict = {}
        stat_dict['Minimum Temp'] = item[0]
        stat_dict['Average Temp'] = item[1]
        stat_dict['Maximum Temp'] = item[2]
        stats.append(stat_dict)

    # Throw an error message for a bogus date/query. Jsonify the populated list if date is valid.
    for val in stats[0].values():
        if val is None:
            return jsonify({"Error": f"No data for {start} to {end} found or entered date was invalid"}), 404
        else:
            return jsonify(stats)
    


# Run the app
if __name__ == "__main__":
    hawaii_app.run(debug=True)