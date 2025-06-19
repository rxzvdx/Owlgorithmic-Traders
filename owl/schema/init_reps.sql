-- Author(s):
--    Antonio Rosado
--    Kashan Khan
--    Imad Khan
--    Alexander Schifferle
--    Mike Kheang
-- Assignment:
--    Senior Project (Summer 2025) – “init_reps.sql”
-- Last Update:
--    Revised June 18th 2025
-- Purpose:
--    Define the `representatives` table to store each member’s ID, name, state, and district.

-- Create the `representatives` table
CREATE TABLE representatives (
    rep_id INT AUTO_INCREMENT PRIMARY KEY,  -- Unique identifier for each representative
    name VARCHAR(255) NOT NULL,             -- Full name of the representative (required)
    state VARCHAR(100),                     -- U.S. state the representative serves
    district VARCHAR(50)                    -- Congressional district (e.g., “CA-12” or “At-Large”)
);
