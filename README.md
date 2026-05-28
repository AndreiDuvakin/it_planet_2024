[🇷🇺 Русский](README_RU.md)

## About the project

This project was created for participation in the IT-Planet Olympiad.

# IT-Planet_If_else_Duvakin

## Weather History Company

## Conditions

The Participant grants the Organizer permission to use, modify, publish the project, and continue using it.
distribution, including the right to make changes, additions, prefaces, comments, and any other revisions.
The participant guarantees that the project does not violate the current legislation, does not contain information discrediting individuals.
or products, does not cause lawsuits or claims, does not violate the rights and interests of third parties, complies with
public interests, principles of humanity and morality. The participant confirms that all materials used in the project and
the data is its own property or used with the permission of the copyright holders, which does not restrict the use of
the project is fully implemented by the Organizer.
The participant confirms that the transfer of exclusive rights to the project created within the framework of the competition does not violate the rights of:
third parties and that all project materials can be used by the Organizer without any restrictions.

## System Description

The system is an API service developed in Python using the Flask framework and the PostgreSQL DBMS
and a platform designed for developing, deploying, and running applications in containers-Docker, which
destined
for collecting, storing, and analyzing meteorological data. The system includes the following components:

* Flask: the main part of the system that provides an HTTP interface for interacting with meteorological information.
Flask processes requests from clients and returns the corresponding data.

* PostgreSQL: A relational database used to store all meteorological data, as well as weather information.
users and other entities of the system.

* Docker: Used to containerize the application, making it easier to deploy and scale.

The project structure includes various files and directories, such as application Flask files, data models, and scripts
for generating test data, as well as Docker configuration files and dependencies in the file requirements.txt.

The goal of the system is to provide a convenient and reliable way to collect, store, and access your data.
meteorological information for further analysis and use.

## Starting the system

Before starting the system, make sure that Docker and Docker Compose are installed on your computer. If they are not installed,
follow the instructions on the [official Docker site] (https://www.docker.com/) for your operating system.

Please also note that you will need an internet connection to run it. An image will be downloaded for the app to work
PostgreSQL DBMS and required dependencies (libraries).

For the application to work, you need to set the encryption key. To do this, you need to create a ".env " file with a specific password.
the "secure_key" variable. This is not a mandatory condition because if the environment variable is missing, the system will
generates the key randomly. Example of a [. env] (. env) file.

![img.png](images/img3.png)

To start the system, open the terminal inWeatherServicethe [WeatherService] folderWeatherServiceand run one of the following commands: 
`docker compose up` или `docker-compose up` 
The system will start up. Note that even if Docker tells you that containers are running, to run the program,
additional time may be required inside containers, up to 20 seconds.

After starting the system, API methods will be available at the address localhost: 5000 (provided that the configuration was not configured).
changed), and the database
data at the localhost:5432 address (provided that the configuration has not been changed).

Please note that the system uses ports 5432 and 5000 for operation. If these ports are busy during startup
with other programs, an exception will be thrown. To change the ports where the API service and database can be accessed
change the first part of the "ports" parameter in the [docker-compose.yml] file(WeatherService%2Fdocker-compose.yml) in the database
data and applications.

### For the database:

![img.png](images/img.png)

### For the API:

![img_1.png](images/img_1.png)

### Filling in test data

For the convenience of testing, when the container is first launched, the database is filled with test data. A new one is being created
user for quick authorization.

Authorization data for the test user:

```json
{
"email": "test@user.ru",
"password": "test_password"
}
```

You can disable automatic database filling by removing the `&& python3 ' command. init_test_data.py` from
файла [docker-compose.yml](WeatherService%2Fdocker-compose.yml).

![img.png](images/img4.png)

### Ready-made Postman tests

To automate testing, you can use a prepared collection of queries
Postman v2.1: [ItPlanet.postman_collection.json](postman_collection%2FItPlanet.postman_collection.json).
Queries are written for test data that is added to the database automatically when the container is first launched.

# Methods

## Creating a user

Method: **POST**

Path: **/registration**

#### Request

Accepts a JSON object with the following fields:

- **firstName** (required): The user's name.
- **lastName** (required): The user's last name.
- **email** (required): The user's email address.
- **password** (required): Password for the user's account.

