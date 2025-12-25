-- Query game information by name (supports LIKE pattern matching)
SELECT g.game_name,
       sd.status_name,
       GROUP_CONCAT(pd.platform_name),
       g.press_score,
       g.average_time_beat,
       g.user_score,
       g.my_score,
       g.metacritic_url,
       g.trailer_url,
       g.my_time_beat,
       g.last_launch_date
FROM games g
INNER JOIN status_dictionary sd
    ON g.status = sd.status_dictionary_id
INNER JOIN games_on_platforms gop
    ON gop.reference_game_id = g.game_id
INNER JOIN platform_dictionary pd
    ON pd.platform_dictionary_id = gop.platform_id
WHERE g.game_name LIKE ?
GROUP BY g.game_name
ORDER BY g.average_time_beat ASC;
