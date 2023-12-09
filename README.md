# COSMILE Europe Data Scraping Project

## Overview

This project aims to scrape data from the COSMILE Europe website, focusing on nearly 30,000 ingredients. The ultimate deliverable is an Excel file tabulating the data in a specified format. To efficiently gather the necessary INCI names for COSMILE, an additional scraping process is performed using data from [From Nature With Love](https://www.fromnaturewithlove.com/resources/inci.asp).

## Task Description

The client has requested data on ingredients listed on the COSMILE Europe website. These ingredients are only accessible through the search bar, and their total count is approximately 30,000. As of now, the project has successfully extracted 14,848 valid URLs from the COSMILE Europe database. To enhance the dataset further, a new scraping phase is required. This additional scraping will aim to acquire more INCI names, enabling a more comprehensive search on the COSMILE platform.

## Project Structure

The project is organized as follows:

- **`data/`**: Contains data files generated during the scraping process.
  - `inci_names.txt`: TXT file downloaded from [From Nature With Love](https://www.fromnaturewithlove.com/resources/inci.asp).
  - `INCI_names.json`: JSON file with INCI names.
  - `INCI_results.json`: JSON file created after "initial.py" with INCI names and corresponding URLs.
  - `INCI_results_unique.json`: JSON file cleaned version of "INCI_results.json" without any duplicates.

- **`logs/`**: Contains log files.
  - `app.log`: Log file for tracking errors and progress.

- **`notebooks/`**: Contains Jupyter notebooks.
  - `txt_to_json.ipynb`: Jupyter notebook for the ETL process. Converts the downloaded Tab Delimited Text File of INCI names from [From Nature With Love](https://www.fromnaturewithlove.com/resources/inci.asp) to a JSON file (`INCI_names.json`).

- **`output/`**: Contains output files generated during the scraping process.
  - `INCI_info.csv`: Excel file with data for nearly 30,000 ingredients.
  - `INCI_info_adjusted.csv`: Excel file without HTML elements, cleaning done through Excel

- **`scripts/`**: Contains Python scripts.
  - `initial.py`: Script that retrieves initial data by searching COSMILE with INCI names.
  - `extract_export.py`: Script extracting data for each ingredient from COSMILE using URLs from `INCI_results.json`.

- **`.gitignore`**: File to specify files and directories that should be ignored by version control (e.g., `__pycache__`, `*.pyc`, `*.csv`, etc.).

- **`current_index.txt`**: File to keep track of the current index in case of an interruption.

- **`README.md`**: Project documentation.

- **`requirements.txt`**: List of Python packages and versions required for the project.

## Getting Started

To get started with the project, follow these steps:

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/allan-gadelha/cosmile-europe-data-scraping.git
   cd cosmile-europe-data-scraping
   ```

2. **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3. **Run Notebooks and Scripts:**
    - Run `notebooks/txt_to_json.ipynb` for the ETL process to generate INCI_names.json. This converts the downloaded Tab Delimited Text File of INCI names from From Nature With Love to a JSON file.

    - Run `scripts/initial.py` for initial data retrieval, which uses the names from INCI_names.json to construct search URLs (https://cosmileeurope.eu/inci/results/?q=name). Outputs INCI_results.json with dictionaries containing "name" and "url" values.

    - Run `notebooks/txt_to_json.ipynb` a second time after running initial.py. This step further processes the results from initial.py and updates INCI_results.json.

    - Run `scripts/extract_export.py` for data extraction from COSMILE.

4. **Resume from Breakpoints:**
    - In case of an interruption, use the information in `current_index.txt` to resume the process.

## Requeriments

- json
- time
- logging
- requests
- requests-html
- lxml
- pandas
- from requests.exceptions import ConnectionError

## Contact

For any questions or issues, feel free to contact the project owner:

- Email: [Allan Gadelha](mailto:c.allan.gadelha@gmail.com)
- GitHub: [Allan Gadelha](https://github.com/allan-gadelha)
- LinkedIn: [Allan Gadelha](https://www.linkedin.com/in/allan-gadelha-216647279/)