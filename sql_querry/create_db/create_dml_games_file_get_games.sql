SELECT game_id, game_name, status, release_date, press_score, user_score, my_score, metacritic_url, trailer_url, average_time_beat, my_time_beat
FROM games 
WHERE game_name LIKE "%{row}%";