from flask import request
import psycopg2
from flask import Flask, jsonify
from sqlalchemy import func
from flask_sqlalchemy import SQLAlchemy

from flasgger import Swagger
from flasgger.utils import swag_from


app = Flask(__name__)
swagger = Swagger(app)
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "postgresql://postgres:secret_weather_password@localhost/weather"
db = SQLAlchemy(app)


class WeatherData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    min_temp = db.Column(db.Float, nullable=False)
    max_temp = db.Column(db.Float, nullable=False)
    precipitation = db.Column(db.Float, nullable=False)
    station_id = db.Column(db.String(128), nullable=False)


@app.route("/")
def hello():
    """
    Weather App root URL to show the heading

    :return: static HTML heading about the project
    """
    return "<center><h1>Welcome to the Weather Station Application</h1></center>"


# Define the route for the weather_app API
@app.route("/api/weather")
@swag_from("swagger/weather.yml")
def get_weather_data():
    """
    Gets the weather data for all stations.
    For pagination, limit and offset query params can be used with appropriate values

    :return: JSON data containing the weather related information
    """
    # Connect to the Postgres database
    conn = psycopg2.connect(
        host="localhost",
        database="weather",
        user="postgres",
        password="secret_weather_password",
    )
    cursor = conn.cursor()

    # Parse the limit and offset query parameters
    limit = request.args.get("limit", default=10, type=int)
    offset = request.args.get("offset", default=0, type=int)

    # Execute the SQL query with LIMIT and OFFSET clauses
    cursor.execute(
        "SELECT * FROM weather_data ORDER BY date, station_id LIMIT %s OFFSET %s",
        (limit, offset),
    )

    # Fetch the results and convert them to a list of dictionaries
    results = cursor.fetchall()
    weather_data = [
        dict(zip(("date", "min_temp", "max_temp", "precipitation", "station_id"), row))
        for row in results
    ]

    # Close the database connection
    cursor.close()
    conn.close()

    # Return the weather data as JSON
    return jsonify(weather_data)


@app.route("/api/weather/stats")
@swag_from("swagger/weather_stats.yml")
def get_weather_stats():
    """
    Gets the statistics for the all the stations for all years.
    minimum temperature, maximum temperature and total precipitation

    :return: JSON data containing the summarized weather information for all stations
    """
    query = (
        db.session.query(
            WeatherData.station_id,
            func.date_part("year", WeatherData.date).label("year"),
            func.min(WeatherData.min_temp).label("min_temp"),
            func.max(WeatherData.max_temp).label("max_temp"),
            func.avg((WeatherData.min_temp + WeatherData.max_temp) / 2).label(
                "avg_temp"
            ),
        )
        .group_by(WeatherData.station_id, "year")
        .all()
    )

    stats = []
    for row in query:
        stats.append(
            {
                "station_id": row.station_id,
                "year": row.year,
                "min_temp": f"{row.min_temp} F",
                "max_temp": f"{row.max_temp} F",
                "avg_temp": f"{row.avg_temp} F",
            }
        )

    return jsonify(stats)


@app.route("/api/weather/summary")
@swag_from("swagger/weather_summary.yml")
def weather_summary():
    """
    Gets the summarized data for the stations for all years.
    station_id query param can be used to fetch the data for only specific station

    :return: JSON data containing the summarized weather information for all/given stations
    """
    station_id = request.args.get("station_id")

    # Base query
    query = db.session.query(
        func.date_trunc("year", WeatherData.date).label("year"),
        WeatherData.station_id,
        func.avg(WeatherData.max_temp).label("avg_max_temp"),
        func.avg(WeatherData.min_temp).label("avg_min_temp"),
        func.sum(WeatherData.precipitation).label("total_precipitation"),
    )

    # Apply filters
    if station_id:
        query = query.filter(WeatherData.station_id == station_id)

    # Group by year and station_id
    query = query.group_by("year", "station_id")

    # Execute the query
    results = query.all()

    stats = []
    for result in results:
        stat = {
            "year": result.year.strftime("%Y"),
            "station_id": result.station_id,
            "avg_max_temp": f"{(float(result.avg_max_temp) - 32) / 1.8000} C",  # convert to celsius
            "avg_min_temp": f"{(float(result.avg_min_temp) - 32) / 1.8000} C",  # convert to celsius
            "total_precipitation": f"{float(result.total_precipitation) * 0.01} cm",  # convert to centimeters
        }
        stats.append(stat)

    return jsonify(stats)


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
