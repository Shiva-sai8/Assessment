import psycopg2


if __name__ == "__main__":
    connection = psycopg2.connect(
        database="weather",
        user="postgres",
        password="secret_weather_password",
        host="localhost",
        port="5432",
    )
    cursor = connection.cursor()

    try:
        cursor.execute("DROP TABLE weather_data;")
    except Exception:
        pass

    connection.commit()
    try:
        cursor.execute(
            """
            CREATE TABLE weather_data (
                id SERIAL PRIMARY KEY,
                date DATE NOT NULL,
                min_temp REAL NOT NULL,
                max_temp REAL NOT NULL,
                precipitation REAL NOT NULL,
                station_id VARCHAR(20) NOT NULL
            );
            CREATE INDEX weather_date_idx ON weather_data(date);
            CREATE INDEX weather_station_id_idx ON weather_data(station_id);
            """
        )

    except Exception as error:
        # if table is already created, print the message and exit
        print(error)

    connection.commit()
    cursor.close()
    connection.close()
