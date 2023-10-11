from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv
from sqlalchemy import create_engine
import pandas as pd
import mysql.connector
import os
import re


chrome_options = Options()
chrome_options.add_argument("--headless")

#PREPROCESSSING------------------------------------------------------------------------------------------------------------------------------
def split_name_from_scientific_name(full_name):
    parts = full_name.split(" (")
    name = parts[0]
    scientific_name = parts[1].rstrip(")") if len(parts) > 1 else ""
    return name, scientific_name
#--------------------------------------------------------------------------------------------------------------------------------------------
#SECTION 1 - PROCESS: FAMILY TABLE, SUBFAMILY TABLE, FAMILY_TO_SUBFAMILY
def get_family_subfamily_joint():
    
    driver = webdriver.Chrome(options=chrome_options)
    url = "https://coloradofrontrangebutterflies.com/butterfly-families"
    driver.get(url)

    div = driver.find_element(By.CSS_SELECTOR, '.et_pb_module.et_pb_text.et_pb_text_1.et_pb_bg_layout_light.et_pb_text_align_left')
    elements = div.find_elements(By.XPATH, './/div[@class="et_pb_text_inner"]/*')

    families = []
    subfamilies = []
    family_to_subfamily = []

    family_id = 1
    subfamily_id = 1
    current_family_id = None

    for elem in elements:
        if elem.tag_name == "h2":
            fam_name, sci_fam_name = split_name_from_scientific_name(elem.text)
            families.append({
                'id': family_id,
                'family_name': fam_name,
                'scientific_family_name': sci_fam_name
            })
            current_family_id = family_id
            family_id += 1

        elif elem.tag_name == "p":
            links = elem.find_elements(By.XPATH, './/a')
            for link in links:
                subfam_name, sci_subfam_name = split_name_from_scientific_name(link.text)
                subfamilies.append({
                    'id': subfamily_id,
                    'subfamily_name': subfam_name,
                    'scientific_subfamily_name': sci_subfam_name
                })
                family_to_subfamily.append({
                    'family_id': current_family_id,
                    'subfamily_id': subfamily_id
                })
                subfamily_id += 1

    driver.quit()

    families_df = pd.DataFrame(families)
    subfamilies_df = pd.DataFrame(subfamilies)
    mapping_df = pd.DataFrame(family_to_subfamily)

    return subfamilies_df, mapping_df, families_df
#--------------------------------------------------------------------------------------------------------------------------------------------
#SECTION 2 - PROCESS: BASIC INFORMATION ABOUT BUTTERFLY(NAME, LINK), USE SUBHEADING TO ASSOCIATE BUTTERFLY TO SUBFAMILY 
def get_base_butterfly(subfamilies_df):
    """
    Acquire all the base information for the butterfly and create a subfamily to butterfly data frame.

    Parameters:
    - subfamilies_df (DataFrame): A dataframe containing subfamilies and their associated IDs.

    Returns:
    - butterflies_df (DataFrame): A dataframe containing butterfly names and their links.
    - joint_df (DataFrame): A dataframe linking subfamilies to butterflies.
    """
    
    driver = webdriver.Chrome(options=chrome_options)
    url = "https://coloradofrontrangebutterflies.com/butterfly-families"
    driver.get(url)

    # Retrieve the entire page source
    page_source = driver.page_source

    # Close the Selenium browser
    driver.quit()

    # Parse the page source with BeautifulSoup
    soup = BeautifulSoup(page_source, 'html.parser')

    butterflies_data = []
    joint_data = []

    butterfly_id = 1

    for i in range(2, 19):  # Loop from section 2 to section 18
        section_class = f"et_pb_section et_pb_section_{i} et_section_regular"
        if(i == 3):
            section_class = f"et_pb_section et_pb_section_3 famthumb et_section_regular"
        section = soup.find("div", class_=section_class)

        
        # Extract subfamily name
        subfamily_name = section.find("div", class_="et_pb_text_inner").get_text(strip=True).split('|')[0].split(' Family')[0].strip()
        
        if(subfamily_name == 'Fritillaries'):
            subfamily_name = 'Milkweed Butterflies'

        # Get subfamily_id from the dataframe
        subfamily_id = subfamilies_df[subfamilies_df['subfamily_name'] == subfamily_name]['id'].values[0]

        # Loop over rows in the section
        for row in section.find_all("div", class_="et_pb_row"):
            
            # Loop over columns in the row
            for column in row.find_all("div", class_="et_pb_column"):
                
                # Check if the column has both an image and a text div
                image_div = column.find("div", class_="et_pb_image")
                butterfly_div = column.find("div", class_="et_pb_text")
                
                if image_div and butterfly_div:
                    a_tag = butterfly_div.find("a")
                    if a_tag:
                        butterfly_name = a_tag.get_text(strip=True)
                        butterfly_link = a_tag['href']
                        
                        # Append to butterflies data and joint data
                        butterflies_data.append({
                            'id': butterfly_id,
                            'name': butterfly_name,
                            'link': butterfly_link
                        })
                        # Assuming butterfly_id is the index of this butterfly in butterflies_data
                        butterfly_id = len(butterflies_data)
                        joint_data.append({
                            'id': butterfly_id,
                            'subfamily_id': subfamily_id,
                            'butterfly_id': butterfly_id
                        })
                        butterfly_id+=1

    # Convert to dataframes
    butterflies_df = pd.DataFrame(butterflies_data)
    joint_df = pd.DataFrame(joint_data)

    return butterflies_df, joint_df

subfamilies_df, mapping_df, families_df = get_family_subfamily_joint()
butterflies_df, joint_df = get_base_butterfly(subfamilies_df)

