import unittest
import json

from weather_app.app import app, db, WeatherData


class WeatherSummaryTestCase(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        db.create_all()
        self.client = app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_weather_summary_no_stations(self):
        # Test that summary data for all stations is returned when no station ID is provided
        data = [
            WeatherData(
                station_id="A",
                date="2021-01-01",
                min_temp=10,
                max_temp=20,
                precipitation=100,
            ),
            WeatherData(
                station_id="B",
                date="2021-01-01",
                min_temp=15,
                max_temp=25,
                precipitation=200,
            ),
            WeatherData(
                station_id="A",
                date="2022-01-01",
                min_temp=12,
                max_temp=22,
                precipitation=150,
            ),
        ]
        db.session.add_all(data)
        db.session.commit()

        expected_response = [
            {
                "year": "2021",
                "station_id": "A",
                "avg_max_temp": "-6.666666666666667 C",
                "avg_min_temp": "-11.11111111111111 C",
                "total_precipitation": "1.0 cm",
            },
            {
                "year": "2021",
                "station_id": "B",
                "avg_max_temp": "-3.888888888888889 C",
                "avg_min_temp": "-9.444444444444445 C",
                "total_precipitation": "2.0 cm",
            },
            {
                "year": "2022",
                "station_id": "A",
                "avg_max_temp": "-5.555555555555555 C",
                "avg_min_temp": "-10.0 C",
                "total_precipitation": "1.5 cm",
            },
        ]

        response = self.client.get("/api/weather/summary")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data), expected_response)

    def test_weather_summary_one_station(self):
        # Test that summary data for one station is returned when station ID is provided
        data = [
            WeatherData(
                station_id="A",
                date="2021-01-01",
                min_temp=10,
                max_temp=20,
                precipitation=100,
            ),
            WeatherData(
                station_id="B",
                date="2021-01-01",
                min_temp=15,
                max_temp=25,
                precipitation=200,
            ),
            WeatherData(
                station_id="A",
                date="2022-01-01",
                min_temp=12,
                max_temp=22,
                precipitation=150,
            ),
        ]
        db.session.add_all(data)
        db.session.commit()

        expected_response = [
            {
                "year": "2021",
                "station_id": "A",
                "avg_max_temp": "-6.666666666666667 C",
                "avg_min_temp": "-11.11111111111111 C",
                "total_precipitation": "1.0 cm",
            },
            {
                "year": "2022",
                "station_id": "A",
                "avg_max_temp": "-5.555555555555555 C",
                "avg_min_temp": "-10.0 C",
                "total_precipitation": "1.5 cm",
            },
        ]

        response = self.client.get("/api/weather/summary?station_id=A")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data), expected_response)


if __name__ == "__main__":
    unittest.main()
