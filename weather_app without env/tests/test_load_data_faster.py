import os
import tempfile
import datetime
import unittest
import psycopg2
from app import app
import shutil
import io
import csv


class WeatherDataLoadTestCase(unittest.TestCase):
    def setUp(self):
        self.db_fd, app.config['DATABASE'] = tempfile.mkstemp()
        app.config['TESTING'] = True
        self.app = app.test_client()
        with app.app_context():
            connection = psycopg2.connect(
                database="weather",
                user="postgres",
                password="secret_weather_password",
                host="localhost",
                port="5432",
            )
            cursor = connection.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS weather_data (
                    id SERIAL PRIMARY KEY,
                    date DATE NOT NULL,
                    min_temp INTEGER NOT NULL,
                    max_temp INTEGER NOT NULL,
                    precipitation INTEGER NOT NULL,
                    station_id TEXT NOT NULL
                )
                """
            )
            connection.commit()
            cursor.close()
            connection.close()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(app.config['DATABASE'])

    def test_weather_data_load(self):
        # Create a test directory with some sample files
        test_dir = tempfile.mkdtemp()
        try:
            # Create some sample data
            sample_data = [
                [20220101, 50, 70, 10],
                [20220102, 40, 60, 15],
                [20220103, 30, 50, 20]
            ]
            for filename in ['station1.csv', 'station2.csv']:
                with open(os.path.join(test_dir, filename), 'w') as f:
                    writer = csv.writer(f, delimiter='\t')
                    for row in sample_data:
                        writer.writerow([row[0], row[1], row[2], row[3]])
                    f.flush()
                    f.close()

            # Load the test data into the database
            with app.app_context():
                connection = psycopg2.connect(
                    database="weather",
                    user="postgres",
                    password="secret_weather_password",
                    host="localhost",
                    port="5432",
                )
                cursor = connection.cursor()
                path = os.path.join(os.getcwd(), test_dir)
                for filename in os.listdir(path):
                    if filename.endswith(".csv"):
                        with open(os.path.join(path, filename), "r") as weather_station:
                            reader = csv.reader(weather_station, delimiter="\t")
                            f = io.StringIO()
                            writer = csv.writer(f, delimiter="\t")
                            for row in reader:
                                date = datetime.datetime.strptime(row[0], "%Y%m%d").strftime("%Y-%m-%d")
                                min_temp = int(row[1])
                                max_temp = int(row[2])
                                precipitation = int(row[3])
                                min_temp = 0 if min_temp == -9999 else min_temp
                                max_temp = 0 if max_temp == -9999 else max_temp
                                precipitation = 0 if precipitation == -9999 else precipitation
                                station_id = os.path.basename(weather_station.name).split(".")[0]
                                writer.writerow([date, min_temp, max_temp, precipitation, station_id])
                            f.seek(0)
                            cursor.copy_from(
                                f,
                                "weather_data",
                                sep="\t",
                                null="",
                                columns=("date", "min_temp", "max_temp", "precipitation", "station_id"),
                            )
                            connection.commit()
                            cursor.execute("SELECT COUNT(*) FROM weather_data")
                            count = cursor.fetchone()[0]
                            self.assertEqual(count, 3 * (len(os.listdir(test_dir)) - 1))

        finally:
            shutil.rmtree(test_dir)


if __name__ == "__main__":
    unittest.main()
