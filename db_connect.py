# db_connect.py
# This file connects to MySQL, executes the SQL file to create the database and table, and provides a function to insert user data.

import mysql.connector  # Import the MySQL connector library
from mysql.connector import Error  # For handling errors
from db_config import get_db_config  # Import database config from db_config.py

# Function to connect to MySQL and execute the SQL file to create/setup the database
def create_database_and_table():
    try:
        # Get config without database (for creating DB)
        config = get_db_config()
        config_no_db = {k: v for k, v in config.items() if k != 'database'}

        # Step 1: Connect to MySQL server (without specifying a database)
        connection = mysql.connector.connect(**config_no_db)

        if connection.is_connected():
            print("Connected to MySQL server successfully!")

            # Create a cursor to execute SQL commands
            cursor = connection.cursor()

            # Step 2: Read and execute the SQL file
            with open('create_db.sql', 'r') as sql_file:
                sql_script = sql_file.read()

            # Split the script into individual statements (by semicolon)
            sql_statements = sql_script.split(';')

            for statement in sql_statements:
                statement = statement.strip()
                if statement:  # Skip empty statements
                    cursor.execute(statement)

            print("SQL file executed successfully! Database and table created.")

            # Commit the changes
            connection.commit()

    except Error as e:
        print(f"Error: {e}")
    finally:
        # Close the cursor and connection
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals() and connection.is_connected():
            connection.close()
            print("MySQL connection closed.")

# Function to insert user data into the 'users' table
def insert_user(name, age, phonenumber, email, password):
    try:
        # Connect to the specific database
        connection = mysql.connector.connect(**get_db_config())

        if connection.is_connected():
            print("Connected to database for insertion.")

            cursor = connection.cursor()

            # SQL query to insert user data (parameterized to prevent SQL injection)
            insert_query = """
            INSERT INTO users (name, age, phonenumber, email, password)
            VALUES (%s, %s, %s, %s, %s)
            """

            # Values to insert (as a tuple)
            user_data = (name, age, phonenumber, email, password)

            # Execute the query with parameters
            cursor.execute(insert_query, user_data)

            # Commit the transaction
            connection.commit()

            print(f"Data insertion success: User '{name}' registered successfully!")

    except Error as e:
        print(f"Error inserting user: {e}")
        raise  # Re-raise the exception so Flask can handle it
    finally:
        # Close the cursor and connection
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals() and connection.is_connected():
            connection.close()
            print("MySQL connection closed after insertion.")

# Function to execute the SQL file to set up the database and tables
def execute_sql_file(sql_file_path):
    try:
        connection = mysql.connector.connect(**get_db_config())
        if connection.is_connected():
            print("Connected to MySQL server successfully!")
            cursor = connection.cursor()

            # Read and execute the SQL file
            with open(sql_file_path, 'r') as sql_file:
                sql_script = sql_file.read()

            for statement in sql_script.split(';'):
                if statement.strip():
                    cursor.execute(statement)

            connection.commit()
            print("SQL file executed successfully!")
    except Error as e:
        print(f"Error executing SQL file: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals() and connection.is_connected():
            connection.close()
            print("MySQL connection closed.")

# Function to connect to MySQL and insert data into the `users` table
def insert_into_users(name, age, phonenumber, email, password):
    try:
        connection = mysql.connector.connect(**get_db_config())
        if connection.is_connected():
            print("Connected to MySQL server successfully!")
            cursor = connection.cursor()

            # Insert query for the `users` table
            insert_query = """
            INSERT INTO users (name, age, phonenumber, email, password)
            VALUES (%s, %s, %s, %s, %s)
            """

            # Execute the query with the provided data
            cursor.execute(insert_query, (name, age, phonenumber, email, password))

            # Commit the transaction
            connection.commit()
            print("Data inserted successfully into the `users` table.")
    except Error as e:
        print(f"Error inserting data into MySQL: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals() and connection.is_connected():
            connection.close()
            print("MySQL connection closed.")

# Function to create the registration table if it does not exist
def create_registration_table():
    try:
        connection = mysql.connector.connect(**get_db_config())
        if connection.is_connected():
            print("Connected to MySQL server successfully!")
            cursor = connection.cursor()

            # Create the registration table if it does not exist
            create_table_query = """
            CREATE TABLE IF NOT EXISTS registration (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                phonenumber VARCHAR(15),
                age INT
            )
            """
            cursor.execute(create_table_query)
            connection.commit()
            print("Registration table created or already exists.")
    except Error as e:
        print(f"Error creating registration table: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals() and connection.is_connected():
            connection.close()
            print("MySQL connection closed.")

# Example usage (uncomment to test)
# if __name__ == "__main__":
#     create_database_and_table()  # Create DB and table
#     insert_user("John Doe", 25, "1234567890", "john@example.com", "hashed_password_here")  # Insert a user
#     execute_sql_file("Mysql local.session.sql")  # Execute session SQL file
#     insert_into_users("John Doe", 30, "1234567890", "john.doe@example.com", "securepassword")  # Insert into users
#     create_registration_table()  # Create registration table

# Example usage
if __name__ == "__main__":
    execute_sql_file("Mysql local.session.sql")