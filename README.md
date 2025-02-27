# Assessment Readme

## Requirements
The following _python_ packages are needed to run the script: 

- beautifulsoup4 - HTML parsing for scrapping
- selenium - Automate web interactions via browser simulation
- requests - Handles HTTP requests
- webdriver-manager - Manages browser drivers 

Installed by the following _pip_ command: 
```
pip install beautifulsoup4 selenium requests webdriver-manager
```  
The _Mozilla Firefox_ browser was used in _Selenium_, it is also needed and available to download on the following site: https://www.mozilla.org/es-CL/firefox/ .

## Work Done

The following script connects to an online shop to scrape their products, order them from price ascending and storing them in a csv file with that information and their product link.  
Additionally, the script also picks the 5 cheapest item, and scrapes their individual page information on a folder.

## Running

To run the script, use the following command on a terminal (tested on OSX Macbook)
```
python3 script.py
```  
The script creates a new directory called _product_data_ and stores the previously mentioned top 5 product data including images with a naming convention of: 
- _{Product name}.txt_ for the text information
- _{product name}{X}.jpg_ for images, with X being the image number found (varies by product)  
The script will also create a csv file named _products_by_price.csv_ with all of the products found.

## Results
An example folder with the results will be included in the project.  
The data text on the products may be awkwardly parsed because of the webpage specifications and quirks.  
It is worth noting that sometimes, when the script is run many times, the website may not allow the request to access, leading to errors.
