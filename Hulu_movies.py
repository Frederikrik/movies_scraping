from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time
import traceback

# Function to safely extract data from HTML elements
def safe_extract(element, css_class=None, attribute_name=None, attribute_value=None, default="N/A"):
    """Extract text from an HTML element safely."""
    print(f"Attempting to extract with css_class={css_class}, attribute_name={attribute_name}, attribute_value={attribute_value}")
    if css_class:
        found = element.find(class_=css_class)
    elif attribute_name and attribute_value:
        found = element.find(attrs={attribute_name: attribute_value})
    else:
        found = None

    if not found:
        print(f"Extraction failed; returning default={default}")
        return default
    print(f"Extracted text: {found.text.strip()}")
    return found.text.strip()

# Function to extract text from Shadow DOM elements
def get_shadow_element_text(driver, css_selector):
    print(f"Attempting to extract Shadow DOM element with selector: {css_selector}")
    return driver.execute_script("""
        const element = document.querySelector(arguments[0]);
        return element ? element.assignedSlot?.textContent || null : null;
    """, css_selector)

# Set up WebDriver (Firefox with headless mode for efficiency)
options = webdriver.FirefoxOptions()
options.add_argument('--headless')  # Run without opening a browser window
driver = webdriver.Firefox(options=options)
url = "https://www.rottentomatoes.com/browse/movies_at_home/affiliates:hulu"
print(f"Navigating to URL: {url}")
driver.get(url)

movies = []
max_movies = 500

try:
    wait = WebDriverWait(driver, 20)  # Increased timeout to handle slow page loads

    while len(movies) < max_movies:
        print(f"Scraping page with {len(movies)} movies collected so far...")
        # Parse the current page
        soup = BeautifulSoup(driver.page_source, "html.parser")
        movie_elements = soup.find_all("div", class_="flex-container")
        print(f"Found {len(movie_elements)} movie elements on the page.")

        for movie in movie_elements:
            if len(movies) >= max_movies:
                print("Reached maximum movie count.")
                break

            try:
                # Extract movie details
                title = safe_extract(movie, css_class="p--small")
                critics_score = get_shadow_element_text(driver, "div.critics-score-wrap slot[name='criticsScore']") or "N/A"
                audience_score = get_shadow_element_text(driver, "div.audience-score-wrap slot[name='audienceScore']") or "N/A"
                streaming_start = safe_extract(movie, css_class="smaller")

                print(f"Extracted data: Title={title}, Tomatometer={critics_score}, Popcornmeter={audience_score}, Streaming Start={streaming_start}")

                # Append movie data
                movies.append({
                    "Title": title,
                    "Tomatometer": critics_score.replace('%', '').strip(),
                    "Popcornmeter": audience_score.replace('%', '').strip(),
                    "Streaming Start": streaming_start
                })
            except Exception as e:
                print(f"Error extracting data for a movie: {e}. Skipping.")

        # Click "Load More" button if available
        try:
            load_more_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-qa="dlp-load-more-button"]')))
            print("Found 'Load More' button. Clicking...")
            driver.execute_script("arguments[0].scrollIntoView(true);", load_more_button)
            ActionChains(driver).move_to_element(load_more_button).click(load_more_button).perform()
            time.sleep(2)  # Add a short delay to allow the next page to load
        except Exception as e:
            print("No more 'Load More' button or an error occurred:", e)
            break

    # Verify scraped data
    if not movies:
        print("No movies were scraped. Exiting script.")
        driver.quit()
        exit()

    print(f"Sample movie data: {movies[:5]}")  # Debug: Check first 5 entries

    # Create DataFrame and clean data
    print("Creating DataFrame...")
    df = pd.DataFrame(movies)
    print(f"Initial DataFrame shape: {df.shape}")

    df.drop_duplicates(subset="Title", keep="first", inplace=True)
    print(f"DataFrame shape after dropping duplicates: {df.shape}")

    # Handle missing columns before processing
    if "Tomatometer" not in df.columns:
        print("Tomatometer column missing; filling with default values.")
        df["Tomatometer"] = pd.NA
    if "Popcornmeter" not in df.columns:
        print("Popcornmeter column missing; filling with default values.")
        df["Popcornmeter"] = pd.NA

    # Convert numeric fields and handle missing values
    print("Processing numeric fields...")
    df["Tomatometer"] = pd.to_numeric(df["Tomatometer"], errors="coerce")
    df["Popcornmeter"] = pd.to_numeric(df["Popcornmeter"], errors="coerce")
    df["Streaming Start"] = pd.to_datetime(df["Streaming Start"], format="%b %d, %Y", errors="coerce")

    # Replace inplace=True with assignment-based operations
    df["Tomatometer"] = df["Tomatometer"].fillna(df["Tomatometer"].mean())
    df["Popcornmeter"] = df["Popcornmeter"].fillna(df["Popcornmeter"].mean())
    df["Streaming Start"] = df["Streaming Start"].ffill()

    # Save to CSV
    print("Saving data to CSV...")
    df.to_csv("Hulu_movies.csv", index=False)
    print(f"Movies saved to 'Hulu_movies.csv' with {len(df)} movies.")

except Exception as e:
    print(f"An error occurred: {e}")
    traceback.print_exc()

finally:
    driver.quit()
