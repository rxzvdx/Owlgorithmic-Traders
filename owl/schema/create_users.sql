CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    email VARCHAR(255) UNIQUE,
    google_id VARCHAR(255) UNIQUE,
    opt_in BOOLEAN DEFAULT FALSE
);
