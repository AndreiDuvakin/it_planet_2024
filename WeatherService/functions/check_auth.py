from WeatherService.data.account import Account
from WeatherService.data.connect import connect


def user_is_auth(cookie_session) -> bool:
    if 'id' not in cookie_session:
        return False

    with connect() as session:
        if not session.query(Account).filter(Account.id == cookie_session['id']).first():
            return False

    return True
