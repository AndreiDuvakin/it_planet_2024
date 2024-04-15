import os
import random
import re
from datetime import datetime
from dateutil import parser

from dotenv import load_dotenv
from flask import Flask, request, jsonify, session as cookie_session
from flask_login import LoginManager
from sqlalchemy import desc, or_, and_
from string import ascii_lowercase, digits
from waitress import serve

from data.forecast import Forecast
from data.region import Region
from data.region_type import RegionType
from data.weather import Weather
from data.weather_forecast import WeatherForecast
from functions.check_TWP import check_temperature_wind_speed_precipitation_amount
from check_auth import user_is_auth
from functions.check_conditions import is_current_conditions
from functions.check_id import is_current_id
from data.connect import init_db, connect
from data.account import Account

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('secure_key',
                                          ''.join([random.choice(ascii_lowercase + digits) for _ in range(10)]))
app.config['SESSION_COOKIE_SECURE'] = True
login_manager = LoginManager()
login_manager.init_app(app)


@app.route('/registration', methods=['POST'])
def register_user():
    data = request.json

    if not all(key in data for key in ['firstName', 'lastName', 'email', 'password']):
        return jsonify({'error': 'Отсутствующие поля в теле запроса'}), 400

    if any(not data[field].strip() for field in ['firstName', 'lastName', 'email', 'password']):
        return jsonify({'error': 'Пустые поля или пробелы в тексте запроса'}), 400

    if not re.match(r'^[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}$', data['email']):
        return jsonify({'error': 'Неверный формат email'}), 400

    with connect() as session:
        if session.query(Account).filter(Account.email == data['email']).first() is not None:
            return jsonify({'error': 'Учетная запись с этим адресом электронной почты уже существует'}), 409

        new_user = Account(
            firstName=data['firstName'],
            lastName=data['lastName'],
            email=data['email']
        )
        new_user.set_password(data['password'])

        session.add(new_user)
        session.commit()

        return jsonify({
            'id': new_user.id,
            'firstName': new_user.first_name,
            'lastName': new_user.last_name,
            'email': new_user.email
        }), 201


@app.route('/login', methods=['POST'])
def login():
    with connect() as session:
        if user_is_auth(cookie_session, session):
            return jsonify({'id': cookie_session['id']}), 200

    data = request.json

    if 'email' not in data or 'password' not in data:
        return jsonify({'error': 'Отсутствуют обязательные поля email и password'}), 400

    if not re.match(r'^[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}$', data['email']):
        return jsonify({'error': 'Неверный формат email'}), 400

    email = data['email']
    password = data['password']

    with connect() as session:
        user = session.query(Account).filter(Account.email == email).first()

        if user is None or not user.check_password(password):
            return jsonify({'error': 'Неверный email или пароль'}), 401

        cookie_session['id'] = user.id

        return jsonify({'id': user.id}), 200


@app.route('/accounts/<int:account_id>', methods=['GET', 'PUT', 'DELETE'])
def account(account_id):
    with connect() as session:
        if not user_is_auth(cookie_session, session):
            return jsonify({'error': 'Неверные авторизационные данные'}), 401

    if not is_current_id(account_id):
        return jsonify({'error': 'Некорректный идентификатор региона'}), 400

    with connect() as session:
        if not session.query(Account).filter(Account.id == cookie_session['id']).first():
            return jsonify({'error': 'Неверные авторизационные данные'}), 401

    if request.method == 'GET':

        with connect() as session:
            user = session.query(Account).get(account_id)

            if user is None:
                return jsonify({'error': 'Аккаунт не найден'}), 404

            return jsonify({
                'id': user.id,
                'firstName': user.firstName,
                'lastName': user.lastName,
                'email': user.email
            }), 200
    elif request.method == 'PUT':
        user_id = cookie_session['id']

        if user_id != account_id:
            return jsonify({'error': 'Обновление не своего аккаунта'}), 403

        data = request.json

        required_fields = ['firstName', 'lastName', 'email', 'password']
        for field in required_fields:
            if field not in data or not data[field].strip():
                return jsonify({'error': 'Отсутствуют обязательные поля или они пусты'}), 400

        if not re.match(r'^[\w\.-]+@[\w\.-]+$', data['email']):
            return jsonify({'error': 'Неверный формат email'}), 400

        with connect() as session:
            user = session.query(Account).get(account_id)

            if user is None:
                return jsonify({'error': 'Аккаунт не найден'}), 404

            if not user.check_password(data['password']):
                return jsonify({'error': 'Неверный пароль изменяемого аккаунта'}), 403

            if session.query(Account).filter(Account.email == data['email'],
                                             Account.id != account_id).first() is not None:
                return jsonify({'error': 'Аккаунт с таким email уже существует'}), 409

            user.firstName = data['firstName']
            user.lastName = data['lastName']
            user.email = data['email']

            session.commit()

            return jsonify({
                'id': user.id,
                'firstName': user.firstName,
                'lastName': user.lastName,
                'email': user.email
            }), 200
    elif request.method == 'DELETE':
        user_id = cookie_session['id']

        if user_id != account_id:
            return jsonify({'error': 'Удаление не своего аккаунта'}), 403

        with connect() as session:
            user = session.query(Account).get(account_id)

            if user is None:
                return jsonify({'error': 'Аккаунт не найден'}), 404

            session.delete(user)
            session.commit()

            return jsonify({}), 200


