import os
import csv
from io import StringIO
import psycopg2
import datetime

# Connect to the database
connection = psycopg2.connect(
    database="weather",
    user="postgres",
    password="secret_weather_password",
    host="localhost",
    port="5432",
)

# Set up a cursor
cursor = connection.cursor()

# Path to the directory containing the CSV files
path = os.path.join(os.getcwd(), "readings")

# Iterate over all files in the directory
for filename in os.listdir(path):
    # rename all the files with .csv extension
    if filename.endswith(".csv"):
        with open(os.path.join(path, filename), "r") as weather_station:
            # Load the CSV data
            reader = csv.reader(weather_station, delimiter="\t")

            # Create an in-memory file-like object to pass to copy_from()
            f = StringIO()
            writer = csv.writer(f, delimiter="\t")

            # Write the rows to the in-memory file-like object
            for row in reader:
                # Extract the data from the row
                date = datetime.datetime.strptime(row[0], "%Y%m%d").strftime("%Y-%m-%d")
                min_temp = int(row[1])
                max_temp = int(row[2])
                precipitation = int(row[3])

                min_temp = 0 if min_temp == -9999 else min_temp
                max_temp = 0 if max_temp == -9999 else max_temp
                precipitation = 0 if precipitation == -9999 else precipitation

                station_id = os.path.basename(weather_station.name).split(".")[
                    0
                ]  # discard the extension of file

                writer.writerow([date, min_temp, max_temp, precipitation, station_id])

            # Move the file position to the beginning of the file
            f.seek(0)

            cursor.copy_from(
                f,
                "weather_data",
                sep="\t",
                null="",
                columns=("date", "min_temp", "max_temp", "precipitation", "station_id"),
            )


# Commit the transaction
connection.commit()
# Close the database connection
cursor.close()
connection.close()
