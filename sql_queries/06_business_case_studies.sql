-- =============================================================================
-- Business Case Studies: 5 analysis scenarios with supporting queries
-- =============================================================================

USE phonepe_pulse;

-- CASE 1: Decoding Transaction Dynamics --

-- Transaction count growth over years
SELECT year,
       SUM(transaction_count) AS count,
       ROUND(SUM(transaction_amount), 2) AS amount
FROM aggregated_transaction
WHERE state != 'india'
GROUP BY year
ORDER BY year;

-- Payment category trends (stacked area chart)
SELECT year, transaction_type,
       SUM(transaction_count) AS count
FROM aggregated_transaction
WHERE state != 'india'
GROUP BY year, transaction_type
ORDER BY year;

-- Year-over-year transaction growth %
SELECT a.year,
       a.total AS current_year,
       b.total AS prev_year,
       ROUND(((a.total - b.total) / b.total) * 100, 2) AS growth_pct
FROM (SELECT year, SUM(transaction_count) AS total
      FROM aggregated_transaction WHERE state != 'india' GROUP BY year) a
LEFT JOIN (SELECT year, SUM(transaction_count) AS total
           FROM aggregated_transaction WHERE state != 'india' GROUP BY year) b
  ON a.year = b.year + 1
ORDER BY a.year;


-- CASE 2: Device Dominance & User Engagement --

-- Top 10 device brands (all time)
SELECT brand, SUM(user_count) AS count
FROM aggregated_user
WHERE state != 'india'
GROUP BY brand
ORDER BY count DESC
LIMIT 10;

-- Device brand trend over years
SELECT year, brand, SUM(user_count) AS count
FROM aggregated_user
WHERE state != 'india'
GROUP BY year, brand
ORDER BY year;

-- Dominant device brand by state (top 15)
SELECT state, brand, total_users FROM (
    SELECT state, brand, SUM(user_count) AS total_users,
           ROW_NUMBER() OVER (PARTITION BY state ORDER BY SUM(user_count) DESC) AS rn
    FROM aggregated_user WHERE state != 'india'
    GROUP BY state, brand
) ranked
WHERE rn = 1
ORDER BY total_users DESC
LIMIT 15;


-- CASE 3: Insurance Penetration & Growth --

-- Insurance transactions over quarters
SELECT year, quarter,
       SUM(insurance_count) AS count,
       ROUND(SUM(insurance_amount), 2) AS amount
FROM aggregated_insurance
WHERE state != 'india'
GROUP BY year, quarter
ORDER BY year, quarter;

-- Top 10 states by insurance adoption (all time)
SELECT state, SUM(insurance_count) AS count
FROM aggregated_insurance
WHERE state != 'india'
GROUP BY state
ORDER BY count DESC
LIMIT 10;


-- CASE 4: Market Expansion Analysis --

-- All-time transactions by state (choropleth)
SELECT state,
       SUM(transaction_count) AS count,
       ROUND(SUM(transaction_amount), 2) AS amount
FROM aggregated_transaction
WHERE state != 'india'
GROUP BY state
ORDER BY count DESC;

-- Bottom 10 states (expansion targets)
SELECT state, SUM(transaction_count) AS count
FROM aggregated_transaction
WHERE state != 'india'
GROUP BY state
ORDER BY count ASC
LIMIT 10;


-- CASE 5: User Engagement & Growth Strategy --

-- Engagement ratio by state (app opens / registered users)
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







