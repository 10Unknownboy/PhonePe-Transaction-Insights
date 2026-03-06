-- =============================================================================
-- Top Charts: top 10 states & districts for transactions, users, insurance
-- =============================================================================

USE phonepe_pulse;

-- TRANSACTIONS --

-- Top 10 states by transaction count
SELECT entity_name,
       SUM(transaction_count) AS count,
       ROUND(SUM(transaction_amount), 2) AS amount
FROM top_transaction
WHERE entity_type = 'state' AND state = 'india'
  AND year = 2024 AND quarter = 1
GROUP BY entity_name
ORDER BY count DESC
LIMIT 10;

-- Top 10 districts by transaction count
SELECT entity_name,
       SUM(transaction_count) AS count,
       ROUND(SUM(transaction_amount), 2) AS amount
FROM top_transaction
WHERE entity_type = 'district' AND state = 'india'
  AND year = 2024 AND quarter = 1
GROUP BY entity_name
ORDER BY count DESC
LIMIT 10;

-- USERS --

-- Top 10 states by registered users
SELECT entity_name, SUM(registered_users) AS users
FROM top_user
WHERE entity_type = 'state' AND state = 'india'
  AND year = 2024 AND quarter = 1
GROUP BY entity_name
ORDER BY users DESC
LIMIT 10;

-- Top 10 districts by registered users
SELECT entity_name, SUM(registered_users) AS users
FROM top_user
WHERE entity_type = 'district' AND state = 'india'
  AND year = 2024 AND quarter = 1
GROUP BY entity_name
ORDER BY users DESC
LIMIT 10;

-- INSURANCE --

-- Top 10 states by insurance count
SELECT entity_name,
       SUM(insurance_count) AS count,
       ROUND(SUM(insurance_amount), 2) AS amount
FROM top_insurance
WHERE entity_type = 'state' AND state = 'india'
  AND year = 2024 AND quarter = 1
GROUP BY entity_name
ORDER BY count DESC
LIMIT 10;

-- Top 10 districts by insurance count
SELECT entity_name,
       SUM(insurance_count) AS count,
       ROUND(SUM(insurance_amount), 2) AS amount
FROM top_insurance
WHERE entity_type = 'district' AND state = 'india'
  AND year = 2024 AND quarter = 1
GROUP BY entity_name
ORDER BY count DESC
LIMIT 10;





