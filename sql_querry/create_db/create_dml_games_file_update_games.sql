UPDATE {table_names} 
SET game_name = "{row0}",
    status = '{row2}',
    release_date = '{row3}',
    press_score = '{row4}',
    user_score = '{row5}',
    my_score = '{row6}',
    metacritic_url = '{row7}',
    trailer_url = '{row9}',
    my_time_beat = '{row10}',
    average_time_beat = '{row8}'
WHERE game_id = '{game_from_db}';