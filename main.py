import requests
from bs4 import BeautifulSoup

url = 'https://example-blog.com'
try:
    response = requests.get(url)
    if response.status_code == 200:
        print("Successfully retrieved the webpage!")
    else:
        print("Failed to retrieve the webpage. Status code:", response.status_code)
except requests.exceptions.ConnectionError:
    print("Connection exception")
except:
    print("General unhandled error")

soup = BeautifulSoup(response.content, 'html.parser')

titles = soup.find_all('h1', class_='entry-title')
for title in titles:
    print(title.get_text())
    
print("Done")
