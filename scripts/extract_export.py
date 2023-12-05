import time
from requests_html import HTMLSession
from lxml import etree
import json
from requests.exceptions import ConnectionError
import pandas as pd

# Load the URLs
with open('data/INCI_results_unique.json', 'r') as f:
    urls = json.load(f)

# List to store the results
results = []

# Create a Session
session = HTMLSession()

# For each URL
for url in urls:
    # Initialize a variable for the number of retries
    retries = 5

    while retries > 0:
        try:
            # Make a GET request to the URL
            response = session.get(url['url'])

            # If the request is successful, break the loop
            break
        except ConnectionError:
            # If the request fails, decrement the number of retries and wait for a few seconds
            retries -= 1
            time.sleep(5)

    # If all retries have failed, continue with the next URL
    if retries == 0:
        continue

    # Parse the HTML response using lxml
    root = etree.HTML(response.content)

    # Find the <h2> and <p> elements using XPath
    h2_elements = root.xpath('//div[@class="inci_db"]/h2')
    p_elements = root.xpath('//div[@class="inci_db"]/p')

    # Initialize a dictionary to store the information
    info = {}

    # For each <h2> and corresponding <p>
    for h2, p in zip(h2_elements, p_elements):
        # Get the text of the <h2> and <p> elements
        h2_text = h2.text
        p_text = p.text

        # Store the text in the dictionary
        info[h2_text] = p_text

    # Add the "Name" and "Url" to the dictionary
    info['Name'] = url['name']
    info['Url'] = url['url']

    # Append the dictionary to the list of results
    results.append(info)

# Create a DataFrame from the list of results
df = pd.DataFrame(results)

# Reorder the columns so that "Name" and "Url" are at the beginning and end
df = df[['Name'] + [col for col in df.columns if col != 'Name' and col != 'Url'] + ['Url']]

# Save the DataFrame to a CSV file
df.to_csv('output/INCI_info.csv', index=False, sep=';')