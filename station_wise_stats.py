from models import db, WeatherData
from sqlalchemy import func
from flask import current_app


def calculate_station_wise_weather_stats():
    with current_app.app_context():
        # Get all the unique weather station IDs from the database
        stations = db.session.query(WeatherData.station_id).distinct().all()

    # Loop through each station
    for station in stations:
        # Get all the unique years for the current station
        years = (
            db.session.query(func.extract("year", WeatherData.date))
            .filter_by(station_id=station[0])
            .distinct()
            .all()
        )

        # Loop through each year
        for year in years:
            # Calculate the average maximum temperature, average minimum temperature, and total accumulated precipitation for the current station and year
            result = (
                db.session.query(
                    func.avg(WeatherData.max_temp).label("avg_max_temp"),
                    func.avg(WeatherData.min_temp).label("avg_min_temp"),
                    func.sum(WeatherData.precipitation).label("total_precipitation"),
                )
                .filter_by(station_id=station[0])
                .filter(func.extract("year", WeatherData.date) == year[0])
                .all()
            )

            # Print the results
            print(f"Station {station[0]} - Year {year[0]}:")
            print(f"Average maximum temperature: {result[0][0]}")
            print(f"Average minimum temperature: {result[0][1]}")
            print(f"Total accumulated precipitation: {result[0][2]}")


if __name__ == "__main__":
    calculate_station_wise_weather_stats()
