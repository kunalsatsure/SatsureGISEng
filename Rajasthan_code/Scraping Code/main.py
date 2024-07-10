from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import logging
import pandas as pd

# Configure logging
logging.basicConfig(filename='Scrapping_RJ.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class Node:
    def __init__(self, name, level = 'Root', parent=None):
        self.name = name
        self.parent = parent
        self.properties = {}
        self.children = {}
        self.completed = False
        self.level = level
        self.remrks = None

    def mark_complete(self):
        self.completed = True

    def add_child(self, child_node):
        self.children[child_node.name] = child_node

    def find_child_by_name(self, name):
        return self.children.get(name, None)
    
    def to_dict(self):
        node_dict = {
            "name": self.name,#.encode().decode('unicode-escape'),
            "level": self.level,
            "properties": self.properties,
            "completed": self.completed,
            "remarks": self.remrks
        }
        if self.children:
            node_dict["children"] = [child_node.to_dict() for child_node in self.children.values()]
        return node_dict
  
    def __str__(self):
        return self.name


#To store all problemetic node
nodeProblem = []

class MapScraper:
    def __init__(self, url = 'https://apnakhata.rajasthan.gov.in/LrcLogin.aspx', waittime = 50, checkpoint_file="checkpoint.json"):
        self.url = url
        self.waittime = waittime
        self.driver = webdriver.ChromiumEdge()  # Initialize WebDriver (Chrome in this case)
        self.wait = WebDriverWait(self.driver, self.waittime)  # WebDriverWait instance
        self.checkpoint_file = checkpoint_file
        self.rootNode = Node("Root")

    def click_area(self, element):
        self.driver.execute_script("arguments[0].click();", element)

    def findDistrict(self):
        try:
            self.driver.get(self.url)
            time.sleep(2)  # Give time for the page to load
            # Find the Map Elements --> areas
            areas = WebDriverWait(self.driver, self.waittime).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, 'map[name="Map"] > area')))
            # Extract titles and accesskeys in a list of tuples
            districts = [(area.get_attribute('title'), area.get_attribute('accesskey')) for area in areas]

            if districts:
                return districts
            else:
                return None
        except Exception as e:
            print(e)

    
    def scrape_main(self):
        try:
            self.driver.get(self.url)
            #find all district info
            districts = self.findDistrict()
            isProblem = False
            if nodeProblem:
                logging.error(f"Error in Some District")
                isProblem = True
                districts = [(i, j) for i, j in districts if i in nodeProblem]

            if districts is not None:
                for district, dist_id in districts:
                    dist_click_item = WebDriverWait(self.driver, self.waittime).until(EC.element_to_be_clickable(((By.CSS_SELECTOR, f"area[accesskey='{dist_id}']"))))
                    self.click_area(dist_click_item)
                    # Create New Node to mark district processing
                    if isProblem:
                        logging.error(f"Error - District {district} processed started -  {districts.index((district, dist_id)) + 1} / {len(districts)}")
                        districtMark = self.rootNode.find_child_by_name(district)
                        districtMark.remarks = None
                    else:
                        #add logging
                        logging.info(f"District {district} processed started -  {districts.index((district, dist_id)) + 1} / {len(districts)}")
                        #create new district node
                        districtMark = Node(district, 'district')
                        districtMark.properties['id'] = dist_id
                        self.rootNode.add_child(districtMark)
                    
                    try:
                        #tehsil level
                        # get tehsil list (name, id)
                        tehsil_list = WebDriverWait(self.driver, self.waittime).until(EC.visibility_of_element_located((By.CSS_SELECTOR,'#ctl00_ContentPlaceHolder1_grdhidetehsil')))
                        tehsils = [(elm.text, elm.get_dom_attribute('id')) for elm in tehsil_list.find_elements(By.CSS_SELECTOR, 'a')]


                        for tehsil, tehsil_id in tehsils:
                            #Create New Node to Mrak Teshil processing
                            teshilMark = districtMark.children.get(tehsil)
                            if teshilMark is not None:
                                logging.error(f"Error - District {district} -> Error Teshil {tehsil} processed started")
                                if teshilMark.completed:
                                    continue
                                else:
                                    teshilMark.remarks = None
                                    
                            else:
                                logging.info(f"District {district} -> Teshil {tehsil} processed started -  {tehsils.index((tehsil, tehsil_id)) + 1} / {len(tehsils)}")
                                teshilMark = Node(tehsil, 'Tehsil', district)
                                teshilMark.properties['id'] = tehsil_id
                                districtMark.add_child(teshilMark)
                            
                            tehsil_click_item = WebDriverWait(self.driver, self.waittime).until(EC.element_to_be_clickable((By.CSS_SELECTOR, f"a[id='{tehsil_id}']")))
                            tehsil_click_item.click()

                            try:
                                #village level 
                                # wait for villages get loaded
                                WebDriverWait(self.driver, self.waittime).until(EC.visibility_of_element_located((By.CSS_SELECTOR,"a[href^='javascript:Setvillage']")))
                                village_elements = self.driver.find_elements(By.CSS_SELECTOR,"a[href^='javascript:Setvillage']")
                                count = 1
                                for vill_elm in village_elements:
                                    logging.info(f"District {district} -> Teshil {tehsil} -> Village {vill_elm.text} processed started -  {count} / {len(village_elements)}")
                                    #Create New Node to Mrak Village processing
                                    villageMark = Node(vill_elm.text, 'Village', teshilMark.name)
                                    villageMark.properties['id'] = vill_elm.get_dom_attribute('href')
                                    teshilMark.add_child(villageMark)
                                    count += 1
                            except Exception as e:
                                logging.error(f"Error occurred during village processing: {e}")
                                teshilMark.remrks = f"Error Occured During Village Process {e}"
                                nodeProblem.append(districtMark.name)
                                continue

                            
                            #mark complete teshil
                            if teshilMark.remrks is None:
                                teshilMark.mark_complete()
                                logging.info(f"District {district} -> Teshil {tehsil} processed successfully.")
                            self.driver.get('https://apnakhata.rajasthan.gov.in/Owner_wise/tehsil.aspx')
                    except Exception as e:
                        logging.error(f"Error occurred during tehsil processing: {e}")
                        districtMark.remrks = f"Error Occured During Teshil Process {e}"
                        nodeProblem.append(districtMark.name)
                        continue
                    if districtMark.remrks is None:
                        #mark complete district
                        districtMark.mark_complete()
                        logging.info(f"District {district} processed successfully.")
                        if isProblem:
                            nodeProblem.pop(nodeProblem.index(districtMark.name))
                    self.driver.get('https://apnakhata.rajasthan.gov.in/LrcLogin.aspx')
                if self.rootNode.remrks is None:
                    #mark complete root
                    self.rootNode.mark_complete() 
        except Exception as e:
            logging.error(f"Error occurred during main scraping process: {e}")
            self.rootNode.remrks = f"Error Occured During District Level Process {e}"
        finally:
            self.driver.quit()
    

#process start for Scraping
scrapRoot = MapScraper()
scrapRoot.scrape_main()
# print('Testing --------------', scrapRoot.nodeProblem)
# while nodeProblem:
#     scrapRoot.scrape_main()


#for creating the json
def processRoot(root, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        # Initialize an empty list to hold JSON objects
        json_list = []
        
        # Iterate over each district in root.children
        for dist in root.children:
            # Convert the district data to dictionary
            district_data = root.children[dist].to_dict()
            
            # Append district_data to json_list
            json_list.append(district_data)
        
        # Write the entire json_list to file as a JSON array
        json.dump(json_list, f, ensure_ascii=False, indent=4)
processRoot(scrapRoot.rootNode, scrapRoot.checkpoint_file)

def jsonToDf(jsonfilepath = 'checkpoint.json'):
    with open(jsonfilepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Flatten JSON and create DataFrame
    df = pd.DataFrame([
        (dist['name'], dist['properties']['id'], tehsil['name'], tehsil['properties']['id'], village['name'], village['properties']['id'])
        for dist in data
        for tehsil in dist['children']
        for village in tehsil['children']
    ], columns=['district', 'district_id', 'tehsil', 'tehsil_id', 'village', 'village_id'])

    return df

data = jsonToDf()