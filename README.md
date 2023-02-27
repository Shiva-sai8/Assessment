
# About Postgres database
This project requires postgres database and we are using docker container for that.

Name of the docker container for this is: weather-app-postgres  
Database username: postgres  
Database password: secret_weather_password  
Database name: weather

###Steps to start postgres in docker:
1. docker container stop weather-app-postgres (this stops the container if there is already a one runnning)
2. docker rm -f weather-app-postgres
3. docker run --name weather-app-postgres -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=secret_weather_password -e POSTGRES_DB=weather -p 5432:5432 -d postgres


### Creation of the database and schema required to run the application is handled in:
python database.py

### Loading the data in newly created database:
python load_data_faster.py  

There are 2 scripts, this one loads the data in DB in less time using postgres COPY functionality
it takes around 10 seconds for the application to start and load the data into database at the first time.

### Application is ready to serve the requests once the database is running and the data is loaded in DB.

## Steps to run the web application:
1. create a virtual env and install the dependencies to run the application
2. FOLLOWING COMMANDS SHOULD BE RUN INSIDE weather_app package 
   1. python3 -m venv env
   2. source env/bin/activate
   3. pip3 install -r requirements.txt
3. python app.py

# ENDPOINTS:

### GOTO http://localhost:5000/apidocs for swagger documentation or look at the OpenAPI Specifications in weather_app/swagger directory

### 1. http://localhost:5000
This is a homepage endpoint

### 2. http://localhost:5000/api/weather
This will return all the data from the datastore ordered by date
This endpoint accepts 2 query params with integer values for pagination:
1. limit - to limit the number of records in the api call
2. offset - offset of the records to fetch from
    If no query param is passed, it will return all the data from the datastore and will take
    longer time to process the response due to huge data size  
    Examples: 
   1. http://localhost:5000/api/weather?limit=10&offset=2000
   2. http://localhost:5000/api/weather
   3. http://localhost:5000/api/weather?limit=100
   4. http://localhost:5000/api/weather?offset=900000

### 3. http://localhost:5000/api/weather/stats
This endpoint will return the statistics of all the weather stations with minimum, maximum, and average temperature for each year

### 4. http://localhost:5000/api/weather/summary
This will return the summary of the weather stations with average minimum and maximum temperatures and total precipitation in millimeters.  
This endpoint accepts 1 query param station_id which will be used to show the summary of given station.  
If no query param is passed, it will return the summary of all weather stations for all years.  
Examples:
1. http://localhost:5000/api/weather/summary?station_id=USC00115326
2. http://localhost:5000/api/weather/summary
