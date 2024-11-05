import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser
import logging
import csv
import sqlite3


logger = logging.getLogger(__name__)
logging.basicConfig(filename='example.log', encoding='utf-8', level=logging.DEBUG)

use_storage = False

def is_allowed_to_scrape(url):
    """
    Checks if scraping the given URL is allowed based on the site's robots.txt file.
    
    Args:
        url (str): The URL to check.
        
    Returns:
        bool: True if scraping is allowed, False otherwise.
    """
    parsed_url = urlparse(url)
    robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
    rp = RobotFileParser()
    rp.set_url(robots_url)
    #print(robots_url)
    try:
        rp.read()
        for entry in rp.entries:
            print(entry)
        return rp.can_fetch("*", url)
    except:
        print(f"Couldn't retrieve or parse robots.txt for {robots_url}. Proceeding with caution.")
        return False  # Default to False if there's an issue with robots.txt

def fetch_content(url, selector):
    """
    Fetches and parses content from the provided URL based on the HTML selector, if allowed by robots.txt.
    
    Args:
        url (str): The URL of the site to parse.
        selector (dict): Dictionary with tag and attributes to find the desired HTML elements.
                         Example: {'tag': 'h1', 'class_': 'entry-title'}
    
    Returns:
        list: A list of text content from the matched elements.
    """
    if not is_allowed_to_scrape(url):
        print(f"Scraping disallowed by robots.txt for {url}. Skipping...")
        return []

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises an error for non-2xx responses
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    elements = soup.find_all(selector['tag'], class_=selector.get('class_'))
    return [element.get_text() for element in elements]

def parse_multiple_sites(sites):
    """
    Parses multiple sites and extracts content based on their individual selectors.
    
    Args:
        sites (list of dict): List of dictionaries where each dictionary contains 'url' and 'selector'.
    
    Returns:
        list: A list of results
    """
    results = []
    for site in sites:
        url = site['url']
        selector = site['selector']
        print(f"Checking permission and parsing content from {url}...")
        content = fetch_content(url, selector)
        result = {
            "url":  url,
            "content": content
        }
        results.append(result)
    
    return results

# Example usage
sites = [
    {'url': 'https://dnes.bg', 'selector': {'tag': 'h1', 'class_': ''}},
    {'url': 'https://amazon.com', 'selector': {'tag': 'h2', 'class_': ''}},
    {'url': 'https://scrapethissite.com/pages', 'selector': {'tag': 'h3', 'class_': 'page-title'}},
    # Add more sites and selectors as needed
]

parsed_data = parse_multiple_sites(sites)
print(parsed_data)
# for url, data in parsed_data.items():
#     print(f"Content from {url}:")
#     for item in data:
#         print(" -", item)
#     print("Done")

# Define CSV file and headers
with open('posts.csv', mode='w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=['url', 'content'])
    writer.writeheader()
    writer.writerows(parsed_data)

if use_storage:
    # Connect to SQLite database (or create one)
    conn = sqlite3.connect('scraped_data.db')

    # Create a cursor object to execute SQL commands
    cursor = conn.cursor()

    # Create a table for storing scraped data
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        date TEXT
    )
    ''')

    # Insert data into the table
    cursor.executemany('INSERT INTO posts (title, date) VALUES (?, ?)', 
                    [('Post 1', '2023-09-01'), ('Post 2', '2023-09-02')])

    # Commit the transaction and close the connection
    conn.commit()
    conn.close()