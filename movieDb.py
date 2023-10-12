import sqlite3
import time
import pickle

CREATE_MOVIES_TABLE_STATEMENT = """
    CREATE TABLE IF NOT EXISTS movies (
    id INTEGER PRIMARY KEY,
    server TEXT NOT NULL,
    movie_name TEXT NOT NULL,
    username TEXT NOT NULL,
    runtime_mins INTEGER NOT NULL,
    imdb_data BLOB
)"""

INSERT_STATEMENT = """
    INSERT INTO movies (
        server,
        movie_name,
        username,
        runtime_mins,
        imdb_data
    ) VALUES (?, ?, ?, ?, ?)
"""

SELECT_ALL_FOR_SERVER_STATEMENT = """
    SELECT id, movie_name FROM movies
        WHERE server = ?
        ORDER BY movie_name
"""

SEARCH_STATEMENT = """
    SELECT id, movie_name
        FROM movies
        WHERE
            server = ? AND
            LOWER(movie_name) LIKE '%' || LOWER(?) || '%'
        ORDER BY LENGTH(movie_name) ASC
"""

SEARCH_RUNTIME_STATEMENT = """
    SELECT id, movie_name
        FROM movies
        WHERE
            server = ? AND
            CAST(runtime_mins AS UNSIGNED) <
            CAST(? AS UNSIGNED)
        ORDER BY movie_name
"""

PICK_RUNTIME_STATEMENT = """
    SELECT id, movie_name
        FROM movies
        WHERE
            server = ? AND
            CAST(runtime_mins AS UNSIGNED) <
            CAST(? AS UNSIGNED)
        ORDER BY RANDOM()
        LIMIT 1
"""

GET_IMDB_DATA_STATEMENT = """
    SELECT id, movie_name, imdb_data
        FROM movies
        WHERE 
            LOWER(movie_name) LIKE '%' || LOWER(?) || '%'
            ORDER BY LENGTH(movie_name) ASC
"""

DELETE_STATEMENT = """
    DELETE FROM movies WHERE id = ?
"""

DELETE_ALL_STATEMENT = """
    DELETE FROM movies
"""

PICK_STATEMENT = """
    SELECT id, movie_name
        FROM movies
        ORDER BY RANDOM()
        LIMIT 1;
"""

RUNTIMES_KEY = "runtimes"

def _get_names_from_search_result(result):
    return [name for (_, name) in result]

def _log(message):
    print(f"{time.time()}[movieDb.py] {message}")

class MovieDatabase():

    def __init__(self, db_path):
        self.db_path = db_path
        self._initialise_db()

    def _initialise_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(CREATE_MOVIES_TABLE_STATEMENT)
            conn.commit()

    def add_movie(self, server, movie_name, username, runtime, imdb_data):
        _log(f"add_movie: {server}, {movie_name}, {username}, {type(imdb_data)}")
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            movie_record = (server, movie_name, username, runtime, imdb_data)
            cursor.execute(INSERT_STATEMENT, movie_record)
            conn.commit()

    def get_list_for_server(self, server):
        _log(f"get_list_for_server: {server}")
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            search = (server,)
            cursor.execute(SELECT_ALL_FOR_SERVER_STATEMENT, search)
            return _get_names_from_search_result(cursor.fetchall())

    def delete_movie_by_name(self, server, movie_name):
        search_result = self._search_movies_by_name(server, movie_name)
        if len(search_result) == 0:
            raise Exception(f"Couldn't find any movies with the name: {movie_name}")
        elif len(search_result) > 1:
            raise Exception(f"Found more than one movie with the name: {movie_name}. Found: {search_result}")
        else:
            found_id = search_result[0][0]
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(DELETE_STATEMENT, (found_id,))
            conn.commit()

    def delete_all_movies(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(DELETE_ALL_STATEMENT)
            conn.commit()

    def _search_movies_by_name(self, server, movie_name):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            search_record = (server, movie_name)
            cursor.execute(SEARCH_STATEMENT, search_record)
            return cursor.fetchall()

    def search_movies_by_name(self, server, movie_name):
        return _get_names_from_search_result(self._search_movies_by_name(server, movie_name))

    def get_movies_below_runtime(self, server, runtime):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            search_details = (server, runtime)
            cursor.execute(SEARCH_RUNTIME_STATEMENT, search_details)
            return _get_names_from_search_result(cursor.fetchall())

    def pick_movie(self, server):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(PICK_STATEMENT)
            return _get_names_from_search_result(cursor.fetchall())

    def pick_movie_below_runtime(self, server, runtime):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            search_details = (server, runtime)
            cursor.execute(PICK_RUNTIME_STATEMENT, search_details)
            return _get_names_from_search_result(cursor.fetchall())

    def get_imdb_data(self, movie_name):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            search_details = (movie_name,)
            cursor.execute(GET_IMDB_DATA_STATEMENT, search_details)
            result = cursor.fetchall()

            return [(movie_name, pickle.loads(imdb_data)) for (_, movie_name, imdb_data) in result]
