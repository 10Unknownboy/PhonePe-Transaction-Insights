-- =============================================================================
-- PhonePe Pulse — Database Setup
-- Description: Creates the phonepe_pulse database and all 9 required tables.
-- Instructions: Run this script once before using data_extractor.py.
-- =============================================================================

CREATE DATABASE IF NOT EXISTS phonepe_pulse;
USE phonepe_pulse;

-- Aggregated: transaction data by payment type (state + country level)
CREATE TABLE IF NOT EXISTS aggregated_transaction (
    id INT AUTO_INCREMENT PRIMARY KEY,
    state VARCHAR(100),
    year INT,
    quarter INT,
    transaction_type VARCHAR(100),
    transaction_count BIGINT,
    transaction_amount DOUBLE,
    INDEX idx_agg_txn_state_yr_qtr (state, year, quarter)
);

-- Aggregated: user data by device brand
CREATE TABLE IF NOT EXISTS aggregated_user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    state VARCHAR(100),
    year INT,
    quarter INT,
    brand VARCHAR(100),
    user_count BIGINT,
    user_percentage DOUBLE,
    INDEX idx_agg_user_state_yr_qtr (state, year, quarter)
);

-- Aggregated: insurance data by type
CREATE TABLE IF NOT EXISTS aggregated_insurance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    state VARCHAR(100),
    year INT,
    quarter INT,
    insurance_type VARCHAR(100),
    insurance_count BIGINT,
    insurance_amount DOUBLE,
    INDEX idx_agg_ins_state_yr_qtr (state, year, quarter)
);

-- Map: district-level transaction hover data
CREATE TABLE IF NOT EXISTS map_transaction (
    id INT AUTO_INCREMENT PRIMARY KEY,
    state VARCHAR(100),
    year INT,
    quarter INT,
    district VARCHAR(100),
    transaction_count BIGINT,
    transaction_amount DOUBLE,
    INDEX idx_map_txn_state_yr_qtr (state, year, quarter)
);

-- Map: district-level registered users & app opens
CREATE TABLE IF NOT EXISTS map_user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    state VARCHAR(100),
    year INT,
    quarter INT,
    district VARCHAR(100),
    registered_users BIGINT,
    app_opens BIGINT,
    INDEX idx_map_user_state_yr_qtr (state, year, quarter)
);

-- Map: district-level insurance hover data
CREATE TABLE IF NOT EXISTS map_insurance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    state VARCHAR(100),
    year INT,
    quarter INT,
    district VARCHAR(100),
    insurance_count BIGINT,
    insurance_amount DOUBLE,
    INDEX idx_map_ins_state_yr_qtr (state, year, quarter)
);

-- Top: top transactions by state, district, pincode
CREATE TABLE IF NOT EXISTS top_transaction (
    id INT AUTO_INCREMENT PRIMARY KEY,
    state VARCHAR(100),
    year INT,
    quarter INT,
    entity_name VARCHAR(100),
    entity_type VARCHAR(20),
    transaction_count BIGINT,
    transaction_amount DOUBLE,
    INDEX idx_top_txn_type_state_yr_qtr (entity_type, state, year, quarter)
);

-- Top: top users by state, district, pincode
CREATE TABLE IF NOT EXISTS top_user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    state VARCHAR(100),
    year INT,
    quarter INT,
    entity_name VARCHAR(100),
    entity_type VARCHAR(20),
    registered_users BIGINT,
    INDEX idx_top_user_type_state_yr_qtr (entity_type, state, year, quarter)
);

-- Top: top insurance by state, district, pincode
CREATE TABLE IF NOT EXISTS top_insurance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    state VARCHAR(100),
    year INT,
    quarter INT,
    entity_name VARCHAR(100),
    entity_type VARCHAR(20),
    insurance_count BIGINT,
    insurance_amount DOUBLE,
    INDEX idx_top_ins_type_state_yr_qtr (entity_type, state, year, quarter)
);

-- Truncate all tables (run before re-loading data to avoid duplicates)
TRUNCATE TABLE aggregated_transaction;
TRUNCATE TABLE aggregated_user;
TRUNCATE TABLE aggregated_insurance;
TRUNCATE TABLE map_transaction;
TRUNCATE TABLE map_user;
TRUNCATE TABLE map_insurance;
TRUNCATE TABLE top_transaction;
TRUNCATE TABLE top_user;
TRUNCATE TABLE top_insurance;


