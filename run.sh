#!/bin/bash

# Start a Postgres container
docker container stop weather-app-postgres
docker rm -f weather-app-postgres
docker run --name weather-app-postgres -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=secret_weather_password -e POSTGRES_DB=weather -p 5432:5432 -d postgres
# here sleep timer is required to make sure postgres is up and running
sleep 2

# create the database and schema required to run the application
python database.py

sleep 0.5
# there are 2 scripts, this one loads the data in DB in less time using postgres COPY functionality
# it takes around 10 seconds for the application to start and load the data into database
# at the first time.
python load_data_faster.py

# now, application is ready to serve the requests.
# create a virtual env and install the dependencies to run the application

# FOLLOWING COMMANDS SHOULD BE RUN INSIDE weather_app package

# python3 -m venv env
# source env/bin/activate
# pip3 install -r requirements.txt

# run the application using below command, flask server will run on 5000 port
# python app.py

####################                           ENDPOINTS                         ####################

# GOTO http://localhost:5000/apidocs for swagger documentation or look at the
# OpenAPI Specifications in weather_app/swagger directory

# 1. http://localhost:5000 - this is a homepage endpoint
#
# 2. http://localhost:5000/api/weather - this will return all the data from the datastore ordered by date
#    This endpoint accepts 2 query params with integer values for pagination:
#     1. limit - to limit the number of records in the api call
#     2. offset - offset of the records to fetch from
#    If no query param is passed, it will return all the data from the datastore and will take
#    longer time to process the response due to huge data size
#    Ex: http://localhost:5000/api/weather?limit=10&offset=2000
#        http://localhost:5000/api/weather
#        http://localhost:5000/api/weather?limit=100
#        http://localhost:5000/api/weather?offset=900000
#
# 3. http://localhost:5000/api/weather/stats - this endpoint will return the statistics of all the weather
#    stations with minimum, maximum, and average temperature for each year
#
# 4. http://localhost:5000/api/weather/summary - this will return the summary of the weather stations with
#    average minimum and maximum temperatures and total precipitation in millimeters
#    This endpoint accepts 1 query param station_id which will be used to show the summary of given station
#    If no query param is passed, it will return the summary of all weather stations for all years
#    Ex: http://localhost:5000/api/weather/summary?station_id=USC00115326
#        http://localhost:5000/api/weather/summary
