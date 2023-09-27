import mysql.connector
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_DATABASE = os.getenv("DB_DATABASE")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_DIALECT = os.getenv("DB_DIALECT")  # This variable is not used in the connection, but it's loaded here for completeness.

def create_database():
    # Establish a connection to the MySQL server without specifying the database
    connection = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USERNAME,
        password=DB_PASSWORD,
        port=DB_PORT
    )
    cursor = connection.cursor()

    try:
        # Check if the database exists
        cursor.execute(f"SHOW DATABASES LIKE '{DB_DATABASE}'")
        result = cursor.fetchone()

        if result:
            # If the database exists, drop it
            cursor.execute(f"DROP DATABASE {DB_DATABASE}")
            print(f"Database {DB_DATABASE} existed and was dropped.")

        # Create a new database
        cursor.execute(f"CREATE DATABASE {DB_DATABASE}")
        print(f"Database {DB_DATABASE} created successfully!")

        # Use the new database to create tables
        cursor.execute(f"USE {DB_DATABASE}")

        # Create Families table
        cursor.execute("""
        CREATE TABLE Families (
            family_id INT AUTO_INCREMENT PRIMARY KEY,
            family_name VARCHAR(255) NOT NULL,
            subfamily_name VARCHAR(255)
        );
        """)

        # Create Butterflies table
        cursor.execute("""
        CREATE TABLE Butterflies (
            butterfly_id INT AUTO_INCREMENT PRIMARY KEY,
            family_id INT,
            species_name VARCHAR(255) NOT NULL,
            scientific_name VARCHAR(255) NOT NULL,
            appearance TEXT,
            wingspan VARCHAR(255),
            habitat TEXT,
            flight_times TEXT,
            larval_foodplant TEXT,
            additional_info TEXT,
            FOREIGN KEY (family_id) REFERENCES Families(family_id)
        );
        """)

        print("Tables created successfully!")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    create_database()
