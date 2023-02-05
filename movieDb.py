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
    SELECT id, movie_name FROM movies
        WHERE server = %s
        ORDER BY movie_name
"""

SEARCH_STATEMENT = """
    SELECT id, movie_name
        FROM movies
        WHERE
            server = %s AND
            LOWER(movie_name) LIKE CONCAT('%', LOWER(%s), '%')
        ORDER BY CHAR_LENGTH(movie_name) ASC
"""

SEARCH_RUNTIME_STATEMENT = """
    SELECT id, movie_name
        FROM movies
        WHERE
            server = %s AND
            CAST(imdb_data->>'$.runtimes[0]' AS UNSIGNED) <
            CAST(%s AS UNSIGNED)
        ORDER BY movie_name
"""

PICK_RUNTIME_STATEMENT = """
    SELECT id, movie_name
        FROM movies
        WHERE
            server = %s AND
            CAST(imdb_data->>'$.runtimes[0]' AS UNSIGNED) <
            CAST(%s AS UNSIGNED)
        ORDER BY RAND()
        LIMIT 1
"""

GET_IMDB_DATA_STATEMENT = """
    SELECT id, movie_name, imdb_data
        FROM movies
        WHERE 
            # maybe this should include server?
            LOWER(movie_name) LIKE CONCAT('%', LOWER(%s), '%')
            ORDER BY CHAR_LENGTH(movie_name) ASC
"""

DELETE_STATEMENT = """
    DELETE FROM movies WHERE id = %s
"""

DELETE_ALL_STATEMENT = """
    DELETE FROM movies
"""

PICK_STATEMENT = """
    SELECT id, movie_name
        FROM movies
        ORDER BY RAND()
        LIMIT 1;
"""

RUNTIMES_KEY = "runtimes"

def _get_names_from_search_result(result):
    return [name for (_,name) in result]

"""
Persists a database of movies along with their imdb data
"""
class MovieDatabase():

    def _get_db_connection(self):
        # TODO config
        return mysql.connector.connect(
            user='root',
            password='swordfish',
            # TODO currently the mysql container is on a diff network.
            # migrate bert build.sh to docker-compose.
            # services in a docker-composeget put into the same network by default

            # host='539c8a9820dd',
            # host='127.0.0.1',
            # host='539c8a9820ddfb01f3437dd643191635879d9b3d0a35c3cf98dcb5c11de6d1fc',
            host='mysql',
            database='movies')

    def add_movie(self, server, movie_name, created_by, imdb_data):
        with self._get_db_connection() as cxn:
            with cxn.cursor(prepared=True) as cursor:
                movie_record = (server, movie_name, created_by, imdb_data)
                cursor.execute(INSERT_STATEMENT, movie_record)
            cxn.commit()

    # def execute_sql_read(self, sql):
    #     with self._get_db_connection() as cxn:
    #         with cxn.cursor() as cursor:
    #             cursor.execute(sql)
    #             return cursor.fetchall()

    def get_list_for_server(self, server):
        with self._get_db_connection() as cxn:
            with cxn.cursor() as cursor:
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
        with self._get_db_connection() as cxn:
            with cxn.cursor() as cursor:
                cursor.execute(DELETE_STATEMENT, (found_id,))
            cxn.commit()

    def delete_all_movies(self):
        with self._get_db_connection() as cxn:
            with cxn.cursor(prepared=True) as cursor:
                cursor.execute(DELETE_ALL_STATEMENT)
            cxn.commit()

    def _search_movies_by_name(self, server, movie_name):
        with self._get_db_connection() as cxn:
            with cxn.cursor(prepared=True) as cursor:
                search_record = (server, movie_name)
                cursor.execute(SEARCH_STATEMENT, search_record)
                return cursor.fetchall()

    def search_movies_by_name(self, server, movie_name):
        return _get_names_from_search_result(self._search_movies_by_name(server, movie_name))

    def get_movies_below_runtime(self, server, runtime):
        with self._get_db_connection() as cxn:
            with cxn.cursor(prepared=True) as cursor:
                search_details = (server, runtime)
                cursor.execute(SEARCH_RUNTIME_STATEMENT, search_details)
                return _get_names_from_search_result(cursor.fetchall())

    def pick_movie(self, server):
        with self._get_db_connection() as cxn:
            with cxn.cursor(prepared=True) as cursor:
                cursor.execute(PICK_STATEMENT)
                return _get_names_from_search_result(cursor.fetchall())

    def pick_movie_below_runtime(self, server, runtime):
        with self._get_db_connection() as cxn:
            with cxn.cursor(prepared=True) as cursor:
                search_details = (server, runtime)
                cursor.execute(PICK_RUNTIME_STATEMENT, search_details)
                return _get_names_from_search_result(cursor.fetchall())

    def get_imdb_data(self, movie_name):
        with self._get_db_connection() as cxn:
            with cxn.cursor(prepared=True) as cursor:
                search_details = (movie_name,)
                cursor.execute(GET_IMDB_DATA_STATEMENT, search_details)
                result = cursor.fetchall()
                return [(movie_name, imdb_data) for (_, movie_name, imdb_data) in result]
