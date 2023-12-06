import time
from requests_html import HTMLSession
from lxml import etree
import json
import requests
import pandas as pd
import logging

# Set up logging
logging.basicConfig(filename='logs/app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Load the URLs
with open('data/INCI_results_unique.json', 'r') as f:
    urls = json.load(f)

# Just in case a error stop the program
# Load the last processed index
with open('current_index.txt', 'r') as f:
    start_index = int(f.read().strip())

# Set the starting index to 0
start_index = 0

# List to store the results
results = []

# Create a Session
session = HTMLSession()


# Making a failproof for KeyboardInterrupt = Ctrl + C, this is done because i've interrupted one time and i got a error when trying to restart the program!
try:
    # For each URL
    for i, url in enumerate(urls[start_index:], start=start_index):
        
        #Testing to see if the code work till the first save breakpoint
        if i > 102:
            break


        # Just in case there's no url, but we already made sure that everyone has
        if url is None:
            continue

        # Record the start time
        start_time = time.time()

        # Make a GET request to specific INCI url
        for _ in range(5): # Retry up to 5 times
            try:
                # Make a GET request to the URL
                response = session.get(url['url'])
                # If the request is successful, break the loop
                break
            except requests.exceptions.ConnectionError as e:
                logging.error(f'Connection error at index {i}: {e}')
                time.sleep(10)  # Wait for 10 seconds before retrying
        else:
            logging.error(f'Failed to get response after 5 retries at index {i}')
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

        if i % 100 == 0:
            # Create a DataFrame from the list of results
            df = pd.DataFrame(results)
            
            # Reorder the columns so that "Name" and "Url" are at the beginning and end
            df = df[['Name'] + [col for col in df.columns if col != 'Name' and col != 'Url'] + ['Url']]

            # Save the DataFrame to a CSV file
            df.to_csv('output/INCI_info.csv', index=False, sep=';')

        # Calculate the processing time
        processing_time = time.time() - start_time  

        # Log the current index and processing time
        logging.info(f'Processed name at index {i} in {processing_time} seconds')

        # Save the current index to a separate file
        with open('current_index.txt', 'w') as f:
            f.write(str(i))

        # Add a delay to avoid making too many requests in a short time
        time.sleep(1)
            

except KeyboardInterrupt:
    # Save the current state before exiting
    # Create a DataFrame from the list of results
    df = pd.DataFrame(results)
    
    # Reorder the columns so that "Name" and "Url" are at the beginning and end
    df = df[['Name'] + [col for col in df.columns if col != 'Name' and col != 'Url'] + ['Url']]

    # Save the DataFrame to a CSV file
    df.to_csv('output/INCI_info.csv', index=False, sep=';')
    
    with open('current_index.txt', 'w') as f:
        f.write(str(i))
    print("Interrupted by user, saved current state.")


# After the loop ends, save the results one last time, made this one because of the "i % 50 == 0" inside the loop
# Create a DataFrame from the list of results
df = pd.DataFrame(results)

# Reorder the columns so that "Name" and "Url" are at the beginning and end
df = df[['Name'] + [col for col in df.columns if col != 'Name' and col != 'Url'] + ['Url']]

# Save the DataFrame to a CSV file
df.to_csv('output/INCI_info.csv', index=False, sep=';')