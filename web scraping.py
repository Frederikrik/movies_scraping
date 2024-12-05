import requests
from bs4 import BeautifulSoup
import pandas as pd

URL = "https://www.dsi.uzh.ch/de/current/events.html"

# GET request to the webpage to get HTML
response = requests.get(URL)
print(response)

# parse HTML content using Beautiful Soup
soup = BeautifulSoup(response.content, "html.parser") # creates a BeautifulSoup object; use .content instead of .text to avoid problems with character encoding

# extract event information
events = []
print("start extracting")
for row in soup.find_all("tr"):  #  we loop through each row
    date = row.find("th").text.strip() if row.find("th") else None
    print(date)
    title_tag = row.find("a")
    print(title_tag)
    title = title_tag.text.strip() if title_tag else None
    url = title_tag["href"] if title_tag and "href" in title_tag.attrs else None # href attribute in HTML stands for Hypertext REFerence. It is used in anchor (<a>) tags to define the URL (link) that the anchor points to.
    location = row.find_all("td")[-1].text.strip() if row.find_all("td") else None #Location is taken from the last <td> in the row.

    if title:  # Include only rows with a valid title!
        events.append({
            "Title": title,
            "Date": date,
            "Location": location,
            "URL": url
        })

# convert to DataFrame
df = pd.DataFrame(events)

# save and display the DataFrame
print(df)
df.to_csv("DSI_events.csv", index=False)