#### Answer

If the user is successfully created, it returns a JSON object with the following fields:

- **id**: ID of the user's account.
- **firstName**: The user's name.
- **lastName**: Last name of the user.
- **email**: Email address.

#### Statuses

- **201**: The request was completed successfully.
- **400**:
- If there are no required fields in the request body.
- If the fields 'firstName`,' lastName`, 'email` or' password` are empty or consist only of spaces.
- If the email address is incorrect.
- **403**: Request from an authorized account.
- **409**: An account with this email address already exists.

Request example:

```json
{
"firstName": "John",
"lastName": "Doe",
"email": "john.doe@example.com",
"password": "password123"
}
```

Sample response:

```json
{
"id": 123,
"firstName": "John",
"lastName": "Doe",
"email": "john.doe@example.com"
}
```

## User authentication

Method: **POST**

Path: **/login**

#### Request

Accepts a JSON object with the following fields:

- **email** (required): The user's email address.
- **password** (required): Password for the user's account.

#### Answer

If authentication is successful, it returns a JSON object with the field:

- **id**: ID of the user's account.

#### Statuses

- **200**: The request was completed successfully.
- **400**: The required `email` or `password ' fields are missing in the request body.
- **401**: Invalid email address or password.

Request example:

```json
{
"email": "john.doe@example.com",
"password": "password123"
}
```

Sample response:

```json
{
"id": 123
}
```

## User Account

Method: **GET**

Path: **/accounts/{AccountId}**

#### Request

Doesn't accept the request body.

#### Answer

Returns a JSON object with the following fields:

- **id**: ID of the user's account.
- **firstName**: The user's name.
- **lastName**: Last name of the user.
- **email**: Email address.

#### Statuses

- **200**: The request was completed successfully.
- **400**: Invalid 'AccountId' ID.
- **401**: Invalid authorization data.
- **404**: An account with the specified 'AccountId' was not found.

Request example:

```http
GET /accounts/123 HTTP/1.1
```

Sample response:

```json
{
"id": 123,
"firstName": "John",
"lastName": "Doe",
"email": "john.doe@example.com"
}
```

## Account Search

Method: **GET**

Path: **/accounts/search**

#### Request

Accepts request parameters:

- **firstName** (optional): Name of the user to be searched for. Can only be used
a case-insensitive part of the name. If this parameter is omitted, it does not participate in filtering.
- **lastName** (optional): Last name of the user to be searched for. Can only be used
part of the last name without taking into account the case. If this parameter is omitted, it does not participate in filtering.
- **email** (optional): The user's email address to be searched for. Can
use only the case-insensitive part of the email address. If the parameter is omitted, it is not included in the
filtering options.
- **from** (optional): The number of elements that must be skipped to form the results page (
by default, 0).
- **size** (optional): The number of elements on the page (10 by default).

#### Answer

Returns an array of JSON objects with the following fields:

- **id**: ID of the user's account.
- **firstName**: The user's name.
- **lastName**: Last name of the user.
- **email**: Email address.

The search results are sorted by the user's account ID from smallest to largest.

#### Statuses

- **200**: The request was completed successfully.
- **400**: Error in the request parameters (`from < 0 ' or `size <= 0`).
- **401**: Invalid authorization data.

Request example:

```http
GET /accounts/search?firstName=John&lastName=Doe&email=john.doe@example.com&from=0&size=10 HTTP/1.1
```

Sample response:

```json
[
{
"id": 123,
"firstName": "John",
"lastName": "Doe",
"email": "john.doe@example.com"
},
{
"id": 456,
"firstName": "John",
"lastName": "Smith",
"email": "john.smith@example.com"
}
]
```

## Changing your account

Method: **PUT**

Path: **/accounts/{AccountId}**

#### Request

Accepts a JSON object with the following fields:

- **firstName** (required): New user name.
- **lastName** (required): New last name of the user.
- **email** (required): The user's new email address.
- **password** (required): Password for the user's account.

#### Answer

Returns a JSON object with the following fields:

- **id**: ID of the user's account.
- **firstName**: New user name.
- **lastName**: The user's new last name.
- **email**: New email address.

#### Statuses

