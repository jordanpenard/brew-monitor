import bcrypt
from flask_login import UserMixin
from brewmonitor.utils import config

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
