 Create a database for the project
CREATE DATABASE IF NOT EXISTS film_frame CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE film_frame;

-- Users table (store password hashes only; do not store plain passwords in production)
CREATE TABLE IF NOT EXISTS users (
  id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(200) NOT NULL,
  age INT NOT NULL,
  phonenumber VARCHAR(15),
  email VARCHAR(255) NOT NULL UNIQUE,
  password VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Example: create a dedicated DB user (change the password)
-- CREATE USER 'proj_user'@'localhost' IDENTIFIED BY 'Chither@2006';
-- GRANT SELECT, INSERT, UPDATE, DELETE ON project_db.* TO 'proj_user'@'localhost';
-- FLUSH PRIVILEGES;
--Example insert (demo only). Use a secure hash in your application (bcrypt) instead of SQL hashing.
-- This uses SHA2 as a simple example (not recommended for real password storage):
-- INSERT INTO users (fullname, email, password_hash) VALUES ('Demo User', 'demo@example.com', SHA2('demo-password',256));

-- History table to store user's watched movies
CREATE TABLE IF NOT EXISTS history (
  id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  user_id INT UNSIGNED NOT NULL,
  movie_name VARCHAR(255) NOT NULL,
  viewed_at DATETIME NOT NULL,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
-- End of file