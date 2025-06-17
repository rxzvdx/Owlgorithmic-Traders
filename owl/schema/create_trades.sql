CREATE TABLE trades (
    trade_id INT AUTO_INCREMENT PRIMARY KEY,
    rep_id INT,
    asset_name VARCHAR(255),
    owner VARCHAR(100),
    transaction_type VARCHAR(100),
    notification_date DATE,
    amount_range VARCHAR(100),
    year INT,
    FOREIGN KEY (rep_id) REFERENCES representatives(rep_id)
);
