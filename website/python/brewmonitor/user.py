from functools import wraps
from typing import AnyStr, Optional, Dict, Iterator

import bcrypt
from flask import current_app
from flask_login import UserMixin, current_user

from brewmonitor.configuration import SQLConnection


class User(UserMixin):

    @classmethod
    def create_table_req(cls) -> str:
        # To pretend to be like storage.access.BaseTable
        return '''
            create table if not exists User (
                id integer primary key autoincrement,
                is_admin bool,
                username text not null,
                password text not null
            );
        '''

    @classmethod
    def from_db(cls, db_conn: SQLConnection, u_id: int) -> "User":
        data = db_conn.execute(
            '''
            select username, is_admin
            from User
            where id = ?;
            ''',
            (u_id,),
        ).fetchone()
        return cls(u_id, data[0], data[1])

    @classmethod
    def get_users(cls, db_conn: SQLConnection) -> Iterator[Dict]:
        data = db_conn.execute(
            '''
            select id, username, is_admin
            from User;
            ''',
        ).fetchall()

        def index_to_name(n):
            return {
                'id': n[0],
                'username': n[1],
                'is_admin': n[2],
            }

        return map(index_to_name, data)

    @classmethod
    def create(cls, db_conn: SQLConnection, username: AnyStr, password: AnyStr, is_admin: bool) -> "User":
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf8'), salt)
        cursor = db_conn.cursor()
        cursor.execute(
            '''
            insert into User (username, password, is_admin)
            values (?, ?, ?);
            ''',
            (username, hashed_password, is_admin)
        )
        # lastrowid is the last successful insert on that cursor
        return cls(cursor.lastrowid, username, is_admin)

    @classmethod
    def delete(cls, db_conn: SQLConnection, u_id: int):
        db_conn.execute(
            '''
            delete from User
            where id = ?;
            ''',
            (u_id,),
        )

    @classmethod
    def verify(cls, db_conn: SQLConnection, username: AnyStr, password: AnyStr) -> Optional["User"]:
        data = db_conn.execute(
            '''
            select id, is_admin, password
            from User
            where username = ?;
            ''',
            (username,),
        ).fetchone()

        if data is not None:
            hashed_password = data[2]
            if bcrypt.checkpw(password.encode('utf8'), hashed_password):
                return User(
                    data[0],
                    username,
                    data[1],
                )
        return None

    def __init__(self, u_id: int, name: AnyStr, is_admin: bool):
        self.id = u_id
        self.name = name
        self.is_admin = is_admin

    def is_active(self) -> bool:
        return True

    def is_anonymous(self) -> bool:
        return False

    def is_authenticated(self) -> bool:
        return True


def admin_required(func):

    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            return current_app.login_manager.unauthorized()
        return func(*args, **kwargs)
    return decorated_view
