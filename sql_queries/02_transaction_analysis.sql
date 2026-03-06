-- =============================================================================
-- Transaction Analysis: yearly/quarterly trends, payment types, top states
-- =============================================================================

USE phonepe_pulse;

-- Yearly transaction trend
SELECT year,
       SUM(transaction_count) AS count,
       ROUND(SUM(transaction_amount), 2) AS amount
FROM aggregated_transaction
WHERE state != 'india'
GROUP BY year
ORDER BY year;

-- Quarter-wise trend for a specific year
SELECT quarter,
       SUM(transaction_count) AS count,
       ROUND(SUM(transaction_amount), 2) AS amount
FROM aggregated_transaction
WHERE state != 'india' AND year = 2024
GROUP BY quarter
ORDER BY quarter;

-- Payment type trend over years
SELECT year, transaction_type,
       SUM(transaction_count) AS count
FROM aggregated_transaction
WHERE state != 'india'
GROUP BY year, transaction_type
ORDER BY year;

-- Top 10 states by transaction count
SELECT state,
       SUM(transaction_count) AS count,
       ROUND(SUM(transaction_amount), 2) AS amount
FROM aggregated_transaction
WHERE state != 'india'
  AND year = 2024 AND quarter = 1
GROUP BY state
ORDER BY count DESC
LIMIT 10;

-- Average transaction value by payment type
SELECT transaction_type,
       ROUND(SUM(transaction_amount) / SUM(transaction_count), 2) AS avg_value
FROM aggregated_transaction
WHERE state != 'india'
GROUP BY transaction_type
ORDER BY avg_value DESC;

