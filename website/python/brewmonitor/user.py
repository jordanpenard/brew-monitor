import bcrypt
from flask import current_app
from flask_login import UserMixin, current_user
from brewmonitor.utils import config
from functools import wraps

class User(UserMixin):
    def __init__(self, id):
        self.id = id
        with config().db_connection() as db_conn:
            data = db_conn.execute(
                '''
                select username, is_admin
                from User
                where id = ?;
                ''',
                (id,)
            ).fetchone()
            self.name = data[0]
            self.is_admin = data[1]
    
    def get_users():
        with config().db_connection() as db_conn:
            data = db_conn.execute(
                '''
                select id, username, is_admin
                from User;
                '''
            ).fetchall()
            
            def index_to_name(n):
                return {'id':n[0],'username':n[1],'is_admin':n[2]}
                
            return map(index_to_name, data)

    def add(username, password, is_admin):
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf8'), salt)
        with config().db_connection() as db_conn:
            db_conn.execute(
                '''
                insert into User (username, password, is_admin)
                values (?, ?, ?);
                ''',
                (username, hashed_password, is_admin)
            )

    def delete(id):
        with config().db_connection() as db_conn:
            db_conn.execute(
                '''
                delete from User
                where id = ?;
                ''',
                (id,)
            )

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return True

    def verify(username, password):
        with config().db_connection() as db_conn:
            data = db_conn.execute(
                '''
                select id, password
                from User
                where username = ?;
                ''',
                (username,)
            ).fetchone()

            if data is not None:
                id = data[0]
                hashed_password = data[1]
                if bcrypt.checkpw(password.encode('utf8'), hashed_password) is True:
                    return User(id)
        return None


def admin_required(func):

    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            return current_app.login_manager.unauthorized()
        return func(*args, **kwargs)
    return decorated_view
    
