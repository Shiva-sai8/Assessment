import os
import csv
import logging
import sys

from io import StringIO
import psycopg2
import datetime

from pathlib import Path


def get_logger():
    """
    Returns a logger object to log messages

    :return: Logger object
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # create formatter and add it to the handler
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)

    logger.addHandler(ch)

    return logger


def get_db_connection():
    """
    Returns the postgres database connection to load the data in DB

    :return: Database connection object
    """
    return psycopg2.connect(
        database="weather",
        user="postgres",
        password="secret_weather_password",
        host="localhost",
        port="5432",
    )


def get_db_cursor(connection):
    """
    Returns the postgres database cursor to handle DB queries to load the data

    :param connection: Database connection object
    :return: Database cursor object
    """
    return connection.cursor()


def close_db_cursor(cursor):
    """
    Closes the cursor of the database

    :param cursor: Database cursor object
    :return: None
    """
    cursor.close()


def close_db_connection(connection):
    """
    Closes the connection of the database

    :param connection: Database connection object
    :return: None
    """
    connection.close()


def load_weather_data(cursor, logger):
    """
    Loads the weather data into postgres database.
    This reads the weather data required to load from readings package

    :param cursor: Database cursor object created for inserting the data in weather DB
    :param logger: Logger object to log the error messages and general updates
    :return: None
    """
    readings_path = os.path.join(os.getcwd(), "readings")
    logger.debug(f"Reading weather data to load in database from: {readings_path}")

    if not Path(readings_path).is_dir():
        logger.error(f"Data directory is not present, please store all the files in readings directory.")
        sys.exit(0)

    for filename in os.listdir(readings_path):
        if filename.endswith(".csv"):
            with open(os.path.join(readings_path, filename), "r") as weather_station:
                try:
                    reader = csv.reader(weather_station, delimiter="\t")
                except Exception as e:
                    logger.error(f"Could not load data from file: {filename}, got error: {e}")
                    continue

                f = StringIO()
                writer = csv.writer(f, delimiter="\t")

                for row in reader:
                    try:
                        date, min_temp, max_temp, precipitation = extract_data_from_row(row, logger)
                    except Exception as e:
                        logger.error(f"Error extracting data from row: {e}")
                        continue

                    station_id = os.path.basename(weather_station.name).split(".")[0]

                    try:
                        writer.writerow([date, min_temp, max_temp, precipitation, station_id])
                    except Exception as e:
                        logger.error(f"Error saving the record in database: {e}")
                        continue

                f.seek(0)

                try:
                    insert_data_into_database(cursor, f)
                except Exception as e:
                    logger.error(f"Error inserting data into database: {e}")
                    continue

    logger.debug(f"Weather readings are loaded into the database!")


def extract_data_from_row(row, logger):
    """
    Extracts the relevant data from a row of a weather data CSV file.

    :param row: A list containing the fields of a row in the CSV file.
    :param logger: Logger object to log error messages.
    :return: A tuple containing the extracted data (date, min_temp, max_temp, precipitation).
    """
    try:
        date = datetime.datetime.strptime(row[0], "%Y%m%d").strftime("%Y-%m-%d")
    except Exception as e:
        logger.error(f"Error reading the date from row: {e}")
        raise

    min_temp = int(row[1])
    max_temp = int(row[2])
    precipitation = int(row[3])

    min_temp = 0 if min_temp == -9999 else min_temp
    max_temp = 0 if max_temp == -9999 else max_temp
    precipitation = 0 if precipitation == -9999 else precipitation

    return date, min_temp, max_temp, precipitation


def insert_data_into_database(cursor, f):
    """
    Inserts weather data from an in-memory file into the database.

    :param cursor: Database cursor object created for inserting the data in weather DB.
    :param f: An in-memory file-like object containing the weather data to insert.
    """
    cursor.copy_from(
        f,
        "weather_data",
        sep="\t",
        null="",
        columns=("date", "min_temp", "max_temp", "precipitation", "station_id"),
    )


if __name__ == "__main__":
    connection = get_db_connection()
    cursor = get_db_cursor(connection)
    logger = get_logger()

    load_weather_data(cursor, logger)

    try:
        # Commit the transaction
        connection.commit()
    except Exception as e:
        logger.error(f"Error loading the weather data in DB: {e}")

    # Close the database cursor and connection
    close_db_cursor(cursor)
    logger.debug("Database cursor is closed.")
    close_db_connection(connection)
    logger.debug("Database connection is closed.")
