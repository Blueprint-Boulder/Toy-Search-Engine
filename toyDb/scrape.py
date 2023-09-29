from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd

def split_name_from_scientific_name(full_name):
    parts = full_name.split(" (")
    name = parts[0]
    scientific_name = parts[1].rstrip(")") if len(parts) > 1 else ""
    return name, scientific_name

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

get_family_subfamily_joint()