@app.route('/accounts/search', methods=['GET'])
def search_accounts():
    with connect() as session:
        if not user_is_auth(cookie_session, session):
            return jsonify({'error': 'Неверные авторизационные данные'}), 401

    first_name = request.args.get('firstName', None)
    last_name = request.args.get('lastName', None)
    email = request.args.get('email', None)
    from_index = request.args.get('from', 0)
    size = request.args.get('size', 10)

    if size:
        try:
            if int(size) <= 0:
                return jsonify({'error': 'Неверный формат количества элементов на странице'}), 400
            size = int(size)
        except ValueError:
            return jsonify({'error': 'Неверный формат количества элементов на странице'}), 400

    if from_index:
        try:
            if int(from_index) < 0:
                return jsonify({'error': 'Неверный формат количества элементов, которые нужно пропустить'}), 400
            from_index = int(from_index)
        except ValueError:
            return jsonify({'error': 'Неверный формат количества элементов, которые нужно пропустить'}), 400

    with connect() as session:
        query = session.query(Account)
        if first_name:
            query = query.filter(Account.first_name.ilike(f'%{first_name}%'))
        if last_name:
            query = query.filter(Account.last_name.ilike(f'%{last_name}%'))
        if email:
            query = query.filter(Account.email.ilike(f'%{email}%'))

        users = query.offset(from_index).limit(size).all()
        users.sort(key=lambda user: user.id)

        if not users:
            return jsonify({'error': 'Нет результатов поиска'}), 404

        result = [{'id': user.id, 'firstName': user.first_name, 'lastName': user.last_name, 'email': user.email}
                  for user in users]

        return jsonify(result), 200


