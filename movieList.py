"""
Module for managing a persistent list of movies.
The list is stored in a picked hashmap of movie
names to imdb info
"""
import logging
import random
import pickle
import re
from imdb import IMDb

IMDB_ID = "imdbID"
MAIN_INFO_KEY = "main"
RUNTIMES_KEY = "runtimes"
TITLE_KEY = "title"
LONG_TITLE_KEY = "long imdb title"
MOVIELIST_FILENAME = "/data/movies.pickle"
LOG_FILENAME = "/data/movie_list.log"
PIRATE_SEARCH_BASE = "https://thepiratebay.org/search.php?q="
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
def _create_initial_movies():
    return dict()

@logged
def _save(obj, filename):
    # print(f"writing {filename} with this data: {obj}")
    with open(filename, "wb") as f:
        pickle.dump(obj, f)

@logged
def _load(filename):
    with open(filename, "rb") as f:
        return pickle.load(f)

@logged
def _save_movies(obj):
    _save(obj, MOVIELIST_FILENAME)

@logged
def _load_movies():
    return _load(MOVIELIST_FILENAME)

@logged
def _get_movies():
    try:
        return _load_movies()
    except Exception as e:
        print(f"failed to read file, initializing instead")
        print(f"previous: {e}")
        data = _create_initial_movies()
        _save_movies(data)
        return data

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
        self.ia = IMDb()
        self.last_movie_mentioned = ""
        self.search_cache = {}

    @logged
    def search_list(self, query):
        names = self.get_movie_names()

        def matches_query(movie_name):
            return str.lower(query) in str.lower(movie_name)

        filtered_movie_names = filter(matches_query, names)
        return list(filtered_movie_names)

    @logged
    def pick_random_movie_name(self):
        names = self.get_movie_names()
        movie_name = random.choice(list(names))
        self.last_movie_mentioned = movie_name
        return movie_name

    @logged
    def get_movie_names(self):
        return list(_get_movies().keys())

    @logged
    def add_movie(self, movie_query):
        if movie_query == None:
            movie_query = self.last_movie_mentioned
        url_match = _match_imdb_url(movie_query)
        if url_match:
            imdb_id = url_match.group(1)
            movie_info = self._get_movie_info_by_id(imdb_id)
            movie_name = movie_info[LONG_TITLE_KEY]
        else:
            movie_info = self._get_movie_info(movie_query)
            movie_name = movie_query

        movies = _get_movies()
        movies[movie_name] = movie_info
        _save_movies(movies)
        self.last_movie_mentioned = movie_name
        return movie_name

    @logged
    def remove_movie_name(self, movie_name):
        if movie_name == None:
            movie_name = self.last_movie_mentioned
        movies = _get_movies()
        if movie_name in movies:
            del movies[movie_name]
            _save_movies(movies)
            return movie_name
        return None

    @logged
    def correct_movie(self, option):
        if option == None:
            return self._get_correct_movie_options(self.last_movie_mentioned)
        elif option.isdigit():
            return self._set_correct_movie_option(int(option))
        elif _match_imdb_url(option):
            self.remove_movie_name(self.last_movie_mentioned)
            return self.add_movie(option)
        self.last_movie_mentioned = option
        return self._get_correct_movie_options(option)

    @logged
    def _set_correct_movie_option(self, option_number):
        search_results = self._search_for_movie(self.last_movie_mentioned, 5)
        correct_option = search_results[option_number]
        correct_option_link = _build_imdb_link(correct_option.movieID)

        old_option = self._get_movie_info(self.last_movie_mentioned)
        old_option_caption = old_option[LONG_TITLE_KEY]

        self.remove_movie_name(self.last_movie_mentioned)
        new_option_name = self.add_movie(correct_option_link)

        new_option = self._get_movie_info(new_option_name)
        new_option_caption = new_option[LONG_TITLE_KEY]

        new_option_link = self.get_imdb_link(new_option_name)
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
    def get_imdb_link(self, movie_name):
        if movie_name is None:
            movie_name = self.last_movie_mentioned
        movieId = self._get_movie_id(movie_name)
        url = f"https://www.imdb.com/title/tt{movieId}"
        self.last_movie_mentioned = movie_name
        return url

    @logged
    def get_pirate_link(self, movie_name):
        if movie_name is None:
            movie_name = self.last_movie_mentioned
        search_url = PIRATE_SEARCH_BASE + movie_name.replace(" ", "+")
        return search_url

    @logged
    def get_movies_below_runtime(self, runtime):
        movies = _get_movies()
        movie_names = list(movies.keys())

        def check_runtime(movie_name):
            movie_info = movies[movie_name]
            try:
                movie_runtime = _get_movie_runtime_from_movie_info(movie_info)
                return movie_runtime < runtime
            except Exception as e:
                print(e)
                return False

        filtered_movie_names = filter(check_runtime, movie_names)
        return list(filtered_movie_names)

    @logged
    def pick_random_movie_below_runtime(self, runtime):
        movie_name = random.choice(self.get_movies_below_runtime(runtime))
        self.last_movie_mentioned = movie_name
        return movie_name

    @logged
    def get_movie_runtime(self, movie_name):
        if movie_name is None:
            movie_name = self.last_movie_mentioned
        movie = self._get_movie_info(movie_name)
        self.last_movie_mentioned = movie_name
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
    def _update_movie(self, movie):
        self.ia.update(movie, info=[MAIN_INFO_KEY])
        return movie

    @logged
    def _get_movie_info_by_id(self, movie_id):
        movie_info = self.ia.get_movie(movie_id)
        return movie_info

    @logged
    def _get_movie_info(self, movie_name):
        movies = _get_movies()
        if  movie_name not in movies or movies[movie_name] is None:
            print(f"fetching data for {movie_name}")
            movie_result = self._search_for_movie(movie_name)
            movie_info = self._update_movie(movie_result)
        else:
            print(f"reading {movie_name} from cache")
            movie_info = movies[movie_name]
        return movie_info
