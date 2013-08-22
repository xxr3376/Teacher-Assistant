from models import User
def auth_user(username, password):
    user = User.query.filter_by(username=username).first()
    if user is None:
        return None
    else:
        return user if user.check_password(password) else None
