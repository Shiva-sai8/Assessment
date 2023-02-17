import os
import psycopg2
import csv


if __name__ == "__main__":
    # Connect to the database
    connection = psycopg2.connect(
        database="weather",
        user="postgres",
        password="secret_weather_password",
        host="localhost",
        port="5432",
    )
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
                for row in reader:
                    # Extract the data from the row
                    date = row[0].replace("-", "")
                    min_temp = int(row[1])
                    max_temp = int(row[2])
                    precipitation = int(row[3])

                    min_temp = 0 if min_temp == -9999 else min_temp
                    max_temp = 0 if max_temp == -9999 else max_temp
                    precipitation = 0 if precipitation == -9999 else precipitation

                    station_id = os.path.basename(weather_station.name).split(".")[
                        0
                    ]  # discard the extension of file

                    # Check for duplicates before inserting
                    cursor.execute(
                        "SELECT 1 FROM weather_data WHERE date=%s AND station_id=%s",
                        (date, station_id),
                    )
                    if cursor.fetchone() is None:
                        # Insert the data into the database
                        cursor.execute(
                            "INSERT INTO weather_data (date, min_temp, max_temp, precipitation, station_id) VALUES (%s, %s, %s, %s, %s)",
                            (date, min_temp, max_temp, precipitation, station_id),
                        )
                        connection.commit()

    # Close the database connection
    cursor.close()
    connection.close()