#--------------------------------------------------------------------------------------------------------------------------------------------
#SECTION 3 - EDIT BUTTERFLIES DATA FRAME
def fix_link(butterflies_df,id_num):
    new_link = butterflies_df.loc[id_num,'name']
    new_link = new_link.lower()
    new_link = new_link.replace(" ","-")
    new_link = f"https://coloradofrontrangebutterflies.com/{new_link}"
    butterflies_df.at[id_num, 'link'] = new_link
    return new_link

def get_butterfly_details(butterflies_df):

    butterflies_df['scientific_name'] = ""
    butterflies_df['appearance'] = ""
    butterflies_df['wingspan'] = ""
    butterflies_df['habitat'] = ""
    butterflies_df['flight times'] = ""
    butterflies_df['larval foodplant'] = ""
    butterflies_df['did you know'] = ""

    butterfly_labels = ["Appearance","Wingspan","Habitat","Flight Times","Larval Foodplant","Did You Know"]

    driver = webdriver.Chrome(options=chrome_options)
    id_num = 0

    for url in butterflies_df['link']:

        driver.get(url)
        stupidSoup = BeautifulSoup(driver.page_source,'html.parser')
        science_name = stupidSoup.find('em')

        if(not science_name):

            new_link = fix_link(butterflies_df,id_num)
            driver.get(new_link)
            stupidSoup = BeautifulSoup(driver.page_source,'html.parser')
            science_name = stupidSoup.find('em')
            
        science_name = science_name.get_text()
        science_name = science_name[1:-1]
        butterflies_df.loc[id_num,'scientific_name'] = science_name

        for i in range(0,6):
            pattern = re.compile(f'{butterfly_labels[i]}|Season', re.IGNORECASE)
            #detail = stupidSoup.select_one(f'b:contains("{butterfly_labels[i]}")')
            detail = stupidSoup.find('b',text=pattern)
            test_for_paragraph = detail.find_parent('p')
            if test_for_paragraph:
                detail = detail.find_parent('p')
                text = detail.get_text()
                text = text.replace(detail.find('b').get_text(), '')
            else:
                text = detail.next_sibling.strip()
            
            butterflies_df.loc[id_num,butterfly_labels[i].lower()] = text
            i+=1
        
        id_num+=1

     
    driver.close()
    butterflies_df = butterflies_df.rename(columns={
        'flight times': 'flight_times',
        'larval foodplant': 'larval_foodplant',
        'did you know': 'did_you_know'
    })

    return butterflies_df;  

butterflies_df = get_butterfly_details(butterflies_df)


#DATABSE CREATION---------------------------------------------------------------------------------------------------------------------------
# Load environment variables
load_dotenv()

DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_DATABASE = os.getenv("DB_DATABASE")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

initial_connection = mysql.connector.connect(
    user=DB_USERNAME,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)
cursor = initial_connection.cursor()
cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_DATABASE};")
cursor.close()
initial_connection.close()

# Create MySQL connection
connection = mysql.connector.connect(
    user=os.getenv("DB_USERNAME"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_DATABASE"),
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT")
)

# Define function to create tables
def create_tables():
    cursor = connection.cursor()

    # Drop existing tables first to ensure a fresh start
    cursor.execute("DROP TABLE IF EXISTS Subfamily_to_Butterflies;")
    cursor.execute("DROP TABLE IF EXISTS Family_to_Subfamily;")
    cursor.execute("DROP TABLE IF EXISTS Butterflies;")
    cursor.execute("DROP TABLE IF EXISTS Subfamilies;")
    cursor.execute("DROP TABLE IF EXISTS Families;")

    # Create Families table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Families (
        id INT AUTO_INCREMENT PRIMARY KEY,
        family_name VARCHAR(255),
        scientific_family_name VARCHAR(255)
    );
    """)

    # Create Subfamilies table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Subfamilies (
        id INT AUTO_INCREMENT PRIMARY KEY,
        subfamily_name VARCHAR(255),
        scientific_subfamily_name VARCHAR(255)
    );
    """)

    # Create Family to Subfamily Mapping table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Family_to_Subfamily (
        family_id INT,
        subfamily_id INT,
        FOREIGN KEY (family_id) REFERENCES Families(id),
        FOREIGN KEY (subfamily_id) REFERENCES Subfamilies(id)
    );
    """)

    # Create Butterflies table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Butterflies (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255),
        link VARCHAR(255),
        scientific_name VARCHAR(255),
        appearance TEXT,
        wingspan VARCHAR(255),
        habitat TEXT,
        flight_times TEXT,
        larval_foodplant TEXT,
        did_you_know TEXT
    );
    """)

    # Create Joint table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Subfamily_to_Butterflies (
        id INT AUTO_INCREMENT PRIMARY KEY,
        subfamily_id INT,
        butterfly_id INT,
        FOREIGN KEY (subfamily_id) REFERENCES Subfamilies(id),
        FOREIGN KEY (butterfly_id) REFERENCES Butterflies(id)
    );
    """)

    cursor.close()

create_tables()

# SQLAlchemy engine connection
engine = create_engine(f"mysql+mysqlconnector://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}")

# Write dataframes to SQL
families_df.to_sql(name='Families', con=engine, if_exists='append', index=False)
subfamilies_df.to_sql(name='Subfamilies', con=engine, if_exists='append', index=False)
mapping_df.to_sql(name='Family_to_Subfamily', con=engine, if_exists='append', index=False)
butterflies_df.to_sql(name='Butterflies', con=engine, if_exists='append', index=False)
joint_df.to_sql(name='Subfamily_to_Butterflies', con=engine, if_exists='append', index=False)
print("SUCCESS!")