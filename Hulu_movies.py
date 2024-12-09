from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time
import traceback

# Set up WebDriver (Firefox)
driver = webdriver.Firefox()
url = "https://www.rottentomatoes.com/browse/movies_at_home/affiliates:hulu"
driver.get(url)

movies = []
max_movies = 500

try:
    wait = WebDriverWait(driver, 10)

    while len(movies) < max_movies:
        # Parse the current page
        soup = BeautifulSoup(driver.page_source, "html.parser")
        movie_elements = soup.find_all("div", class_="discovery-tiles__tile")

        for movie in movie_elements:
            if len(movies) >= max_movies:
                break

            try:
                # Extract movie details
                title = movie.find("span", class_="p--small").text.strip() if movie.find("span", class_="p--small") else "N/A"
                scores = movie.find("score-pairs-deprecated")  # Check for the score container
                tomatometer = scores.get("critics-score-wrap", "N/A") if scores else "N/A"
                popcornmeter = scores.get("audience-score-wrap", "N/A") if scores else "N/A"
                streaming_start = movie.find("span", class_="smaller").text.strip() if movie.find("span", class_="smaller") else "N/A"

                # Append movie data
                movies.append({
                    "Title": title,
                    "Tomatometer": tomatometer,
                    "Popcornmeter": popcornmeter,
                    "Streaming Start": streaming_start
                })
            except AttributeError as e:
                print(f"Error extracting data for a movie: {e}. Skipping.")

        # Click "Load More" button
        try:
            load_more_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-qa="dlp-load-more-button"]')))
            driver.execute_script("arguments[0].scrollIntoView(true);", load_more_button)
            ActionChains(driver).move_to_element(load_more_button).click(load_more_button).perform()
            time.sleep(2)  # Add a short delay to allow the next page to load
        except Exception as e:
            print("No more 'Load More' button or an error occurred:", e)
            break

    # Create DataFrame and clean data
    df = pd.DataFrame(movies)
    df.drop_duplicates(subset="Title", keep="first", inplace=True)
    df["Tomatometer"] = pd.to_numeric(df["Tomatometer"], errors="coerce")
    df["Popcornmeter"] = pd.to_numeric(df["Popcornmeter"], errors="coerce")
    df["Streaming Start"] = pd.to_datetime(df["Streaming Start"], format="%b %d, %Y", errors="coerce")
    print(df)

    # Handle missing data
    df["Tomatometer"].fillna(df["Tomatometer"].mean(), inplace=True)
    df["Popcornmeter"].fillna(df["Popcornmeter"].mean(), inplace=True)
    df["Streaming Start"].fillna(method="ffill", inplace=True)

    # Save to CSV
    df.to_csv("Hulu_movies.csv", index=False)
    print(f"Movies saved to 'Hulu_movies.csv' with {len(df)} movies.")

except Exception as e:
    print(f"An error occurred: {e}")
    traceback.print_exc()

finally:
    driver.quit()
