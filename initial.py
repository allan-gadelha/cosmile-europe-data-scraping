import json
import time
import logging
import requests
from requests_html import HTMLSession

# Set up logging
logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Load the names
with open('INCI_names.json', 'r') as f:
    names = json.load(f)

# Load the last processed index
with open('current_index.txt', 'r') as f:
    start_index = int(f.read().strip())

# Load the existing results
with open('INCI_results.json', 'r') as f:
    results = json.load(f)

# Create a Session
session = HTMLSession()

# Base URL
base_url = 'https://cosmileeurope.eu/inci/results/?q='

# Set the starting index to 0
start_index = 0

# List to store the results
results = []

# For each name
for i, name in enumerate(names[start_index:], start=start_index):
    # If the index is greater than 20, break the loop
    #if i > 20:
    #    break    
    
    # Split the name by spaces and use the first part for the URL
    first_word = name.split(' ')[0]

    # Make a GET request to the search URL
    for _ in range(5):  # Retry up to 5 times
        try:
            #User-Agent String, trying to bypass the RemoteDisconnected
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
            response = session.get(base_url + first_word, headers=headers)
            break
        except requests.exceptions.ConnectionError as e:
            logging.error(f'Connection error at index {i}: {e}')
            time.sleep(10)  # Wait for 10 seconds before retrying
    else:
        logging.error(f'Failed to get response after 5 retries at index {i}')
        continue
    
    # Make a GET request to the search URL
    #response = session.get(base_url + first_word)

    # Find all elements that match the CSS selector
    elements = response.html.find('.inci_box_link-link')

    # For each element
    for element in elements:
        # Extract the href and text
        url = element.attrs['href']
        text = element.text

        # Store the href and text in a dictionary
        result = {'name': text, 'url': url}

        # Append the dictionary to the list of results
        results.append(result)

    # Log the current index
    logging.info(f'Processed name at index {i}')

    # Save the current index to a separate file
    with open('current_index.txt', 'w') as f:
        f.write(str(i))

    # Add a delay to avoid making too many requests in a short time
    time.sleep(1)

# Save the list of results to a new JSON file
with open('INCI_results.json', 'w') as f:
    json.dump(results, f)