@app.route('/region/<int:region_id>', methods=['GET', 'PUT', 'DELETE'])
def region_method(region_id):
    with connect() as session:
        if not user_is_auth(cookie_session, session):
            return jsonify({'error': 'Неверные авторизационные данные'}), 401

    if not is_current_id(region_id):
        return jsonify({'error': 'Некорректный идентификатор региона'}), 400

    with connect() as session:
        if session.query(Region).filter(Region.id == region_id).first() is None:
            return jsonify({'error': 'Регион с таким идентификатором не найден'}), 404

    if request.method == 'GET':
        with connect() as session:
            region = session.query(Region).filter(Region.id == region_id).first()

            response = {
                'id': region.id,
                'regionType': region.type_id,
                'accountld': region.account_id,
                'name': region.name,
                'parentRegion': region.parent_region,
                'latitude': region.latitude,
                'longitude': region.longitude
            }

            return jsonify(response), 200
    elif request.method == 'PUT':
        data = request.json

        if not data or 'name' not in data or 'latitude' not in data or 'longitude' not in data:
            return jsonify({'error': 'Отсутствуют обязательные поля в теле запроса'}), 400

        with connect() as session:
            region = session.query(Region).filter(Region.id == region_id).first()

            if region.account_id != cookie_session['id']:
                return jsonify({'error': 'Недостаточно прав для изменения этого региона'}), 403

            try:
                float(data['latitude'])
                float(data['longitude'])
            except ValueError:
                return jsonify({'error': 'Неверные значения кординат'}), 400

            if not data['name']:
                return jsonify({'error': 'Обязательные поля не могут быть пустыми'}), 400

            existing_region = session.query(Region).filter(Region.latitude == data['latitude'],
                                                           Region.longitude == data['longitude'],
                                                           Region.id != region_id).first()

            if existing_region and existing_region.id != region_id:
                return jsonify({'error': 'Регион с такими координатами уже существует'}), 409

            region_type_id = None

            if 'regionType' in data:
                try:
                    region_type_id = int(data['regionType'])
                    if not session.query(RegionType).filter(RegionType.id == region_type_id).first():
                        return jsonify({'error': 'Тип региона не найден'}), 404
                except ValueError:
                    return jsonify({'error': 'Неверный тип региона'}), 400

            region.name = data['name']
            region.type_id = region_type_id if region_type_id is not None else region.type_id
            region.latitude = data['latitude']
            region.longitude = data['longitude']

            parent_region = None

            if 'parentRegion' in data:
                parent_region = session.query(Region).filter(Region.name == data['parentRegion']).first()
                if not parent_region:
                    return jsonify({'error': 'Родительский регион не найден'}), 404
                region.parent_region = parent_region.id

            session.commit()

            response = {
                'id': region.id,
                'name': region.name,
                'parentRegion': None if parent_region is None else parent_region.name,
                'latitude': region.latitude,
                'longitude': region.longitude
            }

            return jsonify(response), 200
    elif request.method == 'DELETE':
        with connect() as session:
            region = session.query(Region).filter(Region.id == region_id).first()

            if region.account_id != cookie_session['id']:
                return jsonify({'error': 'Недостаточно прав для удаления этого региона'}), 403

            child_regions_count = session.query(Region).filter(Region.parent_region == region_id).count()
            if child_regions_count > 0:
                return jsonify({'error': 'Регион является родительским для другого региона'}), 400

            session.delete(region)
            session.commit()

            return jsonify({}), 200


@app.route('/region', methods=['POST'])
def post_region():
    with connect() as session:
        if not user_is_auth(cookie_session, session):
            return jsonify({'error': 'Неверные авторизационные данные'}), 401

    data = request.json

    if not all(field in data for field in ['name', 'latitude', 'longitude']):
        return jsonify({'error': 'Отсутствуют обязательные поля в теле запроса'}), 400

    if not data['name']:
        return jsonify({'error': 'Обязательные поля не могут быть пустыми'}), 400

    try:
        float(data['latitude'])
        float(data['longitude'])
    except ValueError:
        return jsonify({'error': 'Неверные значения кординат'}), 400

    with connect() as session:
        existing_region = session.query(Region).filter_by(latitude=data['latitude'],
                                                          longitude=data['longitude']).first()
        if existing_region is not None:
            return jsonify({'error': 'Регион с такими координатами уже существует'}), 409

        region_type_id = None

        if 'regionType' in data:
            try:
                region_type_id = int(data['regionType'])
                if not session.query(RegionType).filter(RegionType.id == region_type_id).first():
                    return jsonify({'error': 'Тип региона не найден'}), 404
            except ValueError:
                return jsonify({'error': 'Неверный тип региона'}), 400

        new_region = Region(
            name=data['name'],
            latitude=data['latitude'],
            longitude=data['longitude'],
            account_id=cookie_session['id']
        )

        if region_type_id is not None:
            new_region.type_id = region_type_id

        parent_region = None

        if 'parentRegion' in data:
            parent_region = session.query(Region).filter(Region.name == data['parentRegion']).first()
            if not parent_region:
                return jsonify({'error': 'Родительский регион не найден'}), 404
            new_region.parent_region = parent_region.id

        session.add(new_region)
        session.commit()

        response = {
            'id': new_region.id,
            'name': new_region.name,
            'parentRegion': None if parent_region is None else parent_region.name,
            'regionType': new_region.type_id,
            'latitude': new_region.latitude,
            'longitude': new_region.longitude
        }

    return jsonify(response), 201


