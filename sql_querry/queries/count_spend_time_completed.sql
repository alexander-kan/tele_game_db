-- Count time spent for completed games on a platform
SELECT SUM(g.average_time_beat) as sum,
       SUM(g.my_time_beat)      as my_sum
FROM games g
INNER JOIN status_dictionary sd
    ON g.status = sd.status_dictionary_id
INNER JOIN games_on_platforms gop
    ON gop.reference_game_id = g.game_id
INNER JOIN platform_dictionary pd
    ON pd.platform_dictionary_id = gop.platform_id
WHERE pd.platform_name = ?
  AND sd.status_name = "Пройдена";
