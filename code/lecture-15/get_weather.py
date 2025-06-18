import requests
from bs4 import BeautifulSoup

URL = "https://www.timeanddate.com/weather/india/delhi"
HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def extract_weather_details():
    response = requests.get(URL, headers=HEADERS)
    soup = BeautifulSoup(response.content, "html.parser")

    table = soup.select_one("section.bk-focus table")
    if not table:
        raise ValueError("Weather information table not found.")

    weather_data = {}
    for row in table.find_all("tr"):
        heading = row.find("th").text.strip().rstrip(":")
        value = row.find("td").text.strip()

        if heading == "Location":
            weather_data["Location"] = value
        elif heading == "Dew Point":
            weather_data["Dew Point"] = value
        elif heading == "Humidity":
            weather_data["Humidity"] = value
        elif heading == "Pressure":
            weather_data["Pressure"] = value
        elif heading == "Visibility":
            weather_data["Visibility"] = value

    return weather_data

if __name__ == "__main__":
    data = extract_weather_details()
    for key, val in data.items():
        print(f"{key}: {val}")
