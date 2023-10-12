import os
from movieDb import MovieDatabase

print(os.getcwd())

mdb = MovieDatabase("./movies.db")

mdb.delete_all_movies()

mdb.add_movie(
    "server1",
    "alien",
    "cathal",
    "{\"runtimes\": [120]}"
)
mdb.add_movie(
    "server1",
    "aliens",
    "cathal",
    "{\"runtimes\": [91]}"
)
mdb.add_movie(
    "server1",
    "school of rock",
    "tanzi",
    "{\"runtimes\": [60]}"
)
mdb.add_movie(
    "server1",
    "the constant gardener",
    "tanzi",
    "{\"runtimes\": [60]}"
)
mdb.add_movie(
    "server2",
    "spirited away",
    "orla",
    "{\"runtimes\": [60]}"
)
mdb.add_movie(
    "server2",
    "princess mononoke",
    "aisling",
    "{\"runtimes\": [60]}"
)
# res = mdb.execute_sql_read("SELECT * FROM movies")
# # res = mdb.execute_sql_read("SELECT movie_name, imdb_data->>'$.runtimes[0]' AS runtime FROM movies")
# res = mdb.get_movies_below_runtime("server1", 95)
# res = mdb.get_list_for_server("server1")
mdb.delete_movie_by_name("server1", "school of rock")
res = mdb.get_list_for_server("server1")
# print("results:", len(res))
for r in res:
    print(r)
