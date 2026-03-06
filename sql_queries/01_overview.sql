-- =============================================================================
-- Overview Section: KPIs, India map, payment category breakdown
-- =============================================================================

USE phonepe_pulse;

-- Total transaction count & amount
SELECT SUM(transaction_count) AS total_txn,
       ROUND(SUM(transaction_amount), 2) AS total_amt
FROM aggregated_transaction
WHERE state != 'india'
  AND year = 2024 AND quarter = 1;

-- Total registered users & app opens (country level)
SELECT SUM(registered_users) AS total_users,
       SUM(app_opens) AS total_opens
FROM map_user
WHERE state = 'india'
  AND year = 2024 AND quarter = 1;

-- Total insurance count & amount
SELECT SUM(insurance_count) AS total_ins,
       ROUND(SUM(insurance_amount), 2) AS total_ins_amt
FROM aggregated_insurance
WHERE state != 'india'
  AND year = 2024 AND quarter = 1;

-- Transaction amount by state (choropleth map)
SELECT district AS state,
       ROUND(SUM(transaction_amount), 2) AS amount,
       SUM(transaction_count) AS count
FROM map_transaction
WHERE state = 'india'
  AND year = 2024 AND quarter = 1
GROUP BY district;

-- Payment category breakdown (pie chart)
SELECT transaction_type,
       SUM(transaction_count) AS count,
       ROUND(SUM(transaction_amount), 2) AS amount
FROM aggregated_transaction
WHERE state != 'india'
  AND year = 2024 AND quarter = 1
GROUP BY transaction_type
ORDER BY count DESC;