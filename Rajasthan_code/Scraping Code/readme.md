# Rajasthan Map Data Scraper

This project scrapes district, tehsil, and village data from the Rajasthan government website using Selenium.

## Introduction

The Rajasthan Map Data Scraper is a Python script that automates the extraction of geographical data from the Rajasthan government website (https://apnakhata.rajasthan.gov.in). It navigates through districts, tehsils, and villages, collecting data and storing it in a structured JSON format.

## Installation

### Prerequisites

- Python 3.6 or higher
- WebDriver for Selenium (e.g., ChromiumEdge)

### Code Structure
- Import necessary libraries.
- Define classes and functions for web scraping.
- Configure logging for better tracking and debugging.
- Implement main scraping logic using Selenium WebDriver.
- Handle exceptions and log errors for troubleshooting.
- Save results or checkpoints if needed.


### Setup Instructions

1. Install requirement.txt.
2. First open scrapingMain.py file - It'll create a log name Scrapping_RJ_dropdownData.log and Scrapping_RJ_mapData.log and two json file dropdownData.json and mapdata.json in your file path.
3. Lastly make dataframe above genarated json to convert it excel for that run jsonToDf fuction by passing above created json file path. This function code pasted bellow -

# Steps to Convert JSON to DataFrame

## Creating the DataFrame from JSON

To convert a JSON file into a Pandas DataFrame, you can use the following function:

```python
import json
import pandas as pd

def jsonToDf(jsonfilepath='checkpoint.json'):
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

```
# Steps to Check if within a district, the district,district_id, village and village_id combinations repeat for two tehsils in that district
1. For that open checkDuplication.ipynb file there are two method 
2. For Method 1 - keep dropdown df as first piority during Combine DataFrames
3. For Method 2 - No need to maintain specific order to combine
## For Better Output Pls Cross Check Both Result Output