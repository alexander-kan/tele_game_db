CREATE TABLE IF NOT EXISTS platform_dictionary ( --Platform dictionary table
    platform_dictionary_id integer PRIMARY KEY AUTOINCREMENT, --Platform dictionary record identifier
    platform_name text NOT NULL --Platform name
    );
CREATE TABLE IF NOT EXISTS status_dictionary ( --Game completion status dictionary table
    status_dictionary_id integer PRIMARY KEY AUTOINCREMENT, --Status dictionary record identifier
    status_name text NOT NULL --Status name
    );
CREATE TABLE IF NOT EXISTS games ( --Main games table
    game_id text PRIMARY KEY, --Identifier will be created as GUID
    game_name text NOT NULL, --Game name, official, full
    status integer NOT NULL, --Current game status
    release_date date NOT NULL, --Game release date
    press_score float NOT NULL, --Press score
    user_score float NOT NULL, --User score
    my_score integer, --My score
    metacritic_url text NOT NULL, --Metacritic link
    trailer_url text NOT NULL, --Trailer link
    average_time_beat float NOT NULL, --Average playtime
    my_time_beat float, --My playtime
    last_launch_date date, --Last launch date
    FOREIGN KEY (status) REFERENCES status_dictionary (status_dictionary_id)
    );
CREATE TABLE IF NOT EXISTS games_on_platforms ( --Platforms on which I have the game
    games_on_platform_id integer PRIMARY KEY AUTOINCREMENT, --Game on platform record identifier
    platform_id integer NOT NULL, --Platform name
    reference_game_id text NOT NULL, --Link to game
    FOREIGN KEY (reference_game_id) REFERENCES games (game_id),
    FOREIGN KEY (platform_id) REFERENCES platform_dictionary (platform_dictionary_id)
    );
CREATE TABLE IF NOT EXISTS beat_on_platforms ( --Platforms on which I completed the game and how many times
    beat_on_platform_id integer PRIMARY KEY AUTOINCREMENT, --Platform completion record identifier
    platform_id integer NOT NULL, --Platform name
    game_id text NOT NULL, --Link to game
    number_of_beat integer, --How many times I completed it
    FOREIGN KEY (game_id) REFERENCES games (game_id),
    FOREIGN KEY (platform_id) REFERENCES platform_dictionary (platform_dictionary_id)
    );
