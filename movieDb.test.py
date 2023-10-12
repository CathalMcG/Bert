import unittest
import tempfile
import os
import json
from movieDb import MovieDatabase

class TestMovieDatabase(unittest.TestCase):

    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp()
        self.db = MovieDatabase(self.db_path)

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def test_add_movie(self):
        self.db.add_movie("server1", "Movie 1", "user1", json.dumps({"runtimes": [120]}))
        movies = self.db.get_list_for_server("server1")
        self.assertIn("Movie 1", movies)

    def test_delete_movie_by_name(self):
        self.db.add_movie("server1", "Movie 1", "user1", json.dumps({"runtimes": [120]}))
        self.db.delete_movie_by_name("server1", "Movie 1")
        movies = self.db.get_list_for_server("server1")
        self.assertNotIn("Movie 1", movies)

    def test_search_movies_by_name(self):
        self.db.add_movie("server1", "Movie 1", "user1", json.dumps({"runtimes": [120]}))
        self.db.add_movie("server1", "Movie 2", "user1", json.dumps({"runtimes": [90]}))
        self.db.add_movie("server1", "Filme 3", "user1", json.dumps({"runtimes": [90]}))
        results = self.db.search_movies_by_name("server1", "movie")
        self.assertEqual(len(results), 2)

    def test_get_movies_below_runtime(self):
        self.db.add_movie("server1", "Movie 1", "user1", json.dumps({"runtimes": [120]}))
        self.db.add_movie("server1", "Movie 2", "user1", json.dumps({"runtimes": [90]}))
        self.db.add_movie("server1", "Movie 3", "user1", json.dumps({"runtimes": [90]}))
        results = self.db.get_movies_below_runtime("server1", 100)
        self.assertEqual(len(results), 2)

    def test_pick_movie(self):
        self.db.add_movie("server1", "Movie 1", "user1", json.dumps({"runtimes": [120]}))
        self.db.add_movie("server1", "Movie 2", "user1", json.dumps({"runtimes": [90]}))
        movie = self.db.pick_movie("server1")
        self.assertIn(movie[0], ["Movie 1", "Movie 2"])

    def test_pick_movie_below_runtime(self):
        self.db.add_movie("server1", "Movie 1", "user1", json.dumps({"runtimes": [120]}))
        self.db.add_movie("server1", "Movie 2", "user1", json.dumps({"runtimes": [90]}))
        self.db.add_movie("server1", "Movie 3", "user1", json.dumps({"runtimes": [90]}))
        self.db.add_movie("server1", "Movie 4", "user1", json.dumps({"runtimes": [90]}))
        movie = self.db.pick_movie_below_runtime("server1", 100)
        self.assertIn(movie[0], ["Movie 2", "Movie 3", "Movie 4"])

    def test_get_imdb_data(self):
        self.db.add_movie("server1", "Movie 1", "user1", json.dumps({"runtimes": [120]}))
        imdb_data = self.db.get_imdb_data("Movie 1")
        self.assertEqual(len(imdb_data), 1)
        self.assertEqual(imdb_data[0][0], "Movie 1")

if __name__ == '__main__':
    unittest.main()
