import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import requests

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import StaleElementReferenceException


#Search Restaurant
def searchRestaurant(restaurant):
    # Open a new tab using JavaScript
    driver.execute_script("window.open('https://www.google.com', '_blank');")

    # Switch to the new tab
    driver.switch_to.window(driver.window_handles[1])  # Index 1 is the new tab

    # Wait for the element to be present and visible
    wait = WebDriverWait(driver, timeout=10)  # 10 seconds timeout
    
    # Search for the restaurant
    searchBar = wait.until(EC.presence_of_element_located((By.NAME, "q")))
    searchBar.clear()  # Clear the field
    searchBar.send_keys(restaurant + Keys.RETURN)  # Enter text and hit Enter

    success = False
    for _ in range(3):  # Retry up to 3 times
        try:
            #Save Restaurant to Maps
            save_button = wait.until(EC.element_to_be_clickable((
                By.XPATH, "//span[@role='button' and .//span[text()='Save']]")))
            save_button.click()
            time.sleep(5)

            done_button = wait.until(EC.element_to_be_clickable((
                By.XPATH, "//button[@jsname='AHldd']")))
            done_button.click()

            print("Clicked Save button.")
            success = True
            time.sleep(5)
            break
        except StaleElementReferenceException:
            print("Stale element, retrying...")
            continue
        except TimeoutException:
            print("Save button not found. Skipping.")
            break

    if not success:
        print(f"Could not save: {restaurant}")


     # Close the new tab after performing the search
    try:
        # Before closing, check that the window still exists
        if len(driver.window_handles) > 1:
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
        else:
            print("Browser window already closed or crashed.")
    except Exception as e:
        print(f"Error closing browser tab: {e}")

#Web Driver 
options = Options()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--start-maximized")
options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36")

driver = webdriver.Chrome(options=options)

# Open the Google Login
driver.get("https://accounts.google.com/")

# Wait for the user to log in manually (or automate login)
input("Log in to the website and press Enter...")

# Get cookies and extract only `name` and `value`
cookies = driver.get_cookies()
simplified_cookies = [{"name": cookie["name"], "value": cookie["value"]} for cookie in cookies]

# Save simplified cookies to a JSON file
with open("cookies.json", "w") as file:
    json.dump(simplified_cookies, file, indent=4)

print("Simplified cookies saved to cookies.json!")

# Load cookies from the JSON file
with open("cookies.json", "r") as file:
    cookies = json.load(file)

# Add cookies to the browser
for cookie in cookies:
    driver.add_cookie(cookie)
    print(cookies)

# Refresh the page to apply the cookies
driver.refresh()

print("Simplified cookies loaded and applied!")

# Open the website (domain must match the cookies)
url = 'https://award.tabelog.com/hyakumeiten/ramen_tokyo'
driver.execute_script(f"window.open('{url}', '_self');")

# 2. Make the GET request to fetch the HTML content
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
response = requests.get(url, headers=headers)

if response.status_code == 200:
    # 4. Parse the HTML content with BeautifulSoup
    data = BeautifulSoup(response.text, 'html.parser')

    # 5. Extract shop names and areas
    names = data.find_all("div", class_="hyakumeiten-shop__name")
    areas = data.find_all("div", class_="hyakumeiten-shop__area")

    # 6. Extract text
    shop_names = [name.text.strip() for name in names]
    shop_areas = [area.text.strip() for area in areas]

    # 7. Optional: Print
    for name, area in zip(shop_names, shop_areas):
        print(f"{name} - {area}")
        searchRestaurant(name)

else:
    print(f"Failed to retrieve page. Status code: {response.status_code}")

input("Press Enter to exit and close the browser...")
