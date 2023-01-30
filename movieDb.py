import mysql.connector

INSERT_STATEMENT = """
    INSERT INTO movies (
        server,
        movie_name,
        created_by,
        imdb_data
    ) VALUES (%s,%s,%s,%s)
"""

SELECT_ALL_FOR_SERVER_STATEMENT = """
    SELECT movie_name FROM movies
        WHERE server = %s
"""

SELECT_ALL_STATEMENT = """
    SELECT * FROM movies
"""

SEARCH_STATEMENT = """
    SELECT id, movie_name
        FROM movies
        WHERE
            server = %s AND
            LOWER(movie_name) LIKE CONCAT('%', LOWER(%s), '%')
"""

SEARCH_RUNTIME_STATEMENT = """
    SELECT id, movie_name
        FROM movies
        WHERE
            server = %s AND
            CAST(imdb_data->>'$.runtimes[0]' AS UNSIGNED) <
            CAST(%s AS UNSIGNED)
"""

DELETE_STATEMENT = """
    DELETE FROM movies WHERE id = %s
"""

DELETE_ALL_STATEMENT = """
    DELETE FROM movies
"""

RUNTIMES_KEY = "runtimes"

"""
Persists a database of movies along with their imdb data
"""
class MovieDatabase():

    def _get_db_connection(self):
        return mysql.connector.connect(
            user='root',
            password='swordfish',
            host='127.0.0.1',
            database='movies')

    def add_movie(self, server, movie_name, created_by, imdb_data):
        with self._get_db_connection() as cxn:
            with cxn.cursor(prepared=True) as cursor:
                movie_record = (server, movie_name, created_by, imdb_data)
                cursor.execute(INSERT_STATEMENT, movie_record)
            cxn.commit()

    def execute_sql_read(self, sql):
        with self._get_db_connection() as cxn:
            with cxn.cursor() as cursor:
                cursor.execute(sql)
                return cursor.fetchall()

    def get_list_for_server(self, server):
        with self._get_db_connection() as cxn:
            with cxn.cursor() as cursor:
                search = (server,)
                cursor.execute(SELECT_ALL_FOR_SERVER_STATEMENT, search)
                return cursor.fetchall()

    def delete_movie(self, server, movie_name):
        search_result = self.search_movies_by_name(server, movie_name)
        if len(search_result) == 0:
            raise Exception("Couldn't find any movies with the name: " + movie_name)
        elif len(search_result) > 1:
            raise Exception("Found more than one movie with the name: " + movie_name)            
        else:
            found_id = search_result[0][0]
        with self._get_db_connection() as cxn:
            with cxn.cursor() as cursor:
                cursor.execute(DELETE_STATEMENT, (found_id,))
            cxn.commit()

    def delete_all_movies(self):
        with self._get_db_connection() as cxn:
            with cxn.cursor(prepared=True) as cursor:
                cursor.execute(DELETE_ALL_STATEMENT)
            cxn.commit()

    def search_movies_by_name(self, server, movie_name):
        with self._get_db_connection() as cxn:
            with cxn.cursor(prepared=True) as cursor:
                search_record = (server, movie_name)
                cursor.execute(SEARCH_STATEMENT, search_record)
                return cursor.fetchall()

    def get_movies_below_runtime(self, server, runtime):
        with self._get_db_connection() as cxn:
            with cxn.cursor(prepared=True) as cursor:
                search_details = (server, runtime)
                cursor.execute(SEARCH_RUNTIME_STATEMENT, search_details)
                return cursor.fetchall()
