import os
import tempfile
import datetime
import unittest
import psycopg2

from weather_app.app import app

import shutil
import io
import csv
from unittest.mock import Mock, mock_open, patch

from weather_app.load_data_faster import extract_data_from_row, load_weather_data


class WeatherDataLoadTestCase(unittest.TestCase):

    @patch("weather_app.load_data_faster.os.path.join")
    @patch("weather_app.load_data_faster.Path.is_dir")
    @patch("weather_app.load_data_faster.sys.exit")
    @patch("weather_app.load_data_faster.os.listdir")
    @patch("weather_app.load_data_faster.open", new_callable=mock_open)
    @patch("weather_app.load_data_faster.StringIO")
    @patch("weather_app.load_data_faster.psycopg2.connect")
    def test_load_weather_data(
        self,
        mock_connect,
        mock_StringIO,
        mock_open,
        mock_listdir,
        mock_exit,
        mock_isdir,
        mock_join,
    ):
        mock_cursor = mock_connect.return_value.cursor.return_value
        mock_logger = Mock()

        # Set up mock file data
        file_data = [
            ["20220101", "-10", "0", "5"],
            ["20220102", "-5", "5", "10"],
            ["20220103", "0", "10", "0"],
        ]
        mock_file = mock_open(
            read_data="\n".join(["\t".join(row) for row in file_data])
        )
        mock_listdir.return_value = ["USC123456.csv"]
        mock_open.return_value = mock_file
        mock_isdir.return_value = True

        # Call the function to test
        load_weather_data(mock_cursor, mock_logger)

        # Verify the function behavior
        # Verify that the file was read and processed correctly
        mock_open.assert_called_with(mock_join(), "r")
        mock_StringIO.assert_called_once()
        mock_StringIO.return_value.seek.assert_called_with(0)
        mock_cursor.copy_from.assert_called_once_with(
            mock_StringIO.return_value,
            "weather_data",
            sep="\t",
            null="",
            columns=("date", "min_temp", "max_temp", "precipitation", "station_id"),
        )

        # Verify that the logging occurred correctly
        # mock_logger.debug.assert_called_with("Reading weather data to load in database from: readings")
        mock_logger.debug.assert_called_with(
            "Weather readings are loaded into the database!"
        )
        mock_logger.error.assert_not_called()

        # Verify that the sys.exit() was not called
        mock_exit.assert_not_called()

        # Verify that the expected data was written to the in-memory file
        expected_data = [
            [
                datetime.datetime.strptime(file_data[0][0], "%Y%m%d").strftime(
                    "%Y-%m-%d"
                ),
                int(file_data[0][1]),
                int(file_data[0][2]),
                int(file_data[0][3]),
                "USC123456",
            ],
            [
                datetime.datetime.strptime(file_data[1][0], "%Y%m%d").strftime(
                    "%Y-%m-%d"
                ),
                int(file_data[1][1]),
                int(file_data[1][2]),
                int(file_data[1][3]),
                "USC123456",
            ],
            [
                datetime.datetime.strptime(file_data[2][0], "%Y%m%d").strftime(
                    "%Y-%m-%d"
                ),
                int(file_data[2][1]),
                int(file_data[2][2]),
                int(file_data[2][3]),
                "USC123456",
            ],
        ]
        actual_data = [
            call_args[0][0]
            for call_args in mock_StringIO.return_value.write.call_args_list
        ]
        self.assertEqual(actual_data, expected_data)

    def test_extract_data_from_row_valid_input(self):
        logger = Mock()
        row = ["20220101", "-9999", "200", "10"]
        expected_output = ("2022-01-01", 0, 200, 10)

        self.assertEqual(extract_data_from_row(row, logger), expected_output)

    def test_extract_data_from_row_invalid_date(self):
        logger = Mock()
        row = ["01-01-2022", "-9999", "200", "10"]
        expected_output = None

        self.assertEqual(extract_data_from_row(row, logger), expected_output)

    def test_extract_data_from_row_invalid_temperature(self):
        logger = Mock()
        row = ["20220101", "-9999", "invalid", "10"]
        expected_output = None

        self.assertEqual(extract_data_from_row(row, logger), expected_output)

    def test_extract_data_from_row_invalid_precipitation(self):
        logger = Mock()
        row = ["20220101", "-9999", "200", "invalid"]
        expected_output = None

        self.assertEqual(extract_data_from_row(row, logger), expected_output)


if __name__ == "__main__":
    unittest.main()