- **200**: The request was completed successfully.
- **400**: There are no required fields (`firstName`, 'lastName`,' email` or ' password`) or they are empty. Incorrect
email format.
- **401**: Invalid authorization data.
- **403**: Updating a wrong account.
- **404**: Account not found.
- **409**: An account with this email address already exists.

Request example:

```http
PUT /accounts/123 HTTP/1.1
Content-Type: application/json

{
"firstName": "John",
"lastName": "Doe",
"email": "john.doe@example.com",
"password": "newpassword123"
}
```

Sample response:

```json
{
"id": 123,
"firstName": "John",
"lastName": "Doe",
"email": "john.doe@example.com"
}
```

## Deleting an account

Method: **DELETE**

Path: **/accounts/{AccountId}**

#### Request

Accepts an empty request body.

#### Answer

Returns an empty response body.

#### Statuses

- **200**: The request was completed successfully.
- **400**: Invalid account ID ('AccountId' is equal to 'null' or less than or equal to 0).
- **401**: Invalid authorization data.
- **403**: Deleting a wrong account.
- **404**: An account with the specified 'AccountId' was not found.

Request example:

```http
DELETE /accounts/123 HTTP/1.1
```

Sample response:

```http
HTTP/1.1 200 OK
Content-Length: 0
```

## Getting information about the region

Method: **GET**

Path: **/region/{RegionID}**

#### Request

Accepts an empty request body.

#### Answer

Returns information about the region in JSON format:

- **id**: ID of the region.
- **RegionType**: ID of the region type.
- **accountld**: ID of the account that entered data about the region.
- **name**: Name of the region.
- **parentRegion**: Name of the parent region.
- **latitude**: Latitude coordinates.
- **longitude**: Longitude coordinates.

#### Statuses

- **200**: The request was completed successfully.
- **400**: Invalid region ID (`RegionID 'is equal to 'null' or less than or equal to 0).
- **401**: Invalid authorization data.
- **404**: The region with the specified 'RegionID' was not found.

Request example:

```http
GET /region/123 HTTP/1.1
```

Sample response:

```json
{
"id": 123,
"regionType": 456,
"accountld": 789,
"name": "Name of the region",
"parentRegion": "Name of the parent region",
"latitude": 55.123456,
"longitude": 37.654321
}
```

## Creating a region

Method: **POST**

Path: **/region**

#### Request

Accepts a JSON object with the following fields:

- **name** (required): Name of the region.
- **latitude** (required): Latitude coordinates.
- **longitude** (required): Longitude coordinates.
- **RegionType** (optional): ID of the region type.
- **parentRegion** (optional): Name of the parent region.

#### Answer

Returns information about the created region in JSON format:

- **id**: ID of the created region.
- **name**: Name of the region.
- **parentRegion**: Name of the parent region (if specified).
- **RegionType**: ID of the region type (if specified).
- **latitude**: Latitude coordinates.
- **longitude**: Longitude coordinates.

#### Statuses

- **201**: The request was completed successfully and the region was created.
- **400**: Missing required fields in the request body (`name', ' latitude`, `longitude`).
- **401**: Invalid authorization data.
- **404**: Region type or parent region not found.
- **409**: The region with the specified coordinates already exists.

Request example:

```http
POST /region HTTP/1.1
Content-Type: application/json

{
"name": "Name of the region",
"latitude": 55.123456,
"longitude": 37.654321
}
```

Sample response:

```json
{
"id": 123,
"name": "Name of the region",
"parentRegion": "Name of the parent region",
"regionType": 456,
"latitude": 55.123456,
"longitude": 37.654321
}
```

## Changing the region

Method: **PUT**

Path: **/region/{regionld}**

#### Request

Accepts a JSON object with the following fields:

- **name** (required): New name of the region.
- **latitude** (required): New latitude coordinates.
- **longitude** (required): New longitude coordinates.
- **RegionType** (optional): New ID of the region type.
- **parentRegion** (optional): New name of the parent region.

#### Answer

Returns information about the changed region in JSON format:

- **id**: ID of the changed region.
- **name**: New name of the region.
- **parentRegion**: New name of the parent region (if specified).
- **latitude**: New latitude coordinates.
- **longitude**: New longitude coordinates.

#### Statuses

- **200**: The request was completed successfully and the region was changed.
- **400**: Missing required fields in the request body (`name', ' latitude`, `longitude`).
- **401**: Invalid authorization data.
- **404**: The region with the specified ID was not found.
- **409**: The region with the specified coordinates already exists.

Request example:

```http
PUT /region/{123} HTTP/1.1
Content-Type: application/json

{
"name": "New name of the region",
"latitude": 55.123456,
"longitude": 37.654321
}
```

Sample response:

```json
{
"id": 123,
"name": "New name of the region",
"parentRegion": "New name of the parent region".
"latitude": 55.123456,
"longitude": 37.654321
}
```

## Deleting a region

Method: **DELETE**

Path: **/region/{regionld}**

#### Request

Doesn't accept the request body.

#### Answer

Doesn't return the response body.

#### Statuses

- **200**: The request was completed successfully and the region was deleted.
- **400**: A region is the parent of another region.
- **401**: Invalid authorization data.
- **404**: The region with the specified ID was not found.

Request example:

```http
DELETE /region/{123} HTTP/1.1
Authorization: Bearer {token}
```

Sample response:

```json
{}
```

## Getting information about the region type

Method: **GET**

Path: **/region/types/{typeId}**

#### Request

Accepts a request without a body.

#### Answer

Returns information about the region type in JSON format:

- **id**: ID of the region type.
- **type**: The type of region.

#### Statuses

- **200**: The request was completed successfully and information about the region type was received.
- **400**: If the region type is not specified ('typeId = null, typeId <= 0`).
- **401**: Invalid authorization data.
- **404**: The region type with the specified ID was not found.

