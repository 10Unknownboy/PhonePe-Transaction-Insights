-- =============================================================================
-- Insurance Analysis: insurance map, trends, top states, growth
-- =============================================================================

USE phonepe_pulse;

-- Insurance transactions by state (choropleth map)
SELECT district AS state,
       SUM(insurance_count) AS count,
       ROUND(SUM(insurance_amount), 2) AS amount
FROM map_insurance
WHERE state = 'india'
  AND year = 2024 AND quarter = 1
GROUP BY district;

-- Insurance yearly trend
SELECT year,
       SUM(insurance_count) AS count,
       ROUND(SUM(insurance_amount), 2) AS amount
FROM aggregated_insurance
WHERE state != 'india'
GROUP BY year
ORDER BY year;

-- Top 10 states by insurance count
SELECT state,
       SUM(insurance_count) AS count,
       ROUND(SUM(insurance_amount), 2) AS amount
FROM aggregated_insurance
WHERE state != 'india'
  AND year = 2024 AND quarter = 1
GROUP BY state
ORDER BY count DESC
LIMIT 10;

-- Insurance transactions over quarters (line chart)
SELECT year, quarter,
       SUM(insurance_count) AS count,
       ROUND(SUM(insurance_amount), 2) AS amount
FROM aggregated_insurance
WHERE state != 'india'
GROUP BY year, quarter
ORDER BY year, quarter;

-- Insurance growth year-over-year (self join)
SELECT a.year,
       a.total AS current_year,
       b.total AS prev_year,
       ROUND(((a.total - b.total) / b.total) * 100, 2) AS growth_pct
FROM (SELECT year, SUM(insurance_count) AS total
      FROM aggregated_insurance WHERE state != 'india' GROUP BY year) a
LEFT JOIN (SELECT year, SUM(insurance_count) AS total
           FROM aggregated_insurance WHERE state != 'india' GROUP BY year) b
  ON a.year = b.year + 1
ORDER BY a.year;

-- Top 10 districts by insurance count
SELECT district,
       SUM(insurance_count) AS total_count,
       ROUND(SUM(insurance_amount), 2) AS total_amount
FROM map_insurance
WHERE state = 'india'
GROUP BY district
ORDER BY total_count DESC
LIMIT 10;