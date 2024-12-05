import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# Base URL for Prime Video movies
BASE_URL = "https://www.rottentomatoes.com/browse/tv-list-1?minTomato=0&maxTomato=100&services=prime_video"

# Initialize empty list for movie data
movies = []


# Function to scrape a single page
def scrape_page(page_number):
    try:
        url = f"{BASE_URL}&page={page_number}"
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes
        soup = BeautifulSoup(response.content, "html.parser")

        # Find movie elements
        movie_elements = soup.find_all("div", class_="movie_element_class")  # Adjust class name based on HTML structure
        for movie in movie_elements:
            title = movie.find("h3", class_="title_class").text.strip()  # Adjust class name
            tomatometer = movie.find("span", class_="tomatometer_class").text.strip()  # Adjust class name
            popcornmeter = movie.find("span", class_="popcornmeter_class").text.strip()  # Adjust class name
            streaming_date = movie.find("div", class_="streaming_date_class").text.strip()  # Adjust class name

            # Append data to list
            movies.append({
                "Title": title,
                "Tomatometer": tomatometer,
                "Popcornmeter": popcornmeter,
                "Streaming Start": streaming_date
            })
    except Exception as e:
        print(f"Error scraping page {page_number}: {e}")


# Loop through pages (adjust range for number of pages)
for page in range(1, 51):  # Assuming 50 pages for 500 movies
    print(f"Scraping page {page}...")
    scrape_page(page)
    time.sleep(2)  # Add delay to avoid server overload

# Create a DataFrame and clean data
df = pd.DataFrame(movies)

# Clean and preprocess data
df.drop_duplicates(inplace=True)
df["Tomatometer"] = pd.to_numeric(df["Tomatometer"].str.replace("%", ""), errors="coerce")
df["Popcornmeter"] = pd.to_numeric(df["Popcornmeter"].str.replace("%", ""), errors="coerce")
df["Streaming Start"] = pd.to_datetime(df["Streaming Start"], errors="coerce")

# Handle missing data (e.g., drop rows or impute values)
df.dropna(inplace=True)

# Save to CSV
df.to_csv("prime_video_movies.csv", index=False)
print("Data saved to prime_video_movies.csv")


