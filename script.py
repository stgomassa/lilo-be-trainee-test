from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager

from bs4 import BeautifulSoup
import re
import csv
import requests
import os


# Firefox options for Selenium
options = Options()
options.add_argument("--headless") # Remove when not testing
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=options)

url = 'https://prima-coffee.com/brew/coffee'
driver.get(url)

print("Page Title:", driver.title)



try:
    # Wait for pagination page load
    pag_info = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "pagination-info"))
    )

    # Extract total items in store 
    pag_text = pag_info.text.strip()
    match = re.search(r'of (\d+) items', pag_text) 
    if match:
        total_items_str = match.group(1)
    
    # Create the url with a query for all elements
    all_prod_url = url + f"?products.size={total_items_str}"
    print(f"Getting all products from: {all_prod_url}")

    # Load the webpage
    driver.get(all_prod_url)

    # Wait for products to load
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "card-body"))
    )

    # Parse the page with BeautifulSoup
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    # Find all product cards
    products = soup.find_all('article', class_="card")
    items = []

    for product in products:
        # Extract product name
        name_tag = product.find('h4', class_='card-title')
        name = name_tag.text.strip() if name_tag else "N/A"

        # Extract product link
        link_tag = name_tag.find('a') if name_tag else None
        link = link_tag['href'] if link_tag else "N/A"

        # Extract price
        price_tag = product.find('span', class_='price')
        price_text = price_tag.text.strip() if price_tag else ""

        #Regex found to parse price as a number
        price_value = float(re.sub(r"[^\d.]", "", price_text)) if price_text else float("inf")

        items.append({'name': name, 'link': link, 'price': price_text, 'price_value': price_value})

    #Sorting the items by price
    items.sort(key=lambda x: x['price_value'])

    #Create csv file with product table
    csv_filename = "products_by_price.csv"
    with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['Name', 'Link', 'Price'])
        writer.writeheader()
        for item in items:
            writer.writerow({'Name': item['name'], 'Link': item['link'], 'Price': item['price']})

    print(f"Data store sucessfully to {csv_filename}")

    # Print products
    for item in items:
        print(item)

    #Get the 5 cheapest items
    cheapest = [items[0],items[1],items[2],items[3],items[4]]

    os.makedirs("product_data", exist_ok=True)

    #Iterate and scrape 
    for product in cheapest:
        prod_name, prod_link = re.sub(r'[^\w\s-]', '', product['name']), product['link'] #Regex found to get clean filename
        driver.get(prod_link)

        WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "page-content"))
        )

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        #Get the three main fields of data in the DOM
        summary_tag = soup.find('div', class_='View-product')
        summary = summary_tag.text.strip() if summary_tag else "Product not found."

        description_tag = soup.find('article', class_='productView-description')
        description = description_tag.text.strip() if description_tag else "No description available."

        details_tag = soup.find('section', class_='productView-details')
        details = details_tag.text.strip() if details_tag else "No details available."

        # Extract product images
        image_section_a = soup.find('section', class_ = 'productView-images')
        image_section_b = soup.find("div", {"id": "tab-description"})
        image_tags = []
        image_tags.extend(image_section_a.find_all('img'))
        image_tags.extend(image_section_b.find_all('img'))

        # Save product details in a text file
        product_file = os.path.join("product_data", f"{prod_name}.txt")
        with open(product_file, "w", encoding="utf-8") as f:
            f.write(f"Product Name: {product['name']}\n")
            f.write(f"Price: {product['price']}\n")
            f.write(f"Link: {prod_link}\n\n")
            f.write(f"Summary:\n{summary}\n")
            f.write(f"Description:\n{description}\n")
            f.write(f"Details:\n{details}\n")

        # Download and save the product image
        if len(image_tags):
            num = 0
            for image in image_tags:
                image_url = image['src']
                image_data = requests.get(image_url).content
                image_filename = os.path.join("product_data", f"{prod_name}{num}.jpg")
                with open(image_filename, "wb") as img_file:
                    img_file.write(image_data)
                num +=1

        print(f"Saved data for: {product['name']}")

except Exception as e:
    print(f"Error: {e}")

finally:
    driver.quit()  # Close Selenium