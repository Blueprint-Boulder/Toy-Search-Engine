from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd

#PREPROCESSSING------------------------------------------------------------------------------------------------------------------------------
def split_name_from_scientific_name(full_name):
    parts = full_name.split(" (")
    name = parts[0]
    scientific_name = parts[1].rstrip(")") if len(parts) > 1 else ""
    return name, scientific_name

def remove_pipe_bar(text):
    # Split by pipe, get the first part (before pipe) and strip any leading/trailing whitespace
    return text.split("|")[0].strip()

#--------------------------------------------------------------------------------------------------------------------------------------------
def get_family_subfamily_joint():
    driver = webdriver.Chrome()
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

    print("Families:")
    print(families_df)
    print("\nSubfamilies:")
    print(subfamilies_df)
    print("\nFamily to Subfamily Mapping:")
    print(mapping_df)

    return subfamilies_df

    

#this will aquire all the base information for the butterfly and create a subfamily to buttefly data frame
def get_base_butterfly(subfamilies_df):
    # Initialize a new Chrome WebDriver instance
    driver = webdriver.Chrome()

    # Go to the target URL
    url = "http://coloradofrontrangebutterflies.com/butterfly-families/"
    driver.get(url)

    butterfly_names = []
    subfamily_ids = []

    # Iterate over the range for all the subfamilies (from 2 to 18 inclusive)
    for i in range(2, 19):
        try:
            # Find the container that includes the butterfly information
            container = driver.find_element(By.CLASS_NAME, f"et_pb_section_{i}et_section_regular")

            # Extract butterflies
            inner_texts = container.find_elements(By.CLASS_NAME, "et_pb_text_inner")
            for inner_text in inner_texts:
                name = remove_pipe_bar(inner_text.text)
                butterfly_names.append(name)
                
                # Get the subfamily ID based on index (i-2 because range starts from 2)
                subfamily_id = subfamilies_df.iloc[i-2]['Subfamily ID']
                subfamily_ids.append(subfamily_id)

        except Exception as e:
            print(f"Error while processing subfamily index {i}: {e}")
    
    driver.quit()

    # Create DataFrame for the base butterfly information
    butterflies_df = pd.DataFrame({
        'Butterfly Name': butterfly_names,
        'Subfamily ID': subfamily_ids
    })

    # Create the many-to-many joint table
    joint_df = butterflies_df[['Subfamily ID', 'Butterfly Name']]

    return butterflies_df, joint_df







subfamilies_df = get_family_subfamily_joint()
butterflies_df, joint_df = get_base_butterfly(subfamilies_df)
print("Butterflies Data:")
print(butterflies_df)

print("\nJoint Table Data:")
print(joint_df)
