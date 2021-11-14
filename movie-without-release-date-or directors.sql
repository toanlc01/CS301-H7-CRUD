-- Seleting movies without release dates or director
SELECT * FROM movie WHERE (`release` IS NULL OR director IS NULL) AND title <> "" limit 10;

-- Select data from movie with id
SELECT * FROM movie WHERE id = 1 ;