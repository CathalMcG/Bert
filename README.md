<h1>Bert</h1>
The movie list bot.

## Introduction

Bert is a discord bot who helps to manage a list of movies you want to watch.

## Commands

Note: In all cases where a movie name is expected, it may be omitted and Bert will use the most recently mentioned movie name.
eg:
`!imdb The Muppets Treasure Island`
`-> https://www.imdb.com/title/tt0117110/`
`!add`
`-> Added The Muppets Treasure Island to the list.`


`!bert` Say hello.

`!add Muppet Treasure Island` Adds the movie Muppet Treasure Island to the list. You can use a partial title if you like, eg `Muppets`. Bert will search imdb for the movie you mean, but it will still appear on the list as
the name you typed.

`!nope` If Bert picks the wrong movie from imdb you can use this command to correct him.

`!remove Muppet Treasure Island` Removes Muppet Treasure Island from the list. Note you have the name exactly as it appears on the list.

`!removie Muppet Treasure Island` Alias for `!remove`.

`!list` List all the movies on the list.

`!list 90` List all the movies with a runtime < 90 minutes.

`!search Muppet` Search the list for movies which include "muppet" in the title (case-insensitive)

`!pick` Pick a random movie from the list.

`!pick 90` Pick a random movie from the list with runtime < 90 minutes

`!imdb Muppet` Search imdb for the word "muppet" and post a link to the first result.
  
`!runtime Muppet Christmas Carol` Searhc imdb for "Muppet Christmas Carol" and post the runtime of the first result.


## Build Process

1. Create a discord application and bot at `discord.com/developers/applications`.

2. Create a file named `bert_env.sh` by copying `bert_env.sh.example`. This is where we will store your bot's discord key.

3. Set user-only read-write permissions on `bert_env.sh`, eg by executing `chmod 600 bert_env.sh`.

4. Copy your bot's token from the Bots page on the discord developer site into the `BERT_DISCORD_KEY` variable in `bert_env.sh`.

5. Run `./build.sh`
