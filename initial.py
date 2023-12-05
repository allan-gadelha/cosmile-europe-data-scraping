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

# Just in case a error stop the program
# Load the last processed index
with open('current_index.txt', 'r') as f:
    start_index = int(f.read().strip())

# Just in case a error stop the program
# Load the existing results
# except because i've stopped the program with CTRL+C before doing the changes and it didn't saved the file, so now i'm getting this error
# i could've only deleted manually the contents of the file, but i've wanted to handle it with programming!
try:
    with open('INCI_results.json', 'r') as f:
        results = json.load(f)
except json.JSONDecodeError:
    results = []

# Create a Session
session = HTMLSession()

# Base URL
base_url = 'https://cosmileeurope.eu/inci/results/?q='

# Set the starting index to 0
#start_index = 0

# If you want to start from 0
# List to store the results
#results = []

# User-Agent String, trying to bypass the RemoteDisconnected
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

# Making a failproof for KeyboardInterrupt = Ctrl + C, this is done because i've interrupted one time and i got a error when trying to restart the program!
try:
    # For each name
    for i, name in enumerate(names[start_index:], start=start_index):
        # If the index is greater than 20, break the loop
        #if i > 20:
        #    break    
        # In Index 2337 got a error: AttributeError: 'NoneType' object has no attribute 'split'
        if name is None:
            continue

        # Record the start time
        start_time = time.time()


        # Split the name by spaces and use the first part for the URL
        first_word = name.split(' ')[0]


        # Make a GET request to the search URL
        for _ in range(5):  # Retry up to 5 times
            try:
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
            
            # Changing location to outer loop, to prevent opening and saving the file every iteration
            # Save the list of results to a new JSON file
            #with open('INCI_results.json', 'w') as f:
            #    json.dump(results, f)

        # Save the list of results to a new JSON file
        # If i is a multiple of 50, save the results to a file
        if i % 50 == 0:
            with open('INCI_results.json', 'w') as f:
                json.dump(results, f)

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
    with open('INCI_results.json', 'w') as f:
        json.dump(results, f)
    with open('current_index.txt', 'w') as f:
        f.write(str(i))
    print("Interrupted by user, saved current state.")

# After the loop ends, save the results one last time, made this one because of the "i % 50 == 0" inside the loop
with open('INCI_results.json', 'w') as f:
    json.dump(results, f)