Request example:

```http
GET /region/types/{123} HTTP/1.1
```

Sample response:

```json
{
"id": 123,
"type": "Name of the region type"
}
```

## Adding a region type

Method: **POST**

Path: **/region/types**

#### Request

Accepts a JSON object with the field:

- **type** (required): The type of region.

#### Answer

Returns information about the added region type in JSON format:

- **id**: ID of the added region type.
- **type**: The type of region.

* If the region type is not specified, `None 'is returned in the `type' field.

#### Statuses

- **201**: The request was completed successfully and the region type was added.
- **400**: The "type" field in the request body is missing or empty.
- **401**: Invalid authorization data.
- **409**: The region type with the specified name already exists.

Request example:

```http
POST /region/types HTTP/1.1
Content-Type: application/json

{
"type": "Name of the region type"
}
```

Sample response:

```json
{
"id": 123,
"type": "Name of the region type"
}
```

## Changing the region type

Method: **PUT**

Path: **/region/types/{typeId}**

#### Request

Accepts a JSON object with the field:

- **type** (required): New region type.

#### Answer

Returns information about the changed region type in JSON format:

- **id**: ID of the changed region type.
- **type**: New region type.

#### Statuses

- **200**: The request was completed successfully and the region type was changed.
- **400**: The region type ID is invalid ('typeId <= 0`) or the "type" field is missing in the request body.
- **401**: Invalid authorization data.
- **404**: The region type with the specified ID was not found.
- **409**: The region type with the specified name already exists.

Request example:

```http
PUT /region/types/{123} HTTP/1.1
Content-Type: application/json

{
"type": "New region type"
}
```

Sample response:

```json
{
"id": 123,
"type": "New region type"
}
```

## Deleting a Region type

Method: **DELETE**

Path: **/region/types/{typeId}**

#### Request

Sends an empty request body.

#### Answer

Sends an empty response body.

#### Statuses

- **200**: The request was completed successfully and the region type was deleted.
- **400**: The region type ID is incorrect ('typeId <= 0`), or there are regions with this type.
- **401**: Invalid authorization data.
- **404**: The region type with the specified ID was not found.

Request example:

```http
DELETE /region/types/{123} HTTP/1.1
```

Sample response:

```json
{}
```

## Getting weather information in the region

Method: **GET**

Path: **/region/weather/{regionld}**

#### Request

Sends an empty request body.

#### Answer

Returns weather information in the specified region in JSON format:

- **id**: ID of the region.
- **RegionName**: Name of the region.
- **temperature**: Temperature in the region, °C.
- **humidity**: Air humidity in the region,%.
- **windSpeed**: Wind speed, m/s.
- **weatherCondition**: Current weather condition. Possible values: "CLEAR", "CLOUDY", "RAIN", "SNOW"," FOG","STORM".
- **precipitationAmount**: Amount of precipitation, mm.
- **measurementDateTime**: Date and time of measuring weather conditions in ISO-8601 format.
- **weatherForecast**: An array of object IDs with a weather forecast for the next few days.

#### Statuses

- **200**: The request was completed successfully and weather information about the region was received.
- **400**: The region ID is invalid (`regionld <= 0`).
- **401**: Invalid authorization data.
- **404**: The region with the specified ID was not found, or the weather forecast for this region was not found.

Request example:

```http
GET /region/weather/{123} HTTP/1.1
```

Sample response:

```json
{
"id": 123,
"RegionName": "Name of the region",
"temperature": 20.5,
"humidity": 70.0,
"windSpeed": 3.5,
"weatherCondition": "CLOUDY",
"precipitationAmount": 0.0,
"measurementDateTime": "2024-04-14T12:30:00Z",
"weatherForecast": [
456,
789
]
}
```

## Search for weather information in the region

Method: **GET**

Path: *
*
/region/weather/search?startDateTime={startDateTime}&endDateTime={endDateTime}&regionId={regionId}&weatherCondition={weatherCondition}&from=0&size=10
**

#### Request

Sends an empty request body.

#### Request Parameters

- **StartDateTime**: Date and time of the start of the period for searching for weather conditions, in ISO-8601 format. If null, don't
participates in filtering.
- **EndDateTime**: Date and time of the end of the period for searching for weather conditions, in ISO-8601 format. If null, does not participate in
filtering options.
- **RegionID**: Id of the region for which weather information is being searched. If null, it doesn't participate in filtering.
- **weatherCondition**: The current weather condition. Possible values: "CLEAR", "CLOUDY", "RAIN", "SNOW"," FOG","STORM". If
null, does not participate in filtering.
- **from**: The number of elements that must be skipped to form the results page (by default
0).
- **size**: The number of elements on the page (10 by default).

#### Answer

Returns weather information in the specified parameters in JSON format:

- **id**: ID of the region.
- **RegionName**: Name of the region.
- **temperature**: Temperature in the region, °C.
- **humidity**: Air humidity in the region,%.
- **windSpeed**: Wind speed, m/s.
- **weatherCondition**: Current weather condition. Possible values: "CLEAR", "CLOUDY", "RAIN", "SNOW"," FOG","STORM".
- **precipitationAmount**: Amount of precipitation, mm.
- **measurementDateTime**: Date and time of measuring weather conditions in ISO-8601 format.
- **weatherForecast**: An array of object IDs with a weather forecast for the next few days.

#### Statuses

- **200**: The request was completed successfully and weather information about the region was received.
- **400**: Invalid request parameters (for example, RegionID <= 0).
- **401**: Invalid authorization data.
- **404**: The region with the specified ID was not found, or the weather forecast for this region was not found.

Request example:

```http
GET /region/weather/search?startDateTime=2024-04-14T00:00:00Z&endDateTime=2024-04-15T00:00:00Z&regionId=123&weatherCondition=CLOUDY&from=0&size=10 HTTP/1.1
```

Sample response:

```json
[
{
"id": 123,
"RegionName": "Name of the region",
"temperature": 20.5,
"humidity": 70.0,
"windSpeed": 3.5,
"weatherCondition": "CLOUDY",
"precipitationAmount": 0.0,
"measurementDateTime": "2024-04-14T12:30:00Z",
"weatherForecast": [
456,
789
]
},
{
"id": 456,
"RegionName": "Other region",
"temperature": 22.0,
"humidity": 75.0,
"windSpeed": 2.0,
"weatherCondition": "CLOUDY",
"precipitationAmount": 0.0,
"measurementDateTime": "2024-04-14T12:30:00Z",
"weatherForecast": [
789,
1011
]
}
]
```

## Adding a regional weather record

Method: **POST**

Path: **/region/weather**

#### Request

Accepts a JSON object with the following fields:

- RegionID (required): ID of the region
- temperature (required) : Temperature in the region, °C
- humidity( required): Air humidity in the region, %
- windSpeed (required): Wind speed, m / s
- weatherCondition (required): Current weather condition: "CLEAR", "CLOUDY", "RAIN", "SNOW", "FOG", "STORM"
- precipitationAmount (required): Amount of precipitation, mm
- measurementDateTime (required) : Date and time of measuring weather conditions in ISO-8601 format
- weatherForecast (optional): An array of object IDs with a weather forecast for the next few days

#### Answer

- **id**: Unique ID of the created weather record in the region
- **temperature**: Temperature in the region, °C
- **humidity**: Air humidity in the region, %
- **windSpeed**: Wind speed, m / s
- **weatherCondition**: Current weather status: "CLEAR", "CLOUDY", "RAIN", "SNOW", "FOG", "STORM"
- **precipitationAmount**: Precipitation, mm
- **measurementDateTime**: Date and time of measuring weather conditions in ISO-8601 format
- **weatherForecast**: An array of object IDs with a weather forecast for the next few days

#### Statuses

- **200**: The request was completed successfully and the weather record for the region was added.
- **400**: One of the following cases:
- Invalid region ID (RegionID <= 0).
- Date and time of weather conditions measurement not in ISO-8601 format.
- The temperature or wind speed is negative.
- Incorrect weather condition.
- The amount of precipitation is negative.
- **401**: Invalid authorization data.
- **404**: The region with the specified ID was not found, or the weather forecast for this region was not found.

Request example:

```http
POST /region/weather HTTP/1.1
Content-Type: application/json

{
"regionId": 123,
"temperature": 25.5,
"humidity": 60.0,
"windSpeed": 3.0,
"weatherCondition": "CLEAR",
"precipitationAmount": 0.0,
"measurementDateTime": "2024-04-14T12:00:00Z",
"weatherForecast": [456, 789]
}
```

Sample response:

```json
{
"id": 987,
"temperature": 25.5,
"humidity": 60.0,
"windSpeed": 3.0,
"weatherCondition": "CLEAR",
"precipitationAmount": 0.0,
"measurementDateTime": "2024-04-14T12:00:00Z",
"weatherForecast": [
456,
789
]
}
```

## Weather changes in the region

Method: **PUT**

Path: **/region/weather/{RegionID}**

#### Request

Accepts a JSON object with the following fields:

- **RegionID** (required): Region ID
- **temperature** (required) : Temperature in the region, °C
- **humidity** (required): Air humidity in the region, %
- **windSpeed** (required): Wind speed, m / s
- **weatherCondition** (required): Current weather condition: "CLEAR", "CLOUDY", "RAIN", "SNOW", "FOG", "STORM"
- **precipitationAmount** (required): Amount of precipitation, mm
- **measurementDateTime** (required): Date and time of measuring weather conditions in ISO-8601 format
- **weatherForecast** (optional): An array of object IDs with a weather forecast for the next few days

#### Answer

Sends a JSON object with the following fields:

- **id**: Unique ID of the created weather record in the region
- **temperature**: Temperature in the region, °C
- **humidity**: Air humidity in the region, %
- **windSpeed**: Wind speed, m / s
- **weatherCondition**: Current weather status: "CLEAR", "CLOUDY", "RAIN", "SNOW", "FOG", "STORM"
- **precipitationAmount**: Precipitation, mm
- **measurementDateTime**: Date and time of measuring weather conditions in ISO-8601 format
- **weatherForecast**: An array of object IDs with a weather forecast for the next few days

#### Request example

```json
{
"regionId": 123,
"temperature": 25.5,
"humidity": 60.2,
"windSpeed": 3.4,
"weatherCondition": "CLEAR",
"precipitationAmount": 0,
"measurementDateTime": "2024-04-15T08:00:00Z",
"weatherForecast": [
456,
789
]
}
```

Sample response:

```json
{
"id": 987,
"temperature": 25.5,
"humidity": 60.2,
"windSpeed": 3.4,
"weatherCondition": "CLEAR",
"precipitationAmount": 0,
"measurementDateTime": "2024-04-15T08:00:00Z",
"weatherForecast": [
456,
789
]
}
```

## Deleting weather for a region

Method: **DELETE**

Path: **/region/weather/{RegionID}**

#### Request

Sends an empty request body.

#### Answer

Sends an empty response body.

#### Statuses

- **200**: The request was completed successfully and the weather for the specified region was deleted.
- **400**: One of the following cases:
- The region ID is invalid (`RegionID <= 0').
- **401**: Invalid authorization data.
- **404**: The region with the specified ID was not found.

Request example:

```http
DELETE /region/weather/{123} HTTP/1.1
```

Sample response:

```json
{}
```

## Adding weather for a specific region

Method: **POST**

Path: **/region/{RegionID}/weather/{weatherId}**

#### Request

Sends an empty request body.

#### Answer

Sends a JSON object with the following fields:

- id (long): Confirming a unique region ID
- RegionID (long): ID of the region
- regionName (string): New name of the region
- temperature (float): New temperature in the region, °C
- humidity (float): New air humidity in the region, %
- windSpeed (float): Per Wind speed, m / s
- weatherCondition (string): Current weather condition, available values: "CLEAR", "CLOUDY", "RAIN", "SNOW", "FOG","
STORM"
- precipitationAmount (float): Amount of precipitation, mm
- measurementDateTime (dateTime): Date and time of measuring weather conditions in ISO-8601 format
- weatherForecast (array): An array of object IDs with a weather forecast for the next few days

#### Statuses

- **200**: The request was completed successfully.
- **400**: One of the following cases:
- The region ID is invalid (`RegionID <= 0').
- The weather ID is incorrect (`weatherId <= 0`).
- **401**: Invalid authorization data.
- **404**: The region with the specified ID was not found, or the weather for the specified region and ID was not found.

Request example:

```http
POST /region/123/weather/456 HTTP/1.1
```

Sample response:

```json
{
"id": 123,
"regionId": 123,
"RegionName": "Name of the region",
"temperature": 25.0,
"humidity": 50.0,
"windSpeed": 10.0,
"weatherCondition": "CLEAR",
"precipitationAmount": 0.0,
"measurementDateTime": "2024-04-16T12:00:00Z",
"weatherForecast": [
789,
790
]
}
```

## Deleting weather for a region

Method: **DELETE**

Path: **/region/{RegionID}/weather/{weatherId}**

#### Request

Sends an empty request body.

#### Answer

Sends a JSON object with the following fields:

- id (long): ID of the region
- name (string): Name of the region
- parentRegion (string): Name of the parent region
- latitude( double): Latitude coordinates
- longitude( double): Longitude coordinates

#### Statuses

- **200**: The request was completed successfully.
- **400**: One of the following cases:
- The region ID is invalid (`RegionID <= 0').
- The weather ID is incorrect (`weatherId <= 0`).
- **401**: Invalid authorization data.
- **404**: The region with the specified ID was not found.

Request example:

```http
DELETE /region/123/weather/456 HTTP/1.1
```

Sample response:

```json
{
"id": 123,
"name": "Name of the region",
"parentRegion": "Name of the parent region",
"latitude": 50.0,
"longitude": 30.0
}
```

## Getting information about the weather forecast

Method: **GET**

Путь: **/region/weather/forecast/{forecastId}**

#### Request

Sends an empty request body.

#### Answer

Sends a JSON object with the following fields:

- id (long): Unique identifier of the weather forecast
- dateTime (dateTime): Date and time of the forecast in ISO-8601 format
- temperature (float): Predicted temperature, °C
- weatherCondition (string): Current weather condition. Acceptable values: "CLEAR", "CLOUDY", "RAIN", "SNOW", "FOG","
STORM"
- RegionID( long): ID of the region for which the forecast was made

#### Statuses

- **200**: The request was completed successfully.
- **400**: One of the following cases:
- The weather forecast ID is not specified (`forecastId = null').
- The forecast date and time are not in ISO-8601 format.
- The weather condition is not valid.
- The weather forecast ID is less than or equal to zero ('forecastId <= 0`).
- **401**: Invalid authorization data.
- **404**: There is no weather forecast with the specified ID.

Request example:

```http
GET /region/weather/forecast/{forecastId} HTTP/1.1
```

Sample response:

```json
{
"id": 123,
"dateTime": "2024-04-15T12:00:00Z",
"temperature": 20.5,
"weatherCondition": "CLEAR",
"regionId": 456
}
```

## Changing the weather forecast

Method: **PUT**

Путь: **/region/weather/forecast/{forecastId}**

#### Request

Sends a JSON object with the following fields:

- temperature (float): New predicted temperature, °C
- weatherCondition (string): New forecast weather condition. Acceptable values: "CLEAR", "CLOUDY", "RAIN","
SNOW", "FOG", "STORM"
- dateTime (dateTime): New forecast date and time in ISO-8601 format

#### Answer

Sends a JSON object with the following fields:

- id (long): Confirmation of the unique weather forecast ID
- dateTime (dateTime): New forecast date and time in ISO-8601 format
- temperature (float): New temperature, °C
- weatherCondition (string): New weather condition
- RegionID (long): ID of the region

#### Statuses

- **200**: The request was completed successfully.
- **400**: One of the following cases:
- The weather forecast ID is not specified (`forecastId = null').
- The forecast date and time are not in ISO-8601 format.
- The weather condition is not valid.
- The weather forecast ID is less than or equal to zero ('forecastId <= 0`).
- **401**: Invalid authorization data.
- **404**: There is no weather forecast with the specified ID.

Request example:

```http
PUT /region/weather/forecast/{forecastId} HTTP/1.1
Content-Type: application/json

{
"temperature": 25.5,
"weatherCondition": "CLEAR",
"dateTime": "2024-04-16T12:00:00Z"
}
```

Sample response:

```json
{
"id": 123,
"dateTime": "2024-04-16T12:00:00Z",
"temperature": 25.5,
"weatherCondition": "CLEAR",
"regionId": 456
}
```

## Adding a weather forecast

Method: **POST**

Path: **/region/weather/forecast/**

#### Request

Sends a JSON object with the following fields:

- RegionID( long): ID of the region that the forecast is being made for
- dateTime (dateTime): Date and time for which the forecast is made in ISO-8601 format
- temperature (float): Predicted temperature, °C
- weatherCondition (string): Predicted weather condition. Acceptable values: "CLEAR", "CLOUDY", "RAIN", "SNOW","
FOG", "STORM"

#### Answer

Sends a JSON object with the following fields:

- id (long): Unique ID of the created weather forecast
- RegionID( long): ID of the region for which the forecast was created
- temperature (float): Predicted temperature, °C
- weatherCondition (string): Predicted weather condition
- dateTime (dateTime): Date and time of the forecast in ISO-8601 format
- precipitationAmount (float): Amount of precipitation, mm
- windSpeed (float): Wind speed, m / s

#### Statuses

- **200**: The request was completed successfully.
- **400**: One of the following cases:
- The region ID is not specified (`RegionID = null').
- The forecast date and time are not in ISO-8601 format.
- The weather condition is not valid.
- The region ID is less than or equal to zero (`RegionID <= 0`).
- **401**: Invalid authorization data.
- **404**: The region with the specified ID does not exist.

Request example:

```http
POST /region/weather/forecast/ HTTP/1.1
Content-Type: application/json

{
"regionId": 123,
"dateTime": "2024-04-16T12:00:00Z",
"temperature": 25.5,
"weatherCondition": "CLEAR"
}
```

Sample response:

```json
{
"id": 456,
"regionId": 123,
"temperature": 25.5,
"weatherCondition": "CLEAR",
"dateTime": "2024-04-16T12:00:00Z",
"precipitationAmount": 10.2,
"windSpeed": 3.4
}
```

## Deleting the weather forecast

Method: **DELETE**

Путь: **/region/weather/forecast/{forecastId}**

#### Request

Sends an empty request body.

#### Answer

Sends an empty response body.

#### Statuses

- **200**: The request was completed successfully and the weather forecast was deleted.
- **400**: One of the following cases:
- The weather forecast ID is incorrect ('forecastId <= 0`).
- **401**: Invalid authorization data.
- **404**: The weather forecast with the specified ID was not found.

Request example:

```http
DELETE /region/weather/forecast/123 HTTP/1.1
```

Sample response:

```http
HTTP/1.1 200 OK
```

## License
MIT. See file [LICENSE](LICENSE).