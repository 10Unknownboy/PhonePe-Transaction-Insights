-- =============================================================================
-- User Analysis: user map, device brands, brand trends, engagement
-- =============================================================================

USE phonepe_pulse;

-- Registered users & app opens by state (choropleth map)
SELECT district AS state,
       SUM(registered_users) AS users,
       SUM(app_opens) AS opens
FROM map_user
WHERE state = 'india'
  AND year = 2024 AND quarter = 1
GROUP BY district;

-- Top 10 device brands for a given period
SELECT brand, SUM(user_count) AS count
FROM aggregated_user
WHERE state != 'india'
  AND year = 2024 AND quarter = 1
GROUP BY brand
ORDER BY count DESC
LIMIT 10;

-- Device brand trend over years
SELECT year, brand, SUM(user_count) AS count
FROM aggregated_user
WHERE state != 'india'
GROUP BY year, brand
ORDER BY year;

-- Top 10 device brands all-time
SELECT brand, SUM(user_count) AS total_users
FROM aggregated_user
WHERE state != 'india'
GROUP BY brand
ORDER BY total_users DESC
LIMIT 10;

-- Dominant device brand per state (window function)
SELECT state, brand, total_users FROM (
    SELECT state, brand, SUM(user_count) AS total_users,
           ROW_NUMBER() OVER (PARTITION BY state ORDER BY SUM(user_count) DESC) AS rn
    FROM aggregated_user
    WHERE state != 'india'
    GROUP BY state, brand
) ranked
WHERE rn = 1
ORDER BY total_users DESC;

-- User engagement ratio by state (app opens / registered users)
SELECT district AS state,
       SUM(registered_users) AS users,
       SUM(app_opens) AS opens,
       ROUND(SUM(app_opens) / SUM(registered_users), 2) AS engagement_ratio
FROM map_user
WHERE state = 'india'
GROUP BY district
ORDER BY engagement_ratio DESC;

-- Registered user growth over years
SELECT year, SUM(registered_users) AS users
FROM map_user
WHERE state = 'india'
GROUP BY year
ORDER BY year;
