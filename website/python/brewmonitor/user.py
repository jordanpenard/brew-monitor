from flask_login import UserMixin
from brewmonitor.utils import config

class User(UserMixin):
    def __init__(self, id):
        self.id = id

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
                select id
                from User
                where username = ? and password = ?;
                ''',
                (username, password)
            ).fetchone()            
            if data is None:
                return 0
            else:
                return data[0]
    
    def get_name(self):
        with config().db_connection() as db_conn:
            data = db_conn.execute(
                '''
                select username
                from User
                where id = ?;
                ''',
                (self.id)
            )
            return data.fetchone()[0]

    def is_admin(self):
        with config().db_connection() as db_conn:
            data = db_conn.execute(
                '''
                select is_admin
                from User
                where id = ?;
                ''',
                (self.id)
            )
            return data.fetchone()[0]
