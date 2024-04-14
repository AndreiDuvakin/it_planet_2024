from WeatherService.data.account import Account
from WeatherService.data.connect import connect


def user_is_auth(cookie_session, session) -> bool:
    if 'id' not in cookie_session:
        return False

    if not session.query(Account).filter(Account.id == cookie_session['id']).first():
        return False

    return True
