-- Get list of next games for a platform (not started, press_score >= 7)
SELECT g.game_name,
       g.press_score,
       g.average_time_beat,
       g.trailer_url
FROM games g
INNER JOIN status_dictionary sd
    ON g.status = sd.status_dictionary_id
INNER JOIN games_on_platforms gop
    ON gop.reference_game_id = g.game_id
INNER JOIN platform_dictionary pd
    ON pd.platform_dictionary_id = gop.platform_id
WHERE sd.status_name = "Не начата"
  AND g.press_score >= 7
  AND pd.platform_name = ?
GROUP BY g.game_name
ORDER BY g.average_time_beat ASC
LIMIT ? OFFSET ?;
