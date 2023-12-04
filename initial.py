from requests_html import HTMLSession
import json
import time

# Load the INCI names
with open('INCI_names.json', 'r') as f:
    inci_names = json.load(f)

# The base URL for the search
base_url = "https://cosmileeurope.eu/inci/results/?q="

# List to store the URLs
results = []

# Create a Session
session = HTMLSession()

# Get the first INCI name
name = inci_names[0]

# Split the name into words and get the first word
first_word = name.split()[0]
print(first_word)

# Make a GET request to the search URL
response = session.get(base_url + first_word)

# Print the HTML of the response
#print(response.html.html)

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

# Save the list of results to a new JSON file
with open('INCI_results.json', 'w') as f:
    json.dump(results, f)