@app.route('/region/types/<int:type_id>', methods=['GET', 'PUT', 'DELETE'])
def region_type_method(type_id):
    with connect() as session:
        if not user_is_auth(cookie_session, session):
            return jsonify({'error': 'Неверные авторизационные данные'}), 401

    if not is_current_id(type_id):
        return jsonify({'error': 'Некорректный идентификатор региона'}), 400

    with connect() as session:
        if session.query(RegionType).filter(RegionType.id == type_id).first() is None:
            return jsonify({'error': 'Тип региона с таким идентификатором не найден'}), 404

    if request.method == 'GET':
        with connect() as session:
            region_type = session.query(RegionType).filter(RegionType.id == type_id).first()

            response = {
                'id': region_type.id,
                'type': region_type.type
            }

            return jsonify(response), 200
    elif request.method == 'PUT':
        data = request.json

        if 'type' not in data or not data['type'].strip():
            return jsonify({'error': 'Отсутствует новый тип региона или он пуст'}), 400

        with connect() as session:
            existing_type = session.query(RegionType).filter(RegionType.id == type_id).first()

            new_type = session.query(RegionType).filter(RegionType.type == data['type'],
                                                        RegionType.id != type_id).first()
            if new_type is not None:
                return jsonify({'error': 'Тип региона с таким именем уже существует'}), 409

            existing_type.type = data['type']
            session.commit()

            response = {
                'id': existing_type.id,
                'type': existing_type.type
            }
            return jsonify(response), 200
    elif request.method == 'DELETE':
        with connect() as session:
            existing_type = session.query(RegionType).filter(RegionType.id == type_id).first()

            regions_with_type = session.query(Region).filter(Region.type_id == existing_type.type).count()
            if regions_with_type > 0:
                return jsonify({'error': 'Есть регионы с этим типом'}), 400

            session.delete(existing_type)
            session.commit()

            return jsonify({}), 200


@app.route('/region/types', methods=['POST'])
def add_region_type():
    with connect() as session:
        if not user_is_auth(cookie_session, session):
            return jsonify({'error': 'Неверные авторизационные данные'}), 401

    data = request.json

    if 'type' not in data or not data['type'].strip():
        return jsonify({'error': 'Поле "type" отсутствует или пусто'}), 400

    with connect() as session:
        existing_type = session.query(RegionType).filter(RegionType.type == data['type']).first()
        if existing_type:
            return jsonify({'error': 'Тип региона с таким именем уже существует'}), 409

        new_type = RegionType(type=data['type'])
        session.add(new_type)
        session.commit()

        response = {
            'id': new_type.id,
            'type': new_type.type
        }
        return jsonify(response), 201


