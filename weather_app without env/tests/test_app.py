import unittest
from weather_app.app import app, db, WeatherData

import unittest
from unittest.mock import patch, MagicMock
from flask import json


class TestWeatherApp(unittest.TestCase):
    def setUp(self):
        app.testing = True
        self.client = app.test_client()

    def test_get_weather_data(self):
        response = self.client.get("/api/weather")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/json")

    def test_get_weather_data_with_params(self):
        response = self.client.get("/api/weather?limit=5&offset=2")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/json")

    def test_get_weather_stats(self):
        # create some fake weather data for testing
        weather_data = [
            WeatherData(
                station_id=1,
                date="2022-01-01",
                min_temp=10,
                max_temp=20,
                precipitation=5,
            ),
            WeatherData(
                station_id=1,
                date="2022-01-02",
                min_temp=12,
                max_temp=22,
                precipitation=6,
            ),
            WeatherData(
                station_id=2,
                date="2022-01-01",
                min_temp=15,
                max_temp=25,
                precipitation=7,
            ),
            WeatherData(
                station_id=2,
                date="2022-01-02",
                min_temp=17,
                max_temp=27,
                precipitation=8,
            ),
        ]
        db.session.add_all(weather_data)
        db.session.commit()

        # make a GET request to the API endpoint
        response = self.client.get("/api/weather/stats")

        # check that the response has a 200 status code
        self.assertEqual(response.status_code, 200)

        # check that the response data has the correct format
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
        for item in data:
            self.assertIsInstance(item, dict)
            self.assertCountEqual(
                item.keys(), ["station_id", "year", "min_temp", "max_temp", "avg_temp"]
            )

        # check that the response data has the correct values
        expected_data = [
            {
                "station_id": 1,
                "year": 2022,
                "min_temp": "10.0 F",
                "max_temp": "22.0 F",
                "avg_temp": "16.0 F",
            },
            {
                "station_id": 2,
                "year": 2022,
                "min_temp": "15.0 F",
                "max_temp": "27.0 F",
                "avg_temp": "20.0 F",
            },
        ]
        self.assertEqual(data, expected_data)


if __name__ == "__main__":
    unittest.main()
