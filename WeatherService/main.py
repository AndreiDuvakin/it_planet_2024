import os
import re

from dotenv import load_dotenv
from flask import Flask, request, jsonify, session as cookie_session
from flask_login import LoginManager

from WeatherService.data.region import Region
from WeatherService.data.region_type import RegionType
from data.connect import init_db, connect
from data.account import Account

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('secure_key')
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

    with connect() as session:
        if session.query(Account).filter(Account.email == data['email']).first() is not None:
            return jsonify({'error': 'Учетная запись с этим адресом электронной почты уже существует'}), 409

        new_user = Account(
            firstName=data['firstName'],
            lastName=data['lastName'],
            email=data['email']
        )
        new_user.set_password(data['password'])

        cookie_session['id'] = new_user.id

        session.add(new_user)
        session.commit()

        return jsonify({
            'id': new_user.id,
            'firstName': new_user.firstName,
            'lastName': new_user.lastName,
            'email': new_user.email
        }), 201


@app.route('/login', methods=['POST'])
def login():
    data = request.json

    if 'email' not in data or 'password' not in data:
        return jsonify({'error': 'Отсутствуют обязательные поля email и password'}), 400

    if not re.match(r'^[\w\.-]+@[\w\.-]+$', data['email']):
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
def get_account(account_id):
    if 'id' not in cookie_session:
        return jsonify({'error': 'Неверные авторизационные данные'}), 401

    if account_id is None or account_id <= 0:
        return jsonify({'error': 'Некорректный идентификатор аккаунта'}), 400

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

            if session.query(Account).filter(Account.email == data['email'],
                                             Account.id != account_id).first() is not None:
                return jsonify({'error': 'Аккаунт с таким email уже существует'}), 409

            user.firstName = data['firstName']
            user.lastName = data['lastName']
            user.email = data['email']
            user.set_password(data['password'])

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
    if 'id' not in cookie_session:
        return jsonify({'error': 'Неверные авторизационные данные'}), 401

    with connect() as session:
        if not session.query(Account).filter(Account.id == cookie_session['id']).first():
            return jsonify({'error': 'Неверные авторизационные данные'}), 401

    first_name = request.args.get('firstName', None)
    last_name = request.args.get('lastName', None)
    email = request.args.get('email', None)
    from_index = int(request.args.get('from', 0))
    size = int(request.args.get('size', 10))

    if from_index < 0 or size <= 0:
        return jsonify({'error': 'Некорректные параметры from или size'}), 400

    with connect() as session:
        query = session.query(Account)
        if first_name:
            query = query.filter(Account.firstName.ilike(f'%{first_name}%'))
        if last_name:
            query = query.filter(Account.lastName.ilike(f'%{last_name}%'))
        if email:
            query = query.filter(Account.email.ilike(f'%{email}%'))

        users = query.offset(from_index).limit(size).all()

        if not users:
            return jsonify({'error': 'Нет результатов поиска'}), 404

        result = [{'id': user.id, 'firstName': user.firstName, 'lastName': user.lastName, 'email': user.email}
                  for user in users]

        return jsonify(result), 200


@app.route('/region/<int:region_id>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def get_region(region_id):
    if 'id' not in cookie_session:
        return jsonify({'error': 'Неверные авторизационные данные'}), 401

    with connect() as session:
        if not session.query(Account).filter(Account.id == cookie_session['id']).first():
            return jsonify({'error': 'Неверные авторизационные данные'}), 401

    if region_id is None or region_id <= 0:
        return jsonify({'error': 'Некорректный идентификатор региона'}), 400

    with connect() as session:
        if session.query(Region).filter(Region.id == region_id).first() is None:
            return jsonify({'error': 'Регион с таким идентификатором не найден'}), 404

    if request.method == 'GET':
        with connect() as session:
            region = session.query(Region).filter(Region.id == region_id).first()

            response = {
                'id': region.id,
                'regionType': region.region_type,
                'accountld': region.account_id,
                'name': region.name,
                'parentRegion': region.parent_region,
                'latitude': region.latitude,
                'longitude': region.longitude
            }

            return jsonify(response), 200
    elif request.method == 'POST':
        data = request.json

        if not all(field in data for field in ['name', 'latitude', 'longitude']):
            return jsonify({'error': 'Отсутствуют обязательные поля в теле запроса'}), 400

        with connect() as session:
            existing_region = session.query(Region).filter_by(latitude=data['latitude'],
                                                              longitude=data['longitude']).first()
            if existing_region is not None:
                return jsonify({'error': 'Регион с такими координатами уже существует'}), 409

        new_region = Region(
            name=data['name'],
            parent_region=data.get('parentRegion', ''),
            region_type=data.get('regionType', ''),
            latitude=data['latitude'],
            longitude=data['longitude'],
            account_id=cookie_session['id']
        )

        with connect() as session:
            session.add(new_region)
            session.commit()

        response = {
            'id': new_region.id,
            'name': new_region.name,
            'parentRegion': new_region.parent_region,
            'regionType': new_region.region_type,
            'latitude': new_region.latitude,
            'longitude': new_region.longitude
        }

        return jsonify(response), 201
    elif request.method == 'PUT':
        data = request.json

        if not data or 'name' not in data or 'latitude' not in data or 'longitude' not in data:
            return jsonify({'error': 'Отсутствуют обязательные поля в теле запроса'}), 400

        with connect() as session:
            region = session.query(Region).filter(Region.id == region_id).first()

            if region.account_id != cookie_session['id']:
                return jsonify({'error': 'Недостаточно прав для изменения этого региона'}), 403

            existing_region = session.query(Region).filter(Region.latitude == data['latitude'],
                                                           Region.longitude == data['longitude']).first()
            if existing_region and existing_region.id != region_id:
                return jsonify({'error': 'Регион с такими координатами уже существует'}), 409

            region.name = data['name']
            region.parent_region = data.get('parentRegion', region.parent_region)
            region.region_type = data.get('regionType', region.region_type)
            region.latitude = data['latitude']
            region.longitude = data['longitude']

            session.commit()

            response = {
                'id': region.id,
                'name': region.name,
                'parentRegion': region.parent_region,
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


@app.route('/region/types/<int:type_id>', methods=['GET'])
def get_region_type(type_id):
    if 'id' not in cookie_session:
        return jsonify({'error': 'Неверные авторизационные данные'}), 401

    with connect() as session:
        if not session.query(Account).filter(Account.id == cookie_session['id']).first():
            return jsonify({'error': 'Неверные авторизационные данные'}), 401

    if type_id is None or type_id <= 0:
        return jsonify({'error': 'Некорректный идентификатор типа региона'}), 400

    with connect() as session:
        region_type = session.query(RegionType).filter(RegionType.id == type_id).first()

        if region_type is None:
            return jsonify({'error': 'Тип региона с таким идентификатором не найден'}), 404

        response = {
            'id': region_type.id,
            'type': region_type.type
        }

        return jsonify(response), 200


@app.route('/region/types', methods=['POST'])
def add_region_type():
    if 'id' not in cookie_session:
        return jsonify({'error': 'Запрос от неавторизованного аккаунта'}), 401

    with connect() as session:
        if not session.query(Account).filter(Account.id == cookie_session['id']).first():
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


def main():
    init_db()
    app.run(host='localhost', port=5000)
    # serve(app, host='localhost', port=5000, threads=100)


if __name__ == '__main__':
    main()
