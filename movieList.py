"""
Module for managing a persistent list of movies.
The list is stored in a picked hashmap of movie
names to imdb info
"""
import logging
import random
import pickle
import re
from imdb import Cinemagoer
from movieDb import MovieDatabase

IMDB_ID = "imdbID"
MAIN_INFO_KEY = "main"
RUNTIMES_KEY = "runtimes"
TITLE_KEY = "title"
LONG_TITLE_KEY = "long imdb title"
MOVIELIST_FILENAME = "/data/movies.pickle"
LOG_FILENAME = "/data/movie_list.log"
IMDB_URL_PATTERN = "imdb\.com/title/tt(\d+)"
IMDB_URL_BASE = "https://www.imdb.com/title/tt"

logging.basicConfig(
    filename=LOG_FILENAME,
    level=logging.INFO,
    format='%(asctime)s - %(message)s')

def logged(func):
    def modified_func(*args, **kwargs):
        logging.info(f"{func.__name__} (args: {args}, {kwargs})")
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(e)
            raise e
    return modified_func

@logged
def _get_movie_runtime_from_movie_info(movie_info):
    if RUNTIMES_KEY in movie_info:
        return int(movie_info[RUNTIMES_KEY][0])
    raise Exception(f"no runtime found for {movie_info[TITLE_KEY]}")

@logged
def _match_imdb_url(query):
    url_match = re.search(IMDB_URL_PATTERN, query)
    return url_match

@logged
def _build_imdb_link(movie_id):
    return IMDB_URL_BASE + movie_id

class MovieList():
    """A list of movies and related information"""

    @logged
    def __init__(self):
        self.ia = Cinemagoer()
        self.mdb = MovieDatabase("./movies.db")
        # server -> movie
        self.last_movie_mentioned = {}
        self.search_cache = {}

    @logged
    def search_list(self, server, query):
        search_result = self.mdb.search_movies_by_name(server, query)
        return search_result

    @logged
    def pick_random_movie_name(self, server):
        movie_name = self.mdb.pick_movie(server)
        self.last_movie_mentioned[server] = movie_name
        return movie_name

    @logged
    def get_movie_names(self, server):
        return self.mdb.get_list_for_server(server)

    @logged
    def add_movie(self, server, user, movie_query):
        if movie_query == None:
            movie_query = self.last_movie_mentioned[server]
        url_match = _match_imdb_url(movie_query)
        if url_match:
            imdb_id = url_match.group(1)
            movie_info = self._get_movie_info_by_id(imdb_id)
            movie_name = movie_info[LONG_TITLE_KEY]
        else:
            movie_info = self._get_movie_info(movie_query)
            movie_name = movie_query

        pickled_data = pickle.dumps(movie_info, pickle.HIGHEST_PROTOCOL)
        runtime = _get_movie_runtime_from_movie_info(movie_info)
        self.mdb.add_movie(
                server,
                movie_name,
                user,
                runtime,
                pickled_data)
        self.last_movie_mentioned[server] = movie_name
        return movie_name

    @logged
    def remove_movie_name(self, server, movie_name):
        if movie_name == None:
            movie_name = self.last_movie_mentioned[server]
        self.mdb.delete_movie_by_name(server, movie_name)
        return movie_name

    @logged
    def correct_movie(self, server, user, option):
        if option == None:
            return self._get_correct_movie_options(self.last_movie_mentioned[server])
        elif option.isdigit():
            return self._set_correct_movie_option(server, int(option))
        elif _match_imdb_url(option):
            self.remove_movie_name(server, server, self.last_movie_mentioned[server])
            return self.add_movie(server, user, option)
        self.last_movie_mentioned[server] = option
        return self._get_correct_movie_options(option)

    @logged
    def _set_correct_movie_option(self, server, option_number):
        search_results = self._search_for_movie(self.last_movie_mentioned[server], 5)
        correct_option = search_results[option_number]
        correct_option_link = _build_imdb_link(correct_option.movieID)

        old_option = self._get_movie_info(self.last_movie_mentioned[server])
        old_option_caption = old_option[LONG_TITLE_KEY]

        self.remove_movie_name(self.last_movie_mentioned[server])
        new_option_name = self.add_movie(correct_option_link)

        new_option = self._get_movie_info(new_option_name)
        new_option_caption = new_option[LONG_TITLE_KEY]

        new_option_link = self._get_imdb_link(new_option_name)
        self.last_movie_mentioned = new_option_caption
        return f"Replaced {old_option_caption} with {new_option_caption}\n{new_option_link}"

    @logged
    def _get_correct_movie_options(self, movie_query):
        search_results = self._search_for_movie(movie_query, 5)
        def create_tuple(movie):
            imdb_url = _build_imdb_link(movie.movieID)
            return (movie[LONG_TITLE_KEY], imdb_url)
        search_infos = list(map(create_tuple, search_results))
        return search_infos

    @logged
    def get_imdb_link(self, server, movie_name):
        if movie_name == None:
            movie_name = self.last_movie_mentioned[server]
        return self._get_imdb_link(movie_name)

    @logged
    def get_movies_below_runtime(self, server, runtime):
        movies = self.mdb.get_movies_below_runtime(server, runtime)
        return movies

    @logged
    def pick_random_movie_below_runtime(self, server, runtime):
        result = self.mdb.pick_random_movie_below_runtime(server, runtime)
        self.last_movie_mentioned[server] = result
        return result

    @logged
    def get_movie_runtime(self, server, movie_name):
        if movie_name is None:
            movie_name = self.last_movie_mentioned[server]
        movie = self._get_movie_info(movie_name)
        self.last_movie_mentioned[server] = movie_name
        return _get_movie_runtime_from_movie_info(movie)

    @logged
    def _search_for_movie(self, movie_name, number_of_results=None):
        if movie_name not in self.search_cache:
            self.search_cache[movie_name] = self.ia.search_movie(movie_name)
        movie_search_results = self.search_cache[movie_name]
        if len(movie_search_results) < 1:
            raise Exception(f"couldn't find movie {movie_name}")
        if number_of_results != None:
            return movie_search_results[:number_of_results]
        return movie_search_results[0]

    @logged
    def _get_movie_by_id(self, movie_id):
        movie = self.ia.get_movie(movie_id)
        return movie

    @logged
    def _get_movie_id(self, movie_name):
        logging.info(f"_get_movie_id movie_name: {movie_name}")
        movie = self._get_movie_info(movie_name)
        logging.info(f"movie: {movie}")
        movieId = movie.movieID
        logging.info(f"movieId: {movieId}")
        return movieId
        
    @logged
    def _get_imdb_link(self, movie_name):
        movieId = self._get_movie_id(movie_name)
        url = f"https://www.imdb.com/title/tt{movieId}"
        self.last_movie_mentioned = movie_name
        return url

    @logged
    def _update_movie(self, movie):
        self.ia.update(movie, info=[MAIN_INFO_KEY])
        return movie

    @logged
    def _get_movie_info_by_id(self, movie_id):
        movie_info = self.ia.get_movie(movie_id)
        return movie_info

    @logged
    def _get_movie_info(self, movie_name):
        results = self.mdb.get_imdb_data(movie_name)
        if len(results) < 1:
            print(f"fetching data for {movie_name}")
            movie_result = self._search_for_movie(movie_name)
            movie_info = self._update_movie(movie_result)
        elif len(results) > 1:
            raise Exception(f"too many results for {movie_name}. Found: {[name for (name, data) in results]}")
        else:
            print(f"reading {movie_name} from cache")
            movie_info = results[0][1]
        return movie_info
