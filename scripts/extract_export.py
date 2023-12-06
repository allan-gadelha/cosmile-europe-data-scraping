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
        #if i > 52:
        #    break


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

        # Find the <h2>, <h3> and <p> elements using XPath
        #elements = root.xpath('//div[@class="inci_db"]/*[self::h2 or self::h3 or self::p]')

        # Find the <h2>, <h3>, <p> and <div> elements using XPath
        elements = root.xpath('//div[@class="inci_db"]/*[self::h2 or self::h3 or self::p or self::div[@class="inci_box_links"]]')

        # Initialize a dictionary to store the information
        info = {}
        current_h2 = None
        current_h3 = None

        # For each element
        for element in elements:
            # Get the text of the element
            text = element.text

            # If the element is <h2>, store the text as a key
            if element.tag == 'h2':
                current_h2 = text
                current_h3 = None
                info[current_h2] = {}
            # If the element is <h3>, store the text as a nested key under the current <h2>
            elif element.tag == 'h3':
                current_h3 = text
                info[current_h2][current_h3] = []
            # If the element is <p>, append the text to the current key
            elif element.tag == 'p':
                if current_h3 is not None:
                    info[current_h2][current_h3].append(text)
                else:
                    if 'p' not in info[current_h2]:
                        info[current_h2]['p'] = []
                    info[current_h2]['p'].append(text)
            # If the element is <div> with class 'inci_box_links', get the text from all nested <div> with class 'inci_box_link'
            #elif element.tag == 'div' and 'inci_box_links' in element.attrib.get('class', ''):
            #    link_texts = element.xpath('.//div[@class="inci_box_link"]/text()')
            #    info[current_h2]['inci_box_links'] = link_texts
            # If the element is <div> with class 'inci_box_links', get the text from all nested <a> with class 'inci_box_link-link'
            elif element.tag == 'div' and 'inci_box_links' in element.attrib.get('class', ''):
                link_texts = element.xpath('.//div[@class="inci_box_link"]/div[@class="inci_box_link-content"]/a[@class="inci_box_link-link"]/text()')
                info[current_h2]['inci_box_links'] = [text.strip() for text in link_texts if text.strip()]  # remove empty strings and strip leading/trailing whitespaces

        # Convert lists of one item to single values
        for h2, value in info.items():
            if isinstance(value, dict):
                for h3, p_list in value.items():
                    if len(p_list) == 1:
                        info[h2][h3] = p_list[0]
            elif isinstance(value, list) and len(value) == 1:
                info[h2] = value[0]

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