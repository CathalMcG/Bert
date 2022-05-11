"""
A discord bot for my discord server
it keeps a movie list
"""
import argparse
import random
import pickle
import discord
from discord.ext import commands
from movieList import MovieList

ml = MovieList()

bot = commands.Bot(command_prefix='!')

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--discord-token", "-t",
        dest="token",
        type=str,
        required=True)

    parsed_args = parser.parse_args()
    return parsed_args

def replace_common_prefix(prefix, movie):
    prefix_length = len(prefix) + 1
    if movie[:prefix_length] == (prefix + " "):
        movie = movie[prefix_length:] + " (" + prefix + ")"
    return movie

def replace_the(movie):
    return replace_common_prefix("The", movie)

def replace_a(movie):
    return replace_common_prefix("A", movie)

def format_movies(movies):
    movies = list(map(replace_a, map(replace_the, movies)))
    movies.sort(key=lambda m: m.lower())
    return "\n".join(movies)

def create_movies_embed(title, movies):
    formatted_movie_list = format_movies(movies)
    embed = discord.Embed(title=title, description=formatted_movie_list)
    return embed

@bot.command(name="add", description="adds a movie to the list. either a movie name or imdb link")
async def add_movie(ctx, *, movie=None):
    try:
        movie_name = ml.add_movie(movie)
        link = ml.get_imdb_link(movie_name)
        await ctx.send(f"Added {movie_name} to the list. (say !nope if that's the wrong one) ({link})")
    except Exception as e:
        await ctx.send(f"Couldn't add {movie}, this happened:{e}")

@bot.command(name="runtime", description="get the runtime of a movie")
async def get_movie_runtime(ctx, *, movie_name=None):
    runtime = ml.get_movie_runtime(movie_name)
    await ctx.send(f"The runtime of {movie_name} is {runtime} minutes")

@bot.command(
    name="list",
    description="tell you what's on the movie list. you can optionally add a maximum runtime"+
    " (eg !listmovies 90 to only list movies below 90 minutes)")
async def list_movies(ctx, runtime=None):
    if runtime is None:
        movies = ml.get_movie_names()
        title = "Movie list:\n"
    else:
        movies = ml.get_movies_below_runtime(int(runtime))
        title = f"Movie list (< {runtime} minutes):\n"

    movie_embed = create_movies_embed(title, movies)
    await ctx.send(embed=movie_embed)

@bot.command(
    name="pick",
    description="pick a random movie from the list. put a number after for maximum runtime in"+
    " minutes (eg !pickmovie 90 to only pick movies below 90 minutes")
async def pick_movie(ctx, runtime=None):
    if runtime is None:
        movie_name = ml.pick_random_movie_name()
    else:
        movie_name = ml.pick_random_movie_below_runtime(int(runtime))
    movie_link = ml.get_imdb_link(movie_name)
    await ctx.send(f"I chose {movie_name}\n{movie_link}")

@bot.command(name="remove", description="remove a movie from the list")
async def remove_movie(ctx, *, movie=None):
    removed_movie = ml.remove_movie_name(movie)
    if removed_movie:
        await ctx.send(f"Removed {removed_movie} from the list")
    else:
        await ctx.send(f"{movie} wasn't on the list")

@bot.command(name="removie", description="removie a move from the list")
async def removie(ctx, *, movie=None):
    removed_movie = ml.remove_movie_name(movie)
    if removed_movie:
        await ctx.send(f"Removied {removed_movie} from the list")
    else:
        await ctx.send(f"{movie} wasn't on the list")

def create_nope_list_embed(movie_query, nope_list):
    def format_line(tup):
        return f"[{tup[0]}]({tup[1]})"
    title = f"Options for \"{movie_query}\""
    l = "\n".join([f"{i}) {line}" for i, line in enumerate(map(format_line, nope_list))])
    desc_base = f"say \"!nope <n>\" to choose another option, eg \"!nope 2\"\n\n"
    desc = desc_base + l
    embed = discord.Embed(title=title, description=desc)
    return embed

@bot.command(name="nope", description="nope a movie that was just added")
async def nope_movie(ctx, *, option=None):
    result = ml.correct_movie(option)
    if isinstance(result, list):
        nope_list_embed = create_nope_list_embed(option, result)
        await ctx.send(embed=nope_list_embed)
    elif isinstance(result, str):
        await ctx.send(result)
    else:
        raise Exception("unknown correct movie result")

@bot.command(name="search", description="search the movie list")
async def search_movies(ctx, *, query):
    found_movies = ml.search_list(query)
    if len(found_movies) > 0:
        title = f"Movies matching \"{query}\""
        movie_embed = create_movies_embed(title, found_movies)
        await ctx.send(embed=movie_embed)
    else:
        message = f"I didn't find any movies matching \"{query}\""
    await ctx.send(message)

@bot.command(name="imdb", description="get imdb link for movie")
async def get_imdb_link(ctx, *, movie_query=None):
    url = ml.get_imdb_link(movie_query)
    await ctx.send(url)

@bot.command(name="bert", description="says hello")
async def say_hello(ctx):
    await ctx.send("hmm")

@bot.event
async def on_ready():
    print(f"Bert connected to discord")
    get_stats()

args = parse_args()
print("connecting to discord")
bot.run(args.token)
