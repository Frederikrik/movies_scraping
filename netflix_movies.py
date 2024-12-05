from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd
import time
import traceback

# Set up WebDriver (example here Firefox)
driver = webdriver.Firefox()

url = "https://www.rottentomatoes.com/browse/movies_at_home/affiliates:netflix"

try:
    driver.get(url)

    time.sleep(1)

    movies = []
    max_movies = 200  # Max number of movies to scrape
    load_more_selector = 'button[data-qa="dlp-load-more-button"]'  # this is the selector for the "Load More" button on https://www.rottentomatoes.com/browse/movies_at_home/affiliates:netflix

    while len(movies) < max_movies:
        # Scrape current movies
        movie_elements = driver.find_elements(By.CSS_SELECTOR, 'span[data-qa="discovery-media-list-item-title"]')
        for movie_element in movie_elements:
            movie_title = movie_element.text.strip()
            if movie_title and movie_title not in movies:  # to avoid duplicates
                movies.append(movie_title)
                if len(movies) >= max_movies:
                    break

        # clicking "Load More" button
        try:
            load_more_button = driver.find_element(By.CSS_SELECTOR, load_more_selector)
            driver.execute_script("arguments[0].scrollIntoView(true);", load_more_button)
            ActionChains(driver).move_to_element(load_more_button).click(load_more_button).perform()
            time.sleep(1)
        except Exception as e:
            print("No more 'Load More' button or an error occurred:", e)
            break  # Exit loop if the button is not found or fails

    # Save movies
    df = pd.DataFrame(movies, columns=["Title"])
    df.to_csv("netflix_movies.csv", index=False)
    print(f"Movies saved to 'rottentomatoes_netflix_movies.csv' with {len(movies)} movies.")

except Exception as e:
    print(f"An error occurred: {e}")
    traceback.print_exc()

finally:
    time.sleep(5)  # Keep browser open for observation
    driver.quit()
