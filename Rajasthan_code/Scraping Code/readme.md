# Rajasthan Map Data Scraper

This project scrapes district, tehsil, and village data from the Rajasthan government website using Selenium.

## Introduction

The Rajasthan Map Data Scraper is a Python script that automates the extraction of geographical data from the Rajasthan government website (https://apnakhata.rajasthan.gov.in). It navigates through districts, tehsils, and villages, collecting data and storing it in a structured JSON format.

## Installation

### Prerequisites

- Python 3.6 or higher
- WebDriver for Selenium (e.g., ChromiumEdge)

### Setup Instructions

1. Install requirement.txt.
2. Create  MapScraper Object and call scrape_main function - It'll create a log name Scrapping_RJ.log in your file path.
3. After Completing the above function pls check is there any eror log genrated or not if generated check nodeProblem list -- if list have data run step 2 again.
4. After Completing aove process create json call processRoot function vy passing rootNode and json file name / pathEx -  processRoot(scrapRoot.rootNode, scrapRoot.checkpoint_file).
5. Lastly make dataframe rom above genarated json to convert it excel for that run jsonToDf fuction by passing above created json file path.

