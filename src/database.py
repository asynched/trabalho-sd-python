from sqlite3 import connect
from github import GithubProfile
from dataclasses import dataclass
from globals import STUDENTS, TEACHERS


@dataclass()
class User:
    id: int
    name: str
    username: str
    avatar_url: str
    github_id: int
    role: str = "guest"
    grade: int = 0


class Database:
    def __init__(self, file: str = "dev.sqlite3"):
        self.connection = connect(file, check_same_thread=False)
        self.cursor = self.connection.cursor()

        self.__create_tables()

    def execute(self, query: str, params: tuple = ()):
        self.cursor.execute(query, params)
        self.connection.commit()

    def query(self, query: str, params: tuple = ()):
        self.cursor.execute(query, params)

        return self.cursor

    def __create_tables(self):
        users_query = """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                username TEXT NOT NULL UNIQUE,
                avatar_url TEXT NOT NULL,
                github_id INTEGER NOT NULL,
                role TEXT DEFAULT 'guest',
                grade INTEGER DEFAULT 0
            );
        """

        sessions_query = """
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
        """

        self.cursor.execute(users_query)
        self.cursor.execute(sessions_query)

    def __del__(self):
        self.connection.close()


class UserRepository:
    db: Database

    def __init__(self, database: Database):
        self.db = database

    def create_user(self, user: GithubProfile):
        query = """
            INSERT INTO users (name, username, avatar_url, github_id, role)
            VALUES (?, ?, ?, ?, ?);
        """

        role = "guest"

        if user.login in STUDENTS:
            role = "student"

        if user.login in TEACHERS:
            role = "teacher"

        self.db.execute(query, (user.name, user.login, user.avatar_url, user.id, role))

    def find_user_by_username(self, username: str):
        query = """
            SELECT * FROM users WHERE username = ?;
        """

        cursor = self.db.query(query, (username,))

        user = cursor.fetchone()

        if user is None:
            return None

        return User(
            id=user[0],
            name=user[1],
            username=user[2],
            avatar_url=user[3],
            github_id=user[4],
            role=user[5],
            grade=user[6],
        )

    def find_user_by_session(self, token: str):
        query = """
            SELECT users.* FROM users
            INNER JOIN sessions ON sessions.user_id = users.id
            WHERE sessions.token = ?;
        """

        cursor = self.db.query(query, (token,))

        user = cursor.fetchone()

        if user is None:
            return None

        return User(
            id=user[0],
            name=user[1],
            username=user[2],
            avatar_url=user[3],
            github_id=user[4],
            role=user[5],
            grade=user[6],
        )

    def update_grade(self, user_id: str, grade: int):
        query = """
            UPDATE users SET grade = ? WHERE id = ?;
        """

        self.db.execute(query, (grade, user_id))

    def get_users(self):
        query = """
            SELECT * FROM users;
        """

        cursor = self.db.query(query)

        users = cursor.fetchall()

        return [
            User(
                id=user[0],
                name=user[1],
                username=user[2],
                avatar_url=user[3],
                github_id=user[4],
                role=user[5],
                grade=user[6],
            )
            for user in users
        ]


class SessionRepository:
    db: Database

    def __init__(self, database: Database):
        self.db = database

    def create_session(self, user_id: int, token: str):
        query = """
            INSERT INTO sessions (user_id, token)
            VALUES (?, ?);
        """

        self.db.execute(query, (user_id, token))

        return self.find_session_by_token(token)

    def delete_session(self, token: str):
        query = """
            DELETE FROM sessions WHERE token = ?;
        """

        self.db.execute(query, (token,))

    def find_session_by_token(self, token: str) -> str:
        query = """
            SELECT token FROM sessions WHERE token = ?;
        """

        cursor = self.db.query(query, (token,))

        session = cursor.fetchone()

        if session is None:
            return None

        return session[0]
