-- Author(s):
--    Antonio Rosado
--    Kashan Khan
--    Imad Khan
--    Alexander Schifferle
--    Mike Kheang
-- Assignment:
--    Senior Project (Summer 2025) – init_users.sql”
-- Last Update:
--    Revised June 19, 2025
-- Purpose:
--    Define the `users` table to store application users, their profile details, and opt-in preferences for personalized plans.

-- Create the `users` table
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,         -- Unique identifier for each user
    first_name VARCHAR(100),                        -- User's first name
    last_name VARCHAR(100),                         -- User's last name
    email VARCHAR(255) UNIQUE,                      -- User's email address, must be unique
    google_id VARCHAR(255) UNIQUE,                  -- Google OAuth ID, unique per user
    opt_in BOOLEAN DEFAULT FALSE                    -- Flag indicating if the user opted in for personalized plans
);
