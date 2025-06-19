-- Author(s):
--    Antonio Rosado
--    Kashan Khan
--    Imad Khan
--    Alexander Schifferle
--    Mike Kheang
-- Assignment:
--    Senior Project (Summer 2025) – init_trades.sql”
-- Last Update:
--    Revised June 18, 2025
-- Purpose:
--    Define the `trades` table to store congressional trade disclosures,
--    linking each trade to a representative and capturing key details.

-- Create the `trades` table
CREATE TABLE trades (
    trade_id INT AUTO_INCREMENT PRIMARY KEY,                    -- Unique identifier for each trade record
    rep_id INT,                                                 -- Foreign key linking to `representatives.rep_id`
    asset_name VARCHAR(255),                                    -- Name of the traded asset (e.g., stock, bond)
    owner VARCHAR(100),                                         -- Owner of the asset (e.g., spouse, dependent)
    transaction_type VARCHAR(100),                              -- Nature of transaction (e.g., “Purchase”, “Sale”)
    notification_date DATE,                                     -- Date the transaction was officially reported
    amount_range VARCHAR(100),                                  -- Estimated value bracket of the trade (e.g., “$1,001–$15,000”)
    year INT,                                                   -- Calendar year in which the trade occurred
    FOREIGN KEY (rep_id) REFERENCES representatives(rep_id)     -- Enforce referential integrity
);
