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

def create_tables(connection):
    cursor = connection.cursor()

    # Drop existing tables first to ensure a fresh start
    cursor.execute("DROP TABLE IF EXISTS Butterflies;")
    cursor.execute("DROP TABLE IF EXISTS Families;")

    # Then create tables
    # Create Families table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Families (
        family_id INT AUTO_INCREMENT PRIMARY KEY,
        family_name VARCHAR(255),
        scientific_family_name VARCHAR(255),
        subfamily_name VARCHAR(255)
    );
    """)

    # Create Butterflies table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Butterflies (
        butterfly_id INT AUTO_INCREMENT PRIMARY KEY,
        family_id INT,
        species_name VARCHAR(255),
        scientific_name VARCHAR(255),
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
    cursor.close()


def get_family_id(cursor, family_name, scientific_family_name=None, subfamily_name=None):
    if subfamily_name:
        cursor.execute(
            "SELECT family_id FROM Families WHERE family_name = %s AND scientific_family_name = %s AND subfamily_name = %s", 
            (family_name, scientific_family_name, subfamily_name)
        )
    else:
        cursor.execute(
            "SELECT family_id FROM Families WHERE family_name = %s AND scientific_family_name = %s", 
            (family_name, scientific_family_name)
        )

    result = cursor.fetchone()
    return result[0] if result else None

def insert_butterfly(connection, butterfly_data):
    cursor = connection.cursor()

    #Insert family data
    insertFamily_query = """
    INSERT INTO Families (
        family_name, scientific_family_name, subfamily_name
    )
    VALUES (%s, %s, %s)
    """

     # Extract family names and subfamily name
    family_name = butterfly_data.get('family_name')
    scientific_family_name = butterfly_data.get('scientific_family_name')
    subfamily_name = butterfly_data.get('subfamily_name')

    cursor.execute(insertFamily_query, (
        butterfly_data.get('family_name'),
        butterfly_data.get('scientific_family_name'),
        butterfly_data.get('subfamily_name')
    ))

    connection.commit()
    
    family_id = get_family_id(cursor, family_name, scientific_family_name, subfamily_name)
    if not family_id:
        raise ValueError("The provided family/subfamily does not exist in the Families table.")

    print("Butterfly Family data inserted successfully!")

    # Insert butterfly data
    insert_query = """
    INSERT INTO Butterflies (
        family_id, species_name, scientific_name, appearance, wingspan,
        habitat, flight_times, larval_foodplant, additional_info
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    cursor.execute(insert_query, (
        family_id,
        butterfly_data.get('species_name'),
        butterfly_data.get('scientific_name'),
        butterfly_data.get('appearance'),
        butterfly_data.get('wingspan'),
        butterfly_data.get('habitat'),
        butterfly_data.get('flight_times'),
        butterfly_data.get('larval_foodplant'),
        butterfly_data.get('additional_info')
    ))

    

    connection.commit()
    print("Butterfly data inserted successfully!")
    cursor.close()

if __name__ == "__main__":
    connection = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USERNAME,
        password=DB_PASSWORD,
        port=DB_PORT,
        database=DB_DATABASE,
        charset='utf8mb4'
    )

    create_tables(connection)
    
    # Sample butterfly data for insertion
    butterfly_data = {
        'family_name': 'Parnassians and Swallowtails',
        'scientific_family_name': 'Papilionidae',
        'subfamily_name': 'Parnassians',
        'species_name': 'Rocky Mountain Parnassian',
        'scientific_name': 'Parnassius smintheus',
        'appearance': 'Above, overall white to cream with bold black markings...',
        'wingspan': 'Medium; 1 3/4 to 2 1/2 inches.',
        'habitat': 'Open forests, meadows, and rocky clearings...',
        'flight_times': 'Late May to early September...',
        'larval_foodplant': 'Larval form depends on species of stonecrop (Sedum).',
        'additional_info': 'The eggs are laid in summer...'
    }

    insert_butterfly(connection, butterfly_data)
    connection.close()