@app.route('/region/weather/<int:region_id>', methods=['GET', 'PUT', 'DELETE'])
def get_region_weather(region_id):
    with connect() as session:
        if not user_is_auth(cookie_session, session):
            return jsonify({'error': 'Неверные авторизационные данные'}), 401

    with connect() as session:
        region = session.query(Region).filter(Region.id == region_id).first()

        if region is None:
            return jsonify({'error': 'Регион с указанным идентификатором не найден'}), 404

    with connect() as session:
        if not session.query(Account).filter(Account.id == cookie_session['id']).first():
            return jsonify({'error': 'Неверные авторизационные данные'}), 401

    if request.method == 'GET':
        with connect() as session:
            region = session.query(Region).filter(Region.id == region_id).first()

            if region is None:
                return jsonify({'error': 'Регион с указанным идентификатором не найден'}), 404

            weather = session.query(Weather).filter(Weather.region_id == region_id).order_by(desc(Weather.id)).first()

            if weather is None:
                return jsonify({'error': 'Погода для указанного региона не найдена'}), 404

            weather_forecasts = session.query(WeatherForecast).filter(WeatherForecast.weather_id == weather.id).all()
            forecasts = session.query(Forecast).filter(
                or_(
                    and_(
                        Forecast.region_id == region_id,
                        Forecast.date_time > datetime.now()
                    ),
                    Forecast.id.in_(list(map(lambda weather_forecast: weather_forecast.forecast_id, weather_forecasts)))
                )
            ).all()

            if not forecasts:
                return jsonify({'error': 'Прогноз погоды для указанного региона не найдена'}), 404

            weather_response = {
                'id': region.id,
                'regionName': region.name,
                'temperature': weather.temperature,
                'humidity': weather.humidity,
                'windSpeed': weather.wind_speed,
                'weatherCondition': weather.weather_condition,
                'precipitationAmount': weather.precipitation_amount,
                'measurementDateTime': weather.measurement_date_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                'weatherForecast': [forecast.id for forecast in forecasts]
            }

            return jsonify(weather_response), 200
    elif request.method == 'PUT':
        data = request.json
        region_name = data.get('regionName')
        temperature = data.get('temperature')
        humidity = data.get('humidity')
        wind_speed = data.get('windSpeed')
        weather_condition = data.get('weatherCondition')
        precipitation_amount = data.get('precipitationAmount')
        measurement_datetime = data.get('measurementDateTime')
        weather_forecast = data.get('weatherForecast')

        if not region_name:
            return jsonify({'error': 'Некорректное название региона'}), 400

        try:
            measurement_datetime = parser.isoparse(measurement_datetime)
        except ValueError:
            return jsonify({'error': 'Неверный формат даты и времени (measurementDateTime)'}), 400

        if not check_temperature_wind_speed_precipitation_amount(temperature, wind_speed, precipitation_amount):
            return jsonify(
                {
                    'error': 'Значения температуры, скорости ветра или количества осадков не могут быть отрицательными'}), 400

        if not is_current_conditions(weather_condition):
            return jsonify({'error': 'Неверное состояние погоды (weatherCondition)'}), 400

        with connect() as session:

            weather = session.query(Weather).filter(Weather.region_id == region_id,
                                                    Weather.measurement_date_time == measurement_datetime).first()

            if not weather:
                return jsonify({'error': 'Погода для региона и переданной даты не найдена, изменение невозможно'}), 404

            find_weather_forecast = []
            for forecast_id in weather_forecast:
                forecast = session.query(Forecast).filter(Forecast.id == forecast_id).first()
                if not forecast:
                    return jsonify({'error': 'Прогноз погоды с указанным идентификатором не найден'}), 404

                weather_forecasts = session.query(WeatherForecast).filter(
                    WeatherForecast.weather_id == weather.id).all()
                for query_weather_forecast in weather_forecasts:
                    if query_weather_forecast.forecast_id not in weather_forecast:
                        session.delete(query_weather_forecast)
                    else:
                        find_weather_forecast.append(query_weather_forecast.forecast_id)

            for new_forecast_weather_id in [new_weather_forecast for new_weather_forecast in find_weather_forecast if
                                            weather_forecasts not in weather_forecast]:
                new_weather_forecast = WeatherForecast(
                    weather_id=weather.id,
                    forecast_id=new_forecast_weather_id
                )
                session.add(new_weather_forecast)

            region.name = region_name

            weather.temperature = temperature
            weather.humidity = humidity
            weather.wind_speed = wind_speed
            weather.weather_condition = weather_condition
            weather.precipitation_amount = precipitation_amount
            weather.measurement_date_time = measurement_datetime

            session.commit()

            return jsonify({
                'id': region.id,
                'regionName': region.region_name,
                'temperature': weather.temperature,
                'humidity': weather.humidity,
                'windSpeed': weather.wind_speed,
                'weatherCondition': weather.weather_condition,
                'precipitationAmount': weather.precipitation_amount,
                'measurementDateTime': weather.measurement_datetime.strftime('%Y-%m-%dT%H:%M:%SZ'),
                'weatherForecast': weather_forecast
            }), 200
    elif request.method == 'DELETE':
        with connect() as session:
            weather_to_delete = session.query(Weather).filter(Weather.region_id == region_id).all()
            if not weather_to_delete:
                return jsonify({'error': 'Погода для указанного региона не найдена'}), 404

            for weather_entry in weather_to_delete:
                session.delete(weather_entry)
            session.commit()

        return jsonify({}), 200


