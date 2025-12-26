-- Count completed games for a given platform
SELECT COUNT(*) as count
FROM games g
INNER JOIN status_dictionary sd
    ON g.status = sd.status_dictionary_id
INNER JOIN games_on_platforms gop
    ON gop.reference_game_id = g.game_id
INNER JOIN platform_dictionary pd
    ON pd.platform_dictionary_id = gop.platform_id
WHERE sd.status_name = "Completed"
  AND pd.platform_name = ?;
