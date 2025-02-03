import requests
from bs4 import BeautifulSoup
import pandas as pd

# URL of the webpage to scrape
url = 'https://www.wordunscrambler.net/word-list/wordle-word-list'

# Send a GET request to the webpage
response = requests.get(url)
response.raise_for_status()  # Ensure the request was successful

# Parse the webpage content
soup = BeautifulSoup(response.text, 'html.parser')

# Find all sections that start with "Wordle Words List Starting With"
sections = soup.find_all('h3', string=lambda text: text and text.startswith('Wordle Words List Starting With'))

# Initialize a list to store the words
wordle_words = []

# Iterate through each section
for section in sections:
    # The next sibling tag after <h3> is the <ul> containing the words
    ul_tag = section.find_next_sibling('ul')
    if ul_tag:
        # Find all <li> tags within the <ul>
        li_tags = ul_tag.find_all('li')
        # Extract and store the word from each <li> tag
        for li in li_tags:
            word = li.get_text(strip=True)
            wordle_words.append(word)

df = pd.DataFrame({'wordle_words': wordle_words})
df.to_csv("wordle_words.csv", index=False)