@app.route('/region/weather/search', methods=['GET'])
def search_region_weather():
    with connect() as session:
        if not user_is_auth(cookie_session, session):
            return jsonify({'error': 'Неверные авторизационные данные'}), 401

    start_datetime = request.args.get('startDateTime', None)
    end_datetime = request.args.get('endDateTime', None)
    region_id = request.args.get('regionId', None)
    weather_condition = request.args.get('weatherCondition', None)
    from_index = request.args.get('from', 0)
    size = request.args.get('size', 10)

    if not is_current_id(region_id):
        return jsonify({'error': 'Некорректный идентификатор региона'}), 400

    if start_datetime:
        try:
            parser.isoparse(start_datetime)
        except ValueError:
            return jsonify({'error': 'Неверный формат даты и времени (startDateTime)'}), 400

    if end_datetime:
        try:
            parser.isoparse(end_datetime)
        except ValueError:
            return jsonify({'error': 'Неверный формат даты и времени (endDateTime)'}), 400

    if size:
        try:
            if int(size) < 1:
                return jsonify({'error': 'Неверный формат количества элементов на странице'}), 400
        except ValueError:
            return jsonify({'error': 'Неверный формат количества элементов на странице'}), 400

    if from_index:
        try:
            if int(from_index) < 1:
                return jsonify({'error': 'Неверный формат количества элементов, которые нужно пропустить'}), 400
        except ValueError:
            return jsonify({'error': 'Неверный формат количества элементов, которые нужно пропустить'}), 400

    if weather_condition:
        if not is_current_conditions(weather_condition):
            return jsonify({'error': 'Неверное состояние погоды (weatherCondition)'}), 400

    with connect() as session:

        query = session.query(Weather)

        if start_datetime:
            query = query.filter(
                Weather.measurement_date_time >= parser.isoparse(start_datetime))

        if end_datetime:
            query = query.filter(
                Weather.measurement_date_time <= parser.isoparse(end_datetime))

        if region_id:
            query = query.filter(Weather.region_id == region_id)

        if weather_condition:
            query = query.filter(Weather.weather_condition == weather_condition)

        query = query.offset(from_index).limit(size)

        weather_records = query.all()

        if not weather_records:
            return jsonify({'error': 'Погода по указанным параметрам не найдена'}), 404

        weather_response = []
        for weather_record in weather_records:
            region = session.query(Region).filter(Region.id == weather_record.region_id).first()
            weather_forecasts = session.query(WeatherForecast).filter(
                WeatherForecast.weather_id == weather_record.id).all()
            forecasts = session.query(Forecast).filter(
                or_(
                    and_(
                        Forecast.region_id == region_id,
                        Forecast.date_time > datetime.now()
                    ),
                    Forecast.id.in_(list(map(lambda weather_forecast: weather_forecast.forecast_id, weather_forecasts)))
                )
            ).all()

            if not forecasts:
                return jsonify({'error': 'Прогноз погоды для указанного региона не найден'}), 404

            weather_response.append({
                'id': region.id,
                'regionName': region.name,
                'temperature': weather_record.temperature,
                'humidity': weather_record.humidity,
                'windSpeed': weather_record.wind_speed,
                'weatherCondition': weather_record.weather_condition,
                'precipitationAmount': weather_record.precipitation_amount,
                'measurementDateTime': weather_record.measurement_date_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                'weatherForecast': [forecast.id for forecast in forecasts]
            })

        return jsonify(weather_response), 200


@app.route('/region/weather', methods=['POST'])
def add_region_weather():
    with connect() as session:
        if not user_is_auth(cookie_session, session):
            return jsonify({'error': 'Неверные авторизационные данные'}), 401

    data = request.json
    region_id = data.get('regionId')
    temperature = data.get('temperature')
    humidity = data.get('humidity')
    wind_speed = data.get('windSpeed')
    weather_condition = data.get('weatherCondition')
    precipitation_amount = data.get('precipitationAmount')
    measurement_datetime = data.get('measurementDateTime')
    weather_forecast = data.get('weatherForecast')

    if not is_current_id(region_id):
        return jsonify({'error': 'Некорректный идентификатор региона'}), 400

    try:
        if not parser.isoparse(measurement_datetime):
            return jsonify({'error': 'Неверный формат даты и времени (measurementDateTime)'}), 400

        if not check_temperature_wind_speed_precipitation_amount(temperature, wind_speed, precipitation_amount):
            return jsonify({'error': 'Значения температуры, скорости ветра или количества осадков не могут быть '
                                     'отрицательными'}), 400

        if not is_current_conditions(weather_condition):
            return jsonify({'error': 'Неверное состояние погоды (weatherCondition)'}), 400

        float(humidity)
    except ValueError:
        return jsonify({'error': 'Некорректный формат данных'}), 400

    with connect() as session:
        region = session.query(Region).filter(Region.id == region_id).first()
        if not region:
            return jsonify({'error': 'Регион с указанным идентификатором не найден'}), 404

        new_weather = Weather(
            region_id=region_id, temperature=temperature, humidity=humidity,
            wind_speed=wind_speed, weather_condition=weather_condition,
            precipitation_amount=precipitation_amount,
            measurement_date_time=parser.isoparse(measurement_datetime),
        )
        session.add(new_weather)
        session.flush()

        for forecast_id in weather_forecast:
            forecast = session.query(Forecast).filter(Forecast.id == forecast_id).first()
            if not forecast:
                return jsonify({'error': 'Прогноз погоды с указанным идентификатором не найден'}), 404
            new_weather_forecast = WeatherForecast(
                weather_id=new_weather.id,
                forecast_id=forecast_id
            )
            session.add(new_weather_forecast)

        session.commit()

        return jsonify({
            'id': new_weather.id,
            'temperature': new_weather.temperature,
            'humidity': new_weather.humidity,
            'windSpeed': new_weather.wind_speed,
            'weatherCondition': new_weather.weather_condition,
            'precipitationAmount': new_weather.precipitation_amount,
            'measurementDateTime': new_weather.measurement_date_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'weatherForecast': weather_forecast
        }), 200


@app.route('/region/<int:region_id>/weather/<int:weather_id>', methods=['DELETE'])
def delete_region_weather(region_id, weather_id):
    with connect() as session:
        if not user_is_auth(cookie_session, session):
            return jsonify({'error': 'Неверные авторизационные данные'}), 401

    if not is_current_id(region_id):
        return jsonify({'error': 'Некорректный идентификатор региона'}), 400

    with connect() as session:
        region = session.query(Region).filter(Region.id == region_id).first()

        if region is None:
            return jsonify({'error': 'Регион с указанным идентификатором не найден'}), 404

    if not is_current_id(weather_id):
        return jsonify({'error': 'Некорректный идентификатор погоды'}), 400

    with connect() as session:
        weather_to_delete = session.query(Weather).filter(Weather.region_id == region_id,
                                                          Weather.id == weather_id).first()
        if not weather_to_delete:
            return jsonify({'error': 'Погода для указанного региона и идентификатора не найдена'}), 404

        session.delete(weather_to_delete)
        session.commit()

    return jsonify({}), 200


@app.route('/region/weather/forecast/<int:forecast_id>', methods=['GET', 'PUT'])
def weather_forecast_method(forecast_id):
    with connect() as session:
        if not user_is_auth(cookie_session, session):
            return jsonify({'error': 'Неверные авторизационные данные'}), 401

    if not is_current_id(forecast_id):
        return jsonify({'error': 'Некорректный идентификатор прогноза погоды'}), 400

    with connect() as session:
        forecast = session.query(Forecast).filter(Forecast.id == forecast_id).first()
        if not forecast:
            return jsonify({'error': 'Прогноза погоды с указанным идентификатором не существует'}), 404

    if request.method == 'GET':
        if not is_current_conditions(forecast.weather_condition):
            return jsonify({'error': 'Неверное состояние погоды'}), 400

        try:
            if not parser.isoparse(forecast.date_time):
                return jsonify({'error': 'Неверный формат даты и времени'}), 400
        except ValueError:
            return jsonify({'error': 'Неверный формат даты и времени'}), 400

        weather_forecast_info = {
            'id': forecast.id,
            'dateTime': forecast.dateTime.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'temperature': forecast.temperature,
            'weatherCondition': forecast.weatherCondition,
            'regionId': forecast.region_id
        }

        return jsonify(weather_forecast_info), 200

    elif request.method == 'PUT':
        data = request.json
        temperature = data.get('temperature')
        weather_condition = data.get('weatherCondition')
        date_time = data.get('dateTime')

        try:
            if not parser.isoparse(date_time):
                return jsonify({'error': 'Неверный формат даты и времени'}), 400
        except ValueError:
            return jsonify({'error': 'Неверный формат даты и времени'}), 400

        if not is_current_conditions(weather_condition):
            return jsonify({'error': 'Неверное состояние погоды'}), 400

        with connect() as session:
            forecast = session.query(Forecast).filter(Forecast.id == forecast_id).first()
            if not forecast:
                return jsonify({'error': 'Прогноза погоды с указанным идентификатором не существует'}), 404

            forecast.temperature = temperature
            forecast.weather_condition = weather_condition
            forecast.date_time = parser.isoparse(date_time)
            session.commit()

            updated_forecast_info = {
                'id': forecast.id,
                'dateTime': forecast.date_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                'temperature': forecast.temperature,
                'weatherCondition': forecast.weather_condition,
                'regionId': forecast.region_id
            }

        return jsonify(updated_forecast_info), 200


@app.route('/region/weather/forecast', methods=['POST'])
def add_weather_forecast():
    with connect() as session:
        if not user_is_auth(cookie_session, session):
            return jsonify({'error': 'Неверные авторизационные данные'}), 401

    data = request.json
    region_id = data.get('regionId')
    date_time = data.get('dateTime')
    temperature = data.get('temperature')
    weather_condition = data.get('weatherCondition')

    if is_current_id(region_id):
        return jsonify({'error': 'Некорректный идентификатор региона'}), 400

    try:
        if not parser.isoparse(date_time):
            return jsonify({'error': 'Неверный формат даты и времени'}), 400
    except ValueError:
        return jsonify({'error': 'Неверный формат даты и времени'}), 400

    if not is_current_conditions(weather_condition):
        return jsonify({'error': 'Неверное состояние погоды'}), 400

    with connect() as session:
        new_forecast = Forecast(
            region_id=region_id,
            date_time=parser.isoparse(date_time),
            temperature=temperature,
            weather_condition=weather_condition
        )
        session.add(new_forecast)
        session.commit()

        weather = session.query(Weather).filter(Weather.region_id == region_id).order_by(desc(Weather.id)).first()

        if weather is None:
            return jsonify({'error': 'Погода для указанного региона не найдена'}), 404

        new_forecast_info = {
            'id': new_forecast.id,
            'regionId': new_forecast.region_id,
            'temperature': new_forecast.temperature,
            'weatherCondition': new_forecast.weather_condition,
            'dateTime': new_forecast.date_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'precipitationAmount': weather.precipitation_amount,
            'windSpeed': weather.wind_speed
        }

    return jsonify(new_forecast_info), 200


@app.route('/region/weather/forecast/<int:forecast_id>', methods=['DELETE'])
def delete_weather_forecast(forecast_id):
    with connect() as session:
        if not user_is_auth(cookie_session, session):
            return jsonify({'error': 'Неверные авторизационные данные'}), 401

    if not is_current_id(forecast_id):
        return jsonify({'error': 'Некорректный идентификатор прогноза погоды'}), 400

    with connect() as session:
        forecast = session.query(Forecast).filter(Forecast.id == forecast_id).first()

        if forecast is None:
            return jsonify({'error': 'Прогноза погоды с указанным идентификатором не найдена'}), 404

        session.delete(forecast)
        session.commit()

    return '', 200


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Метод не найден'}), 404


@app.errorhandler(405)
def not_found(error):
    return jsonify({'error': 'Метод не разрешен'}), 405


@app.errorhandler(500)
def not_found(error):
    return jsonify({'error': 'Ошибка на стороне сервера'}), 404


def main():
    init_db()
    serve(app, host='0.0.0.0', port=5000, threads=10)


if __name__ == '__main__':